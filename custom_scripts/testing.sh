#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/nasseraa/.conda/envs/inv_analysis/lib/

# Configurations
### Set to folder saving results
EXPERIMENT_DIR="results-256-256-lite"
### Set GPU ID 
GPU_ID=0
### Set path to TEST DATA folder
DATA_PATH="./input"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

# LPIPS
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode lpips \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"


### Set to folder saving results
EXPERIMENT_DIR="results-1024-1024-lite"
### Set path to TEST DATA folder
DATA_PATH="./data/ffhq-1024_100"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH" 

# LPIPS
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode lpips \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

### Set to folder saving results
EXPERIMENT_DIR="results-1024-1024-large"
### Set path to TEST DATA folder
DATA_PATH="./data/ffhq-1024_100"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH" 

# LPIPS
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode lpips \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"