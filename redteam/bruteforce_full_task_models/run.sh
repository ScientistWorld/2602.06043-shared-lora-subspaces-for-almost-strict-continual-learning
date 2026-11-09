#!/bin/bash
set -euo pipefail
cd /home/user
python -m redteam.harness snapshot
python -m redteam.harness case bruteforce_full_task_models
