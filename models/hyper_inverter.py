import argparse
import copy
import math
import pickle
import time
import dlib
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from configs import paths_config
from configs.paths_config import model_paths
from models.encoders import fpn_encoders
from models.hypernetwork import Hypernetwork
from models.stylegan2_ada import Discriminator, Generator
from models.weight_shapes import (
    STYLEGAN2_ADA_ALL_WEIGHT_WITHOUT_BIAS_SHAPES,
    STYLEGAN2_ADA_CONV_WEIGHT_WITHOUT_BIAS_SHAPES,
    STYLEGAN2_ADA_CONV_WEIGHT_WITHOUT_BIAS_WITHOUT_TO_RGB_SHAPES,
)
from utils import common
from utils.model_utils import RESNET_MAPPING
from custom_python import online_learner
# from custom_python import custom_onlinr_learner
from models.helpers import get_landmark

def get_target_shapes(opts):
    if opts.target_shape_name == "conv_without_bias":
        general_shape = STYLEGAN2_ADA_CONV_WEIGHT_WITHOUT_BIAS_SHAPES
    elif opts.target_shape_name == "all_without_bias":
        general_shape = STYLEGAN2_ADA_ALL_WEIGHT_WITHOUT_BIAS_SHAPES
    elif opts.target_shape_name == "conv_without_bias_without_torgb":
        general_shape = STYLEGAN2_ADA_CONV_WEIGHT_WITHOUT_BIAS_WITHOUT_TO_RGB_SHAPES

    target_shape = {}
    for layer_name in general_shape:
        cur_resolution = int(layer_name.split(".")[0][1:])
        if cur_resolution <= opts.output_size:
            target_shape[layer_name] = general_shape[layer_name]

    return target_shape


class HyperInverter(nn.Module):
    def __init__(self, opts):
        super().__init__()

        # Configurations
        self.set_opts(opts)

        # compute number of style inputs based on the output resolution
        self.opts.n_styles = int(math.log(self.opts.output_size, 2)) * 2 - 2

        # Hypernetwork
        self.target_shape = get_target_shapes(self.opts)
        self.hypernet = Hypernetwork(
            input_dim=512,
            hidden_dim=self.opts.hidden_dim,
            target_shape=self.target_shape,
        )

        # Define and load architecture
        self.load_weights()

        # For visualization
        self.face_pool = torch.nn.AdaptiveAvgPool2d((256, 256))

    def load_weights(self):
        # Load W-Encoder (E1 Encoder in Paper)
        if self.opts.w_encoder_path is not None:
            w_encoder_path = self.opts.w_encoder_path
        elif self.opts.dataset_type == "ffhq_encode" and model_paths["w_encoder_ffhq"] is not None:
            w_encoder_path = model_paths["w_encoder_ffhq"]
        elif self.opts.dataset_type == "church_encode" and model_paths["w_encoder_church"] is not None:
            w_encoder_path = model_paths["w_encoder_church"]
        else:
            raise Exception("Please specify the path to the pretrained W encoder.")

        print(f"Loaded pretrained W encoder from: {w_encoder_path}")

        ckpt = torch.load(w_encoder_path, map_location="cpu")

        opts = ckpt["opts"]
        opts = argparse.Namespace(**opts)

        if "ffhq" in self.opts.dataset_type or "celeb" in self.opts.dataset_type or "video" in self.opts.dataset_type:
            # Using ResNet-IRSE50 for facial domain
            self.w_encoder = fpn_encoders.BackboneEncoderUsingLastLayerIntoW(50, "ir_se", opts)
        else:
            # Using ResNet34 pre-trained on ImageNet for other domains
            self.w_encoder = fpn_encoders.ResNetEncoderUsingLastLayerIntoW()

        self.w_encoder.load_state_dict(common.get_keys(ckpt, "encoder"), strict=True)
        self.w_encoder.to(self.opts.device).eval()
        common.toogle_grad(self.w_encoder, False)

        # Load pretrained StyleGAN2-ADA models
        if self.opts.dataset_type == "ffhq_encode" or self.opts.dataset_type == "video_encode":
            stylegan_ckpt_path = model_paths["stylegan2_ada_ffhq"]
        elif self.opts.dataset_type == "church_encode":
            stylegan_ckpt_path = model_paths["stylegan2_ada_church"]

        with open(stylegan_ckpt_path, "rb") as f:
            ckpt = pickle.load(f)

            # Generator
            G_original = ckpt["G_ema"]
            G_original = G_original.float()

            # Load discriminator if we use adversarial loss
            if self.opts.hyper_adv_lambda > 0:
                # Discriminator
                D_original = ckpt["D"]
                D_original = D_original.float()

        decoder = Generator(**G_original.init_kwargs)
        decoder.load_state_dict(G_original.state_dict())
        decoder.to(self.opts.device).eval()
        self.decoder = []
        for i in range(self.opts.batch_size):
            self.decoder.append(copy.deepcopy(decoder))

        # Load well-trained discriminator from StyleGAN2 for using adversarial loss
        self.discriminator = Discriminator(**D_original.init_kwargs)
        self.discriminator.load_state_dict(D_original.state_dict())
        self.discriminator.to(self.opts.device)

        # Load latent average
        self.latent_avg = self.decoder[0].mapping.w_avg

        # Define W-bar Encoder (E2 Encoder in Paper)
        if self.opts.encoder_type == "LayerWiseEncoder":
            self.w_bar_encoder = fpn_encoders.LayerWiseEncoder(50, "ir_se", self.opts)
        elif self.opts.encoder_type == "ResNetLayerWiseEncoder":
            self.w_bar_encoder = fpn_encoders.ResNetLayerWiseEncoder(self.opts)
        else:
            raise Exception(f"{self.opts.encoder_type} encoder is not defined.")

        if self.opts.checkpoint_path is not None:
            ckpt = torch.load(self.opts.checkpoint_path, map_location="cpu")

            # Load w bar encoder
            self.w_bar_encoder.load_state_dict(common.get_keys(ckpt, "w_bar_encoder"), strict=True)
            self.w_bar_encoder.to(self.opts.device)

            # Load hypernet
            self.hypernet.load_state_dict(common.get_keys(ckpt, "hypernet"), strict=True)
            self.hypernet.to(self.opts.device)

            # Load discriminator
            self.discriminator.load_state_dict(common.get_keys(ckpt, "discriminator"), strict=True)
            self.discriminator.to(self.opts.device)

            print("Loaded pretrained HyperInverter from: {}".format(self.opts.checkpoint_path))
        else:
            w_bar_encoder_ckpt = self.__get_encoder_checkpoint()
            self.w_bar_encoder.load_state_dict(w_bar_encoder_ckpt, strict=False)

    def __get_encoder_checkpoint(self):
        if "ffhq" in self.opts.dataset_type or "video" in self.opts.dataset_type:
            print("Loading encoders weights from irse50!")
            encoder_ckpt = torch.load(model_paths["ir_se50"])
            return encoder_ckpt
        else:
            print("Loading encoders weights from resnet34!")
            encoder_ckpt = torch.load(model_paths["resnet34"])
            mapped_encoder_ckpt = dict(encoder_ckpt)
            for p, v in encoder_ckpt.items():
                for original_name, psp_name in RESNET_MAPPING.items():
                    if original_name in p:
                        mapped_encoder_ckpt[p.replace(original_name, psp_name)] = v
                        mapped_encoder_ckpt.pop(p)
            return encoder_ckpt

    def forward(self, x, return_latents=False):
        bs, _, _, _ = x.size()
        num_ws = self.decoder[0].mapping.num_ws

        # Resize image to feed to encoder
        tic = time.time()
        x = F.interpolate(x, size=(256, 256), mode="bilinear", align_corners=False)

        # ======== Phase 1 ======== #

        # Obtain w code via W Encoder
        
        w_codes = self.w_encoder(x)  # bs x 1 x 512
        
        # Normalize with respect to the center of an average face
        w_codes = w_codes + self.latent_avg.repeat(w_codes.shape[0], 1)
        w_codes = w_codes.unsqueeze(1).repeat([1, num_ws, 1])
        toc = time.time()
        E1_time = toc-tic
        # Genenerate W-images
        tic = time.time()
        with torch.no_grad():
            w_images = self.decoder[0].synthesis(w_codes, added_weights=None, noise_mode="const")
        toc = time.time()
        generation_time = toc - tic
        # ======== Phase 2 ======== #

        # Get w_bar code via W bar encoder
        tic = time.time()
        w_bar_codes = self.w_bar_encoder(x)

        # Get w image features
        w_images_resized = F.interpolate(w_images, size=(256, 256), mode="bilinear", align_corners=False)
        w_image_codes = self.w_bar_encoder(w_images_resized)
        toc = time.time()
        bar_encoder_features_time = toc - tic
        # Predict weights added to weights of StyleGAN2-Ada synthesis network
        tic = time.time()
        predicted_weights = self.hypernet(w_image_codes, w_bar_codes)
        toc = time.time()
        hypernet_time = toc - tic
        # Generate final images from predicted weights and w codes
        final_images = []

        for idx in range(bs):
            # Add predicted weights to original StyleGAN2-Ada weights
            pred_weights_per_sample = {}
            for key in predicted_weights:
                pred_weights_per_sample[key] = predicted_weights[key][idx]

            # Convert to dict in order to feed to generator
            added_weights = common.convert_predicted_weights_to_dict(pred_weights_per_sample)

            # Gen final image
            w_code = w_codes[idx].unsqueeze(0)
            tic = time.time()
            final_image = (
                self.decoder[idx].synthesis(w_code, added_weights=added_weights, noise_mode="const").squeeze(0)
            )
            final_images.append(final_image)
            toc = time.time()
        final_generation = toc - tic
        final_images = torch.stack(final_images, 0)

        return_data = [w_images, final_images, predicted_weights, [generation_time, bar_encoder_features_time, hypernet_time, E1_time, final_generation]]
        if return_latents:
            return_data.append(w_codes)

        return tuple(return_data)

    def set_opts(self, opts):
        self.opts = opts


class HyperInverter_online(nn.Module):
    def __init__(self, opts):
        super().__init__()

        # Configurations
        self.set_opts(opts)

        # compute number of style inputs based on the output resolution
        self.opts.n_styles = int(math.log(self.opts.output_size, 2)) * 2 - 2

        # Hypernetwork
        self.target_shape = get_target_shapes(self.opts)
        self.hypernet = Hypernetwork(
            input_dim=512,
            hidden_dim=self.opts.hidden_dim,
            target_shape=self.target_shape,
        )

        # Define and load architecture
        self.load_weights()
        self.predictor = dlib.shape_predictor(paths_config.model_paths['shape_predictor'])

        # For visualization
        self.face_pool = torch.nn.AdaptiveAvgPool2d((256, 256))

    def load_weights(self):
        # Load W-Encoder (E1 Encoder in Paper)
        if self.opts.w_encoder_path is not None:
            w_encoder_path = self.opts.w_encoder_path
        elif self.opts.dataset_type == "ffhq_encode" and model_paths["w_encoder_ffhq"] is not None:
            w_encoder_path = model_paths["w_encoder_ffhq"]
        elif self.opts.dataset_type == "church_encode" and model_paths["w_encoder_church"] is not None:
            w_encoder_path = model_paths["w_encoder_church"]
        else:
            raise Exception("Please specify the path to the pretrained W encoder.")

        print(f"Loaded pretrained W encoder from: {w_encoder_path}")

        ckpt = torch.load(w_encoder_path, map_location="cpu")

        opts = ckpt["opts"]
        opts = argparse.Namespace(**opts)

        if "ffhq" in self.opts.dataset_type or "celeb" in self.opts.dataset_type or "video" in self.opts.dataset_type:
            # Using ResNet-IRSE50 for facial domain
            self.w_encoder = fpn_encoders.BackboneEncoderUsingLastLayerIntoW(50, "ir_se", opts)
        else:
            # Using ResNet34 pre-trained on ImageNet for other domains
            self.w_encoder = fpn_encoders.ResNetEncoderUsingLastLayerIntoW()

        self.w_encoder.load_state_dict(common.get_keys(ckpt, "encoder"), strict=True)
        self.w_encoder.to(self.opts.device).eval()
        common.toogle_grad(self.w_encoder, False)

        # load the online learner!
        self.ODL = online_learner.simpleODL(68*2, 5, 10, 1)

        # Load pretrained StyleGAN2-ADA models
        if self.opts.dataset_type == "ffhq_encode":
            stylegan_ckpt_path = model_paths["stylegan2_ada_ffhq"]
        elif self.opts.dataset_type == "church_encode":
            stylegan_ckpt_path = model_paths["stylegan2_ada_church"]

        with open(stylegan_ckpt_path, "rb") as f:
            ckpt = pickle.load(f)

            # Generator
            G_original = ckpt["G_ema"]
            G_original = G_original.float()

            # Load discriminator if we use adversarial loss
            if self.opts.hyper_adv_lambda > 0:
                # Discriminator
                D_original = ckpt["D"]
                D_original = D_original.float()

        decoder = Generator(**G_original.init_kwargs)
        decoder.load_state_dict(G_original.state_dict())
        decoder.to(self.opts.device).eval()
        self.decoder = []
        for i in range(self.opts.batch_size):
            self.decoder.append(copy.deepcopy(decoder))

        # Load well-trained discriminator from StyleGAN2 for using adversarial loss
        self.discriminator = Discriminator(**D_original.init_kwargs)
        self.discriminator.load_state_dict(D_original.state_dict())
        self.discriminator.to(self.opts.device)

        # Load latent average
        self.latent_avg = self.decoder[0].mapping.w_avg

        # Define W-bar Encoder (E2 Encoder in Paper)
        if self.opts.encoder_type == "LayerWiseEncoder":
            self.w_bar_encoder = fpn_encoders.LayerWiseEncoder(50, "ir_se", self.opts)
        elif self.opts.encoder_type == "ResNetLayerWiseEncoder":
            self.w_bar_encoder = fpn_encoders.ResNetLayerWiseEncoder(self.opts)
        else:
            raise Exception(f"{self.opts.encoder_type} encoder is not defined.")

        if self.opts.checkpoint_path is not None:
            ckpt = torch.load(self.opts.checkpoint_path, map_location="cpu")

            # Load w bar encoder
            self.w_bar_encoder.load_state_dict(common.get_keys(ckpt, "w_bar_encoder"), strict=True)
            self.w_bar_encoder.to(self.opts.device)

            # Load hypernet
            self.hypernet.load_state_dict(common.get_keys(ckpt, "hypernet"), strict=True)
            self.hypernet.to(self.opts.device)

            # Load discriminator
            self.discriminator.load_state_dict(common.get_keys(ckpt, "discriminator"), strict=True)
            self.discriminator.to(self.opts.device)

            print("Loaded pretrained HyperInverter from: {}".format(self.opts.checkpoint_path))
        else:
            w_bar_encoder_ckpt = self.__get_encoder_checkpoint()
            self.w_bar_encoder.load_state_dict(w_bar_encoder_ckpt, strict=False)

    def __get_encoder_checkpoint(self):
        if "ffhq" in self.opts.dataset_type or "video" in self.opts.dataset_type:
            print("Loading encoders weights from irse50!")
            encoder_ckpt = torch.load(model_paths["ir_se50"])
            return encoder_ckpt
        else:
            print("Loading encoders weights from resnet34!")
            encoder_ckpt = torch.load(model_paths["resnet34"])
            mapped_encoder_ckpt = dict(encoder_ckpt)
            for p, v in encoder_ckpt.items():
                for original_name, psp_name in RESNET_MAPPING.items():
                    if original_name in p:
                        mapped_encoder_ckpt[p.replace(original_name, psp_name)] = v
                        mapped_encoder_ckpt.pop(p)
            return encoder_ckpt

    def forward(self, x, return_latents=False):
        bs, _, _, _ = x.size()
        num_ws = self.decoder[0].mapping.num_ws

        # Obtain landmarks
        temp_img = common.tensor2im(x[0])
        landmarks = get_landmark(np.array(temp_img), self.predictor)

        # Resize image to feed to encoder
        tic = time.time()
        x = F.interpolate(x, size=(256, 256), mode="bilinear", align_corners=False)
        toc = time.time()
        resize_time = toc - tic

        # ======== Phase 1 ======== #

        # Obtain w code via W Encoder
        tic = time.time()
        w_codes = self.w_encoder(x)  # bs x 1 x 512
        # print("size of x is:", x.size())
        # detached_w_codes = w_codes.data.cpu().numpy()[0]
        # print(detached_w_codes)
        # print("=== LANDMARKS ===")
        # print(landmarks)
        ODL_codes = self.ODL(landmarks, w_codes)
        print(ODL_codes)
        toc = time.time()
        encoder_time = toc - tic
        # Normalize with respect to the center of an average face
        tic = time.time()
        w_codes = w_codes + self.latent_avg.repeat(w_codes.shape[0], 1)
        w_codes = w_codes.unsqueeze(1).repeat([1, num_ws, 1])
        toc = time.time()
        print("what this?", w_codes.size(), w_codes)
        normalize_time = toc - tic

        # Genenerate W-images
        tic = time.time()
        with torch.no_grad():
            w_images = self.decoder[0].synthesis(w_codes, added_weights=None, noise_mode="const")
        toc = time.time()
        generation_time = toc - tic
        # ======== Phase 2 ======== #

        # Get w_bar code via W bar encoder
        tic = time.time()
        w_bar_codes = self.w_bar_encoder(x)

        # Get w image features
        w_images_resized = F.interpolate(w_images, size=(256, 256), mode="bilinear", align_corners=False)
        w_image_codes = self.w_bar_encoder(w_images_resized)
        toc = time.time()
        bar_encoder_features_time = toc - tic
        # Predict weights added to weights of StyleGAN2-Ada synthesis network
        tic = time.time()
        predicted_weights = self.hypernet(w_image_codes, w_bar_codes)
        toc = time.time()
        hypernet_time = toc - tic
        # Generate final images from predicted weights and w codes
        final_images = []

        for idx in range(bs):
            # Add predicted weights to original StyleGAN2-Ada weights
            pred_weights_per_sample = {}
            for key in predicted_weights:
                pred_weights_per_sample[key] = predicted_weights[key][idx]

            # Convert to dict in order to feed to generator
            added_weights = common.convert_predicted_weights_to_dict(pred_weights_per_sample)

            # Gen final image
            w_code = w_codes[idx].unsqueeze(0)
            final_image = (
                self.decoder[idx].synthesis(w_code, added_weights=added_weights, noise_mode="const").squeeze(0)
            )
            final_images.append(final_image)

        final_images = torch.stack(final_images, 0)

        return_data = [w_images, final_images, predicted_weights, [encoder_time, normalize_time, generation_time, bar_encoder_features_time, hypernet_time, resize_time]]
        if return_latents:
            return_data.append(w_codes)

        return tuple(return_data)

    def set_opts(self, opts):
        self.opts = opts