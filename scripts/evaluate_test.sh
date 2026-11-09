#!/bin/bash
# Score every run under checkpoints/ on the held-out test streams.
#
# Imports only eval/test/; test inputs and labels are regenerated there at test
# time. Writes scoring/scores_test.json. Runs with no arguments.

set -e

cd /home/user

mkdir -p scoring

if [[ $# -gt 0 && "$1" != --* ]]; then
  set -- --prediction-root "$1" "${@:2}"
fi

python -m eval.test.evaluate "$@"
