#!/bin/bash
set -euo pipefail
cd /home/user
python -m redteam.harness snapshot
python -m redteam.harness case shortcut_rebuild_seed_answers
