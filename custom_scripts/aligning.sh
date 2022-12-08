#!/bin/sh

# RAW_IMAGE_DIR="../../../../ibex/scratch/nasseraa/clip-long-train-100"
# PROCESSED_IMAGE_DIR="../../../../ibex/scratch/nasseraa/clip-long-train-100-aligned"

# python scripts/align_all_parallel.py \
# --raw_dir "$RAW_IMAGE_DIR" \
# --saved_dir "$PROCESSED_IMAGE_DIR" \
# --num_threads 8

RAW_IMAGE_DIR="../../../../ibex/scratch/nasseraa/clip-long-test-100"
PROCESSED_IMAGE_DIR="../../../../ibex/scratch/nasseraa/clip-long-test-100-aligned"

python scripts/align_all_parallel.py \
--raw_dir "$RAW_IMAGE_DIR" \
--saved_dir "$PROCESSED_IMAGE_DIR" \
--num_threads 8