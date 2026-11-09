#!/bin/bash
# Score every run under checkpoints/ on the visible development streams.
#
# Imports only eval/train/ and the visible data loader; writes
# scoring/scores_train.json. Runs with no arguments.

set -e

cd /home/user

mkdir -p scoring

if [[ $# -gt 0 && "$1" != --* ]]; then
  set -- --prediction-root "$1" "${@:2}"
fi

python -m eval.train.evaluate "$@"
