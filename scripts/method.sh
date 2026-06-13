#!/bin/bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

python -m method.share_linear \
  --data data/synthetic_share_tasks.npz \
  --output-dir checkpoints/share/predictions

bash scripts/evaluate.sh
