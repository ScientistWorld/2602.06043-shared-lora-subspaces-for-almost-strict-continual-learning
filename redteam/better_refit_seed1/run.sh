#!/bin/bash
set -euo pipefail
cd /home/user
python -m redteam.harness snapshot
python -m redteam.harness case better_refit_seed1
