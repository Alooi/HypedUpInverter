#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/nasseraa/.conda/envs/inv_analysis/lib/

INPUT_DATA_DIR="./data/faces/test1"
RESULT_DIR="./results-default-1"
MODEL_PATH="./pretrained_models/hyper_inverter_e4e_ffhq_encode_lightweight.pt"
GPU_ID=0

CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/inference.py \
--exp_dir="$RESULT_DIR" \
--checkpoint_path="$MODEL_PATH" \
--data_path="$INPUT_DATA_DIR" \
--batch_size=4 \
--workers=4