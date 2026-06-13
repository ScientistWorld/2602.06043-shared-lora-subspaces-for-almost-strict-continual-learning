#!/bin/bash
# Evaluate the visible train slice from saved prediction artifacts.
#
# This mirrors scripts/evaluate.sh's method-agnostic contract: it imports only
# eval/ code, reads prediction artifacts from checkpoints/, and writes a scores
# JSON file under scoring/.

set -e

cd /home/user

mkdir -p scoring

if [[ $# -gt 0 && "$1" != --* ]]; then
  set -- --prediction-root "$1" "${@:2}"
fi

python -m eval.train.evaluate "$@"
