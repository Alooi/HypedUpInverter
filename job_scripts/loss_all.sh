#!/bin/bash
#SBATCH --job-name loss_all
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


conda deactivate