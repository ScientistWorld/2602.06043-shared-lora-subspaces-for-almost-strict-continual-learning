#!/bin/bash
# Standard visible evaluation: scores every run under checkpoints/ on the
# development streams and writes scoring/scores.json.
#
# Self-contained in eval/train/ (plus the visible data loader in data/); never
# imports method/. A run is any directory checkpoints/<method_name>/ holding
# <stream_id>/after_task_XX.npz deployed-state snapshots
# (format: briefing/evaluation.md).
#
# Usage:
#   bash scripts/evaluate.sh [prediction_root]

set -e

cd /home/user

mkdir -p scoring

root="${1:-checkpoints}"
python -m eval.train.evaluate --prediction-root "$root" --output scoring/scores.json
