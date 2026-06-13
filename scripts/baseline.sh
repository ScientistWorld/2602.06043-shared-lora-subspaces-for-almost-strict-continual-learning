#!/bin/bash
# Run a baseline method from the paper.
#
# Baselines are simple reference methods the paper compares against. 
# Implement this only if applicable, i.e. the paper has baselines.
# You do not need to implement all baselines to begin — 
# just enough to validate that the evaluation pipeline works 
# and provide a reference point. You can decide to expand more baselines later.
# Each baseline must be actually run and scored through evaluate.sh
# so the numbers are verified, not self-reported.
# You can decide what this baseline script should do yourself.
#
# Usage:
#   bash scripts/baseline.sh <name>

set -e

cd /home/user

name="${1:-lora}"

case "$name" in
  lora)
    python -m baseline.lora_linear \
      --kind lora \
      --data data/synthetic_share_tasks.npz \
      --output-dir checkpoints/lora/predictions
    ;;
  frozen)
    python -m baseline.lora_linear \
      --kind frozen \
      --data data/synthetic_share_tasks.npz \
      --output-dir checkpoints/frozen/predictions
    ;;
  *)
    echo "Unknown baseline: $name" >&2
    exit 2
    ;;
esac

bash scripts/evaluate.sh
