import sys
import os
import torch
import writetofile

sys.path.append(".")
sys.path.append("..")

os.makedirs("pretrained_dicts", exist_ok=True)

# load model from checkpoint
def load_model_from_checkpoint(checkpoint_path, model_name):
    # print(os.getcwd())
    ckpt = torch.load(checkpoint_path, map_location="cpu")
    writetofile.write_to_file(os.path.join("pretrained_dicts", model_name + ".txt"), ckpt.keys())

# load_model_from_checkpoint("pretrained_models/e4e_ffhq_encode.pt", "e4e_ffhq_encode")
# load_model_from_checkpoint("pretrained_models/hyper_inverter_e4e_ffhq_encode_lightweight.pt", "hyper_inverter_e4e_ffhq_encode_lightweight")
load_model_from_checkpoint("exp-scratch-100/checkpoints/iteration_0.pt", "iteration_0")
# load_model_from_checkpoint("pretrained_models/w_encoder_e4e_ffhq_encode.pt", "w_encoder_e4e_ffhq_encode")
# load_model_from_checkpoint("pretrained_models/resnet34-333f7ec4.pth", "resnet34-333f7ec4")