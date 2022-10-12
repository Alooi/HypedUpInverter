#!/bin/sh

RAW_IMAGE_DIR="./input"
PROCESSED_IMAGE_DIR="./output"

python scripts/align_all_parallel.py \
--raw_dir "$RAW_IMAGE_DIR" \
--saved_dir "$PROCESSED_IMAGE_DIR" \
--num_threads 8