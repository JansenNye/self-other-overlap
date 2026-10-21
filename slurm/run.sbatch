#!/bin/bash
#SBATCH --job-name=research
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus=1
#SBATCH --mem=48G
#SBATCH --output=slurm-logs/%x-%j.out
# Submit from the repository root after mkdir -p slurm-logs.
# Example: sbatch slurm/run.sbatch python -m selfconcept.soo.evaluate --help
# Set your cluster's partition/account and GPU/memory requirements when submitting.
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit from the repository root}"
source .venv/bin/activate
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export TOKENIZERS_PARALLELISM=false
exec "$@"
