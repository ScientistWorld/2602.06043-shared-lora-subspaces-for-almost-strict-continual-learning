#!/bin/bash
set -euo pipefail
cd /home/user
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
python -m redteam.harness snapshot
trap 'python -m redteam.harness restore' EXIT
python -u -m redteam.run_batch
python -m redteam.summarize
