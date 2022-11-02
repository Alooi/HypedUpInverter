#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/nasseraa/.conda/envs/inv_analysis/lib/

# Configurations
### Set to folder saving results
EXPERIMENT_DIR="./results-default-1"
### Set the path to model path 
MODEL_PATH="pretrained_models/hyper_inverter_e4e_ffhq_encode_lightweight.pt"
### Set GPU ID 
GPU_ID=0
### Set path to TEST DATA folder
DATA_PATH="./data/faces/test1"

#======================================

# # Inference on test set 
# CUDA_VISIBLE_DEVICES="$GPU_ID" \
# python scripts/inference.py \
# --exp_dir="$EXPERIMENT_DIR" \
# --checkpoint_path="$MODEL_PATH" \
# --data_path="$DATA_PATH" \
# --batch_size=4 \
# --workers=4

# # LPIPS 
# CUDA_VISIBLE_DEVICES="$GPU_ID" \
# python scripts/calc_losses_on_images.py \
# --mode lpips \
# --data_path="$EXPERIMENT_DIR"/inference_results \
# --gt_path="$DATA_PATH"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH" 