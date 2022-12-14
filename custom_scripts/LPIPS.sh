#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/nasseraa/.conda/envs/inv_analysis/lib/

GPU_ID=0
Configurations
## Set to folder saving results
EXPERIMENT_DIR="results-fullvideo-64"
### Set path to TEST DATA folder
DATA_PATH="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"

#======================================

# LPIPS 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode lpips \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

EXPERIMENT_DIR="results-fullvideo-128"
DATA_PATH="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"

# LPIPS 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode lpips \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

EXPERIMENT_DIR="results-fullvideo-32"
DATA_PATH="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"

# LPIPS 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode lpips \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH"

# L2 
CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/calc_losses_on_images.py \
--mode l2 \
--data_path="$EXPERIMENT_DIR"/inference_results \
--gt_path="$DATA_PATH" 