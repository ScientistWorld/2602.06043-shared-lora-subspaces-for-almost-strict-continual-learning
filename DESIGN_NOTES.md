# Final evaluation design

The active design uses raw deployed-state snapshots, independently held evaluation data, evaluator-owned reference and baseline comparisons, whole-attempt failure gates and normalized metric improvements. See [briefing/evaluation.md](briefing/evaluation.md) for the public interface and [HARDENING.md](HARDENING.md) for implementation decisions, measurements and residual limitations. Final verification is recorded in [VERIFICATION.md](VERIFICATION.md).

The notes below are historical. Their CSV interface, public test labels, trusted summary costs and shared-row train/test split have all been superseded. They do not describe the current gym.

---

# Historical train/test evaluation design notes

## Checked

- Read `eval/train/evaluate.py`, `eval/test/evaluate.py`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and `scoring/reference.json`.
- Confirmed the train script calls `eval.train.evaluate` and defaults to `scoring/scores_train.json`.
- Confirmed the test script calls `eval.test.evaluate` and defaults to `scoring/scores_test.json`.
- Confirmed neither split imports from the other split or from `method/`.
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` are absent.
- Ran `bash -n` on both split scripts.

## Changed

- Fixed a label-leak/gameability issue: train and test evaluators no longer trust the method-authored `label` column in prediction CSVs. They now load canonical `y_test_*` labels from the tracked benchmark `.npz` files selected by `summary.json` seed.
- Hardened prediction artifact validation: each scored slice now requires exactly one prediction for every canonical example ID in that slice and rejects duplicate or out-of-range example IDs.
- Added the machine-independent `temporary_adaptation_parameters` constraint metric to both experiments, so methods are scored on peak temporary adaptation footprint as well as final stored parameters.
- Added required `description` fields for every metric in `scoring/reference.json`.
- Reweighted the two deterministic streams from 0.65/0.35 to 0.5/0.5 to reduce seed-specific overfitting pressure.

## Runtime Concerns For Runner Iteration

- I did not run evaluators or regenerate scores, per this iteration's file-edit-only rule.
- The split evaluators now import `numpy`; this matches `environment/setup.sh`, which installs `numpy`, but local inline inspection failed because the login-node Python environment did not have `numpy` available.
- The train/test split is still a deterministic row split over the same generated test sets. It is useful for catching visible-row overfitting and artifact manipulation, but it is not an OOD split.
- Parameter accounting still depends on method-authored `summary.json`; the new temporary-parameter metric improves triangulation but cannot prove a method did not hide state elsewhere.
