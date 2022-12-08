##### Table of contents
1. [Getting Started](#Getting-Started)
2. [Experiments](#Experiments)
3. [Acknowledgments](#Acknowledgments)

# HypedUpInverter: Inverting a video into styleGAN space using HyperNetworks


> **Abstract:** 
    In this paper we explore the recent work of HyperInverters with extensive analysis, all while exploring new direction to employ HyperNetworks for real-time inversion applications. Most real-time applications are focused on a single subject over many frames, going off that knowledge, we can optimize the HyperNetwork for that single subject to improve the quality of the inversions while sacrificing little to no inference-time and efficiency. HyperNetworks are light and can be optimized or retrained in a short time, so we present two methods of doing real-time inversion, either by optimizing the network on a fixed set of frames, or training the hypernetwork on all frames of every video we wish to invert in real-time. In both cases we find the efficiency of the inversions improve while keeping the same speed, if not faster at higher efficiency.


## Getting Started

The codebase is tested on
- Ubuntu
- CUDA 10.0, CuDNN 7 

### Installation

- Clone this repo:
``` 
git clone https://github.com/Alooi/HypedUpInverter.git
cd HypedUpInverter
```

- Install dependencies:
```
conda create -p ./envs python=3.7.3
conda activate ./envs
pip install -r requirements.txt
```

### Datasets

- **Human Faces**: We use `70,000 images` from [FFHQ](https://github.com/NVlabs/ffhq-dataset) dataset to train, and `2,824 images` from [CelebA-HQ](https://github.com/tkarras/progressive_growing_of_gans) dataset to test. The images have `1024 x 1024` resolution and are cropped and aligned to the center. Refering [FFHQ](https://github.com/NVlabs/ffhq-dataset) for more details about the pre-processing step.

- **VFHQ**:  We used a single video from VFHQ, find any video and of any length to run your own experiements on.

If you need to try with your own dataset, you can make the necessary modifications in: (i) `data_configs.py` to define your data paths; (ii) `transforms_configs.py` to define your data transformations.

## Training
Make sure to align all of your frames/images using the script in custom/aligning.sh

custom_scripts/train_fine_tuned.sh: This script is for training a new HyperNetwork with different parameters for every video. This will generate a new folder with the weights and other metrics.

If you are using iBex.kaust, you can use the custom job scripts included for training.

## Experiments

There are custom scripts written in /custom_scripts. Those scripts are meant to work on iBex.kaust with a change to the user name in the scripts.
Before doing any experiements, use the aligning script to align all of your images/frames if required.

### Quantitative Evaluation

custom_scripts/inferencing.sh: use this script to generate inversion, a change to the experiemnt path is required. The results will be in the same experiment folder of your choosing.

### Qualitative Comparison

custom_scripts/LPIPS.sh: contains LPIPS and L2 losses, a change to the experiemnt path is required.

For the following experiments, please visit file `configs/paths_config.py` and update `model_paths` dict with the paths to the pre-trained models of HypedUpInverter, HyperInverter and other inversion methods. For other inversion methods, please visit their Github repositories to download their pre-trained weights.

#### Reconstruction 

The results can be found in the `outputs/SAVED_RESULTS_DIR_NAME` folder.

## Acknowledgments
Our source code is developed based on the codebase of a great series of StyleGAN inversion researches from the Tel Aviv University group and HyperInverter, which are: [pSp](https://github.com/danielroich/PTIhttps://github.com/danielroich/PTI), [e4e](https://github.com/omertov/encoder4editing), [ReStyle](https://github.com/yuval-alaluf/restyle-encoder), [PTI](https://github.com/danielroich/PTI), and [HyperInverter](https://github.com/VinAIResearch/HyperInverter). 

For auxiliary pre-trained models, we specifically thank to [TreB1eN](https://github.com/TreB1eN/InsightFace_Pytorch), [MoCov2](https://github.com/facebookresearch/moco), [CurricularFace](https://github.com/HuangYG123/CurricularFace) and [MTCNN](https://github.com/TreB1eN/InsightFace_Pytorch). For editing directions, thanks to the authors of [GANSpace](https://github.com/harskish/ganspace), [InterFaceGAN](https://github.com/genforce/interfacegan) and [StyleCLIP](https://github.com/orpatashnik/StyleCLIP).

We leverage the PyTorch implementation of [StyleGAN2-ADA](https://github.com/NVlabs/stylegan2-ada-pytorch) for the StyleGAN model. All pre-trained StyleGAN models are from the official release of [StyleGAN2](https://drive.google.com/drive/folders/1yanUI9m4b4PWzR0eurKNq6JR1Bbfbh6L). We convert the original weights exported by TensorFlow code to compatible with the PyTorch version of StyleGAN2-ADA by using [the author's official script](https://github.com/NVlabs/stylegan2-ada-pytorch/blob/main/legacy.py).

Overall, thank you so much to the authors for their great works and efforts to release source code and pre-trained weights.

## Contacts
If you have any questions, please drop an email to ali.nasser.1@kaust.edu.sa or open an issue in this repository.
