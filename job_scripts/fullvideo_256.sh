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

EXPERIMENT_DIR="exp-fullvideo-256"
W_ENCODER_PATH="pretrained_models/w_encoder_e4e_ffhq_encode.pt"
MODEL_PATH="pretrained_models/hyper_inverter_e4e_ffhq_encode_lightweight.pt"
GPU_ID=0

echo "training 256 dim using w_encoder_e4e\n"
echo "full training video!\n"

CUDA_VISIBLE_DEVICES="$GPU_ID" \
python scripts/train.py \
--dataset_type=video_encode \
--encoder_type=LayerWiseEncoder \
--w_encoder_path="$W_ENCODER_PATH" \
--output_size=1024 \
--exp_dir="$EXPERIMENT_DIR" \
--batch_size=8 \
--batch_size_used_with_adv_loss=4 \
--workers=4 \
--val_interval=10 \
--save_interval=10 \
--encoder_optim_name=adam \
--discriminator_optim_name=adam \
--encoder_learning_rate=1e-4 \
--discriminator_learning_rate=1e-4 \
--hyper_lpips_lambda=0.8 \
--hyper_l2_lambda=1.0 \
--hyper_id_lambda=0.1 \
--hyper_adv_lambda=0.005 \
--hyper_d_reg_every=16 \
--hyper_d_r1_gamma=10.0 \
--step_to_add_adversarial_loss=30 \
--target_shape_name=conv_without_bias  \
--max_steps=100 \
--hidden_dim=256 \
--num_cold_steps=20 \
--save_checkpoint_for_resuming_training \
# --resume_training \
# --checkpoint_path="$MODEL_PATH" \


conda deactivate