#!/bin/sh

# Configurations
### Set to folder saving results
EXPERIMENT_DIR="./results-default-1"

### Set path to TEST DATA folder
DATA_PATH="./data/faces/test1"

python scripts/custom_mse.py -i $DATA_PATH -o $EXPERIMENT_DIR