#!/bin/bash
# One batched hardening validation; restored to reference reproduction after it finishes.
set -euo pipefail
cd /home/user
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
# Reproduce the unchanged final training code; saved variants need rescoring only.
bash scripts/reproduce.sh
python -m redteam.hardening.final_audit
python validate.py --post-design --compare
