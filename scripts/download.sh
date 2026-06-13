#!/bin/bash
# Estimated download size: 0 bytes. This reproduction uses a deterministic
# generated benchmark stored under data/ when scripts run.
set -e

cd /home/user

python - <<'PY'
from data.synthetic_tasks import write_npz
write_npz("data/synthetic_share_tasks.npz", seed=13)
PY
