#!/bin/bash
# Run the paper's proposed method (Share) on every stream in
# data/streams/manifest.json and score the development streams.
#
# Writes deployed-state snapshots to checkpoints/share/<stream_id>/after_task_XX.npz.
#
# Usage:
#   bash scripts/method.sh

set -e

cd /home/user

rm -rf checkpoints/share
python -m method.share_linear --output-root checkpoints/share

bash scripts/evaluate.sh
