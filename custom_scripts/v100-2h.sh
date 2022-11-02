#!/usr/bin/bash
srun --time=02:00:00 --gres gpu:v100:1 --mem=12G --resv-ports=1 --pty /bin/bash -l
