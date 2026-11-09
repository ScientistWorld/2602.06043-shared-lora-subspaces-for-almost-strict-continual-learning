# Final verification

Milestone: **core_claim_plus**, for the scaled Share computation and its accuracy/storage tradeoff. This is not a GLUE, CIFAR or full-paper reproduction. See [HARDENING.md](HARDENING.md) for scope, numerical comparisons and remaining shortcuts.

Job `dd9f0659-4e3` completed fresh reference and four-baseline training from the final learning code. Its audit stopped only on an invalid exact-equality assertion against older training results. The comparison was frozen to the fresh run. Continuation `d9180772-7d8` rescored saved outputs without retraining and exited 0. The original and fresh measurements remain in `redteam/hardening/final/reproduction_drift.json`; the unexplained cross-run drift is disclosed, not treated as exact reproducibility.

The 38-case audit passed every check in [verification.json](redteam/hardening/final/verification.json):

- The no-argument hidden command scores every method directory; score-file injection is overwritten.
- Test answers and their generator are confined to `eval/test/`; changing public labels, dimensions and sample counts cannot change evaluation results. Development evaluation also owns its frozen inputs independently.
- Both evaluators read raw deployed-state arrays and recompute accuracy, forgetting and scalar counts. They do not import `method/` or each other, retrain, or trust prediction CSVs, resource claims or verdicts.
- Missing history, invalid/overflowing state and excess storage fail. Failure in either experiment fails the whole attempt. Every failed attempt ranks below every successful attempt.
- Every weighted, direction-correct, coefficient-magnitude, cohort-normalized rank term was independently recomputed. Reference and baseline comparisons are fixed in `eval/`.
- Raw rescoring of the fresh reference equals the frozen comparison. Canonical scores contain only that reference and the four official baselines.

Better methods score higher than seed variation: the six honest improved runs gain +0.2571 to +0.3235 rank, against a three-reference-seed range of 0.0404. The four-direction seed-0 variant gains 6.20 ± 1.68 / 14.24 ± 1.06 accuracy points on paired six-/ten-task streams, mean ± stream standard error, at unchanged storage. Weaker trained controls lose 0.2036–0.4175 rank. Neither the reference nor a simple variant reaches the scored accuracy ceiling. Full independent task states fail the fixed storage allowance; compact simple baselines fail the accuracy floor.

`python validate.py --post-design --compare` passes. Its two input-loader RNG warnings are heuristic: scoring applies submitted snapshots to those inputs. Expected numerical-overflow warnings came from adversarial states that were rejected. Final packaging restores `scripts/run.sh` to reference/baseline reproduction and both evaluations, and pins the package versions used by the jobs. Syntax and shell checks cover these packaging edits; no learning or scoring behavior changed after the successful audit.

Remaining limitations are explicit: static snapshots cannot prove chronology or prohibit replay; backdating and joint replay still gain +0.0399/+0.5941 and require the separate attempt grader. Exact valid-state copying still ties. The benchmark is synthetic, does not measure training memory, and its single long development stream gives imperfect test calibration. These limits prevent a claim of full scientific coverage or complete shortcut resistance.
