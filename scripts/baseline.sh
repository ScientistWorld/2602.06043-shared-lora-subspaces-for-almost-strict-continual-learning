#!/bin/bash
# Run one baseline on every stream and score the development streams.
#
# Usage:
#   bash scripts/baseline.sh <independent_lora|frozen_backbone|sequential_lora|independent_rank1>

set -e

cd /home/user

name="${1:-independent_lora}"

case "$name" in
  independent_lora|frozen_backbone|sequential_lora|independent_rank1)
    rm -rf "checkpoints/$name"
    python -m baseline.lora_linear --kind "$name" --output-root "checkpoints/$name"
    ;;
  *)
    echo "Unknown baseline: $name" >&2
    exit 2
    ;;
esac

bash scripts/evaluate.sh
