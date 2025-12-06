#!/bin/bash -l
#SBATCH -p gpu_short
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH -t 1:00:00
#SBATCH -o logs/minutes_%j.out
#SBATCH -e logs/minutes_%j.err

# Host setup
module load singularity
module load compiler/nvhpc/23.11

echo "Starting Meeting Minutes Automation"
echo "Date: $(date)"
echo "Host: $(hostname)"

# Argument: Input file path (relative to project root)
INPUT_FILE=$1

if [ -z "$INPUT_FILE" ]; then
  echo "Error: No input file provided."
  exit 1
fi

# Run inside Singularity container
# Adjust the container path if necessary. Using the one from the user's example.
CONTAINER_PATH="/work/yuto-sh/tensorflow_latest-gpu.sif"
PROJECT_DIR=$(pwd)

echo "Processing $INPUT_FILE in $PROJECT_DIR"

singularity exec --nv $CONTAINER_PATH \
  bash -c "cd $PROJECT_DIR && \
           pip install --user faster-whisper mlx-lm huggingface_hub && \
           python main.py $INPUT_FILE --summarize"

echo "Job finished at $(date)"
