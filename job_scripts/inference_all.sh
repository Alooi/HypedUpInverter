#!/bin/bash
#SBATCH --job-name hypernet256
#SBATCH --time=0-00:03:00
#SBATCH -o gpu.%A.out
#SBATCH -e gpu.%A.err
#SBATCH --gres=gpu:v100:1
#SBATCH --mem=25GB
module purge
module load anaconda3/2019.10
module load cudnn/8.1.1-cuda11.2.2
module load gcc/6.4.0
source activate inv_analysis

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


conda deactivate