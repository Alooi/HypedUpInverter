#!/bin/sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/nasseraa/.conda/envs/inv_analysis/lib/

GPU_ID=0

INPUT_DATA_DIR="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"
RESULT_DIR="./results-fullvideo-32"
MODEL_PATH="./exp-fullvideo-32/checkpoints/iteration_100.pt"

CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/inference.py \
--exp_dir="$RESULT_DIR" \
--checkpoint_path="$MODEL_PATH" \
--data_path="$INPUT_DATA_DIR" \
--batch_size=4 \
--workers=4



INPUT_DATA_DIR="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"
RESULT_DIR="./results-fullvideo-64"
MODEL_PATH="./exp-fullvideo-64/checkpoints/iteration_100.pt"


CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/inference.py \
--exp_dir="$RESULT_DIR" \
--checkpoint_path="$MODEL_PATH" \
--data_path="$INPUT_DATA_DIR" \
--batch_size=4 \
--workers=4

# INPUT_DATA_DIR="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"
# RESULT_DIR="./results-video-light"
# MODEL_PATH="./exp-fullvideo-128/checkpoints/iteration_98.pt"

# CUDA_VISIBLE_DEVICES="$GPU_ID" \
# python scripts/inference.py \
# --exp_dir="$RESULT_DIR" \
# --checkpoint_path="$MODEL_PATH" \
# --data_path="$INPUT_DATA_DIR" \
# --batch_size=4 \
# --workers=4