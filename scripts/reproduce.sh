#!/bin/bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and should call
# scripts/baseline.sh and scripts/method.sh to run baselines and
# the paper's method, each of which calls scripts/evaluate.sh.
#
# Assumes:
#   - Container is built (environment/container.sif)
#   - Data and models are downloaded (via scripts/download.sh)
#   - Working directory is /home/user
#
# This is the "gold standard" reproduction — 
# You do not need to run this, but keep this in good shape
# so other agents can easily run a full loop of reproduction and get the paper's numbers.

set -e

cd /home/user

rm -rf \
  checkpoints/frozen/predictions \
  checkpoints/lora/predictions \
  checkpoints/share/predictions \
  checkpoints/frozen_seed21/predictions \
  checkpoints/lora_seed21/predictions \
  checkpoints/share_seed21/predictions

rm -f data/synthetic_share_tasks.npz
bash scripts/baseline.sh frozen
bash scripts/baseline.sh lora
bash scripts/method.sh

rm -f data/synthetic_share_tasks_seed21.npz
python -m baseline.lora_linear \
  --kind frozen \
  --seed 21 \
  --data data/synthetic_share_tasks_seed21.npz \
  --output-dir checkpoints/frozen_seed21/predictions
python -m baseline.lora_linear \
  --kind lora \
  --seed 21 \
  --data data/synthetic_share_tasks_seed21.npz \
  --output-dir checkpoints/lora_seed21/predictions
python -m method.share_linear \
  --seed 21 \
  --data data/synthetic_share_tasks_seed21.npz \
  --output-dir checkpoints/share_seed21/predictions
bash scripts/evaluate.sh
python validate.py --compare
