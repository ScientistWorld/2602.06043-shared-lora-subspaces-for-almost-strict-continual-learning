#!/bin/bash
# Evaluate the held-out test slice from saved prediction artifacts.
#
# The test pass uses eval/test/ and writes scoring/scores_test.json. When
# scoring/scores_train.json exists, the test evaluator scores every method entry
# listed there so train/test comparisons use the same method set.

set -e

cd /home/user

mkdir -p scoring

python -m eval.test.evaluate "$@"
