#!/bin/bash
# Hardening job: rebuild the reference end to end on the new hidden-test
# benchmark, then audit variants and shortcuts through the unmodified evaluators.
#
# Runs inside the gym container with the workspace at /home/user, no internet.

set -euo pipefail

cd /home/user

export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

# Public half of the stream registry (tracked in git once generated).
if [[ ! -f data/streams/manifest.json ]]; then
  python -m eval.test.export_public
fi
python -m eval.test.export_public --check

# Reference method + baselines end to end, visible evaluation.
bash scripts/reproduce.sh

# Hidden test with no arguments. A pre-written score file must not survive.
python - <<'PY'
import json
json.dump({"experiments": {"forged": {"results": {"share": {"final_average_accuracy": 100.0}}}}},
          open("scoring/scores_test.json", "w"))
PY
bash scripts/evaluate_test.sh
python - <<'PY'
import json
scores = json.load(open("scoring/scores_test.json"))
assert "forged" not in scores["experiments"], "pre-written score file survived the hidden test"
print("direct score write: overwritten by the evaluator")
PY

# Variants and shortcuts through the same evaluators.
python -m redteam.hardening.run_audit

python validate.py --post-design --compare || true
