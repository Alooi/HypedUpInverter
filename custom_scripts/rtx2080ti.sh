#!/usr/bin/bash
srun --time=02:00:00 --gres gpu:rtx2080ti:1 --mem=12G --resv-ports=1 --pty /bin/bash -l