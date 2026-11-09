#!/bin/bash
# Reproduce the reference end to end: every baseline and the paper's method on
# every stream in data/streams/manifest.json, then the visible evaluation.
#
# Assumes the container is built and data/streams/manifest.json is present
# (tracked in git; verified by scripts/download.sh). Working directory /home/user.

set -e

cd /home/user

export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

bash scripts/download.sh
bash scripts/baseline.sh frozen_backbone
bash scripts/baseline.sh independent_lora
bash scripts/baseline.sh sequential_lora
bash scripts/baseline.sh independent_rank1
bash scripts/method.sh
bash scripts/evaluate_train.sh
