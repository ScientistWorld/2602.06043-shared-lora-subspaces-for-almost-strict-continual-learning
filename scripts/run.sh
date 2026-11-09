#!/bin/bash
# Reproduce the reference and official baselines end to end, then score both
# splits. Audit variants and shortcuts are deliberately not reference results.
set -euo pipefail
cd /home/user
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
bash scripts/reproduce.sh
bash scripts/evaluate_test.sh
python validate.py --post-design --compare
