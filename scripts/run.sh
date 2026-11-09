#!/bin/bash
# Resume the final batch after its exact-training-equality assertion failed.
# The reference and baselines already completed in job dd9f0659-4e3.
set -euo pipefail
cd /home/user
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python -m redteam.hardening.final_audit
python validate.py --post-design --compare
