# Hardening record

**Better results now score higher by more than the measured seed variation.** Six genuine improved runs gain +0.2571 to +0.3235 in the final 38-attempt cohort; the three reference seeds span 0.0404. Weaker trained controls lose 0.2036–0.4175. The major answer, resource, comparison and failure-gate shortcuts below are closed. Snapshot backdating and replay remain paying shortcuts for the separate attempt review, with their scores disclosed below.

This document supersedes historical CSV/summary-based evaluation descriptions. The original audit is preserved in [REDTEAM.md](REDTEAM.md). Final evidence is in [verification.json](redteam/hardening/final/verification.json), [results_test.json](redteam/hardening/final/results_test.json) and [results_train.json](redteam/hardening/final/results_train.json). Use each JSON's `evaluator_ranking.rank_improvement` for the actual all-attempt rank: the adjacent `cases.rank_delta` and Markdown audit tables also report a different, explicitly labelled honest-only cohort.

## Scope and scientific fidelity

The paper is *Shared LoRA Subspaces for almost Strict Continual Learning*, §3.2, Algorithm 1, Tables 1–2 and appendix §8.1. The implemented computation remains initial LoRA training, centered factor SVD, temporary top-direction adaptation, reconstruction of past adapters from retained state, SVD merging, analytical projection, and current-task-only coefficient refinement. It does not replay old data. The reference uses the appendix's two temporary directions and centered merges; four directions are the paper's main-text setting and an honest comparison. The appendix and main-text merge equations differ; the uncentered comparison preserves centered initialization.

This is a synthetic scaling of that computation, not a reproduction of RoBERTa/GLUE, ViT/CIFAR or the other modalities. The base is a frozen random 20×96 map, not a pretrained representation. Settings remain r=12, k=8, p=4, full-batch AdamW (0.03, decay 0.001), 700 initialization steps, 1500 adaptation steps and 700 current-task coefficient-refinement steps. Initial-task coefficient fitting remains a special case rather than a separate temporary-adaptation/merge pass. The reference does not reproduce the paper's optimizer schedule, explained-variance rank selection, full-model memory figures, or relaxed Share-full setting. No such results are claimed.

The original four-task, exposed-answer benchmark has been replaced by six- and ten-task streams: six and four hidden streams respectively, 1000 held-out examples per task, 76,000 test examples total. Three independent development streams follow the same generator and preprocessing, with 500 validation examples per task. Separate public and private RNG components keep hidden teachers, held-out inputs, labels, noise, and their regenerating code exclusively in `eval/test/`. The tracked manifest contains only public seeds, training labels and development validation labels.

## Defenses and ranking

- The evaluator applies raw deployed-state arrays to its own base weights and inputs; it recomputes accuracy, forgetting and stored scalar counts. Prediction CSVs, summaries, resource claims, score files and method-written verdicts have no authority.
- Every task snapshot is required. All arrays must be real, finite, correctly shaped and named. Noncanonical snapshot names and excessive expanded archives fail. Overflowing reconstructed updates or logits fail.
- Evaluator-owned dimensions, input counts, labels, resource denominator (one rank-12 adapter per task), budgets (1392 shared values, 139 per task), 40% success floor, reference metrics and baseline context cannot be changed through a method's artifacts. Visible evaluation has its own frozen manifest and loader. Train and test share no implementation or data-loader imports.
- Failure in either required experiment fails the entire attempt: both experiments receive accuracy 0, forgetting 100, parameter fraction 1. Every passing attempt dominates this scored vector, regardless of cohort normalization.
- Ranking adds `weight × abs(coefficient) × direction × (value − fixed reference) / population sd` over the methods on disk plus the fixed reference anchor. Zero-variance metrics contribute zero. Actual ranks and normalizers are emitted in `_metadata.ranking`. Coefficient signs cannot reverse the stated better direction.
- Accuracy is scored once (coefficient 1), forgetting once (0.2), and deployed parameter fraction once (0.4), with experiment weights 0.5 each. The original rubric double-counted accuracy through per-task scores and storage through fractions and inverse compression, and trusted temporary training costs. Removing overlapping rewards keeps the scientific quantities independent; temporary training costs are no longer claimed as measured. Paper values are unchanged in `_paper_reported`; scaled results are labelled as reproduced measurements.

## Before and after: scientific ordering

The original test had two exposed four-task streams. Its ranks below are from REDTEAM's 28-attempt cohort. The final test uses different, hidden six- and ten-task streams and the evaluator's 38-attempt cohort plus its fixed reference anchor. These scalar magnitudes are not directly comparable across cohorts or datasets; within each column the reference is zero. Restoring current-task coefficient refinement is part of the paper's procedure and is now also in the reference, rather than reserved for an improved variant.

| Comparison | Original test accuracy (%) | Original Δrank | Final test accuracy (%) | Final Δrank |
|---|---:|---:|---:|---:|
| Reference, stored / fresh | 66.00 / 68.50 | 0 | 71.34 / 64.83 | 0 |
| Four directions + coefficient refinement, seed 0 | 73.25 / 77.13 | +0.3200 | 77.53 / 79.07 | +0.3235 |
| Same, seed 1 | 76.38 / 73.88 | +0.5801 | 74.44 / 77.94 | +0.2571 |
| Same, seed 2 | 79.50 / 76.50 | +0.8159 | 76.66 / 77.19 | +0.2812 |
| Four directions + uncentered merge, seed 0 | 74.75 / 76.75 | +0.6354 | 77.23 / 79.00 | +0.3181 |
| Same, seed 1 | 76.00 / 76.00 | +0.6615 | 77.75 / 78.69 | +0.3217 |
| Same, seed 2 | 78.13 / 74.50 | +0.6354 | 77.11 / 79.16 | +0.3184 |
| Untrained weak control | 9.50 / 8.25 | −3.1954 | 0 / 0 (failed) | −3.1273 |
| Reference-seed rank range | — | 2.1700 | — | 0.0404 |

Originally no improved variant exceeded the reference seed range. Now even the smallest genuine gain exceeds that range by 6.36×. Reference final accuracies across seeds 0/1/2 are 71.34/70.13/70.87% on six-task streams and 64.83/63.60/64.81% on ten-task streams: ranges 1.21/1.23 percentage points. The same frozen backbone, training examples and held-out examples are used for every method. Seeds change only method initialization.

Additional final controls remove coefficient refinement while preserving the rest of the computation:

| Final control | Six / ten-task accuracy (%) | Six / ten-task forgetting (pp) | Δrank |
|---|---:|---:|---:|
| No refinement, seed 0 | 60.93 / 49.10 | 6.58 / 7.74 | −0.3651 |
| No refinement, seed 1 | 56.73 / 49.79 | 8.84 / 7.21 | −0.4175 |
| No refinement, seed 2 | 59.71 / 48.47 | 5.28 / 8.83 | −0.3908 |
| No refinement, quarter training, seed 0 | 63.71 / 56.33 | 2.15 / 3.98 | −0.2036 |
| No refinement, quarter training, seed 1 | 62.59 / 54.65 | 3.22 / 3.80 | −0.2456 |

Paired comparisons use each independent stream as one observation, not individual examples as independent replications. Four-direction seed 0 improves accuracy by **6.20 ± 1.68 pp** on six-task streams (6/6 wins) and **14.24 ± 1.06 pp** on ten-task streams (4/4 wins), mean ± standard error of paired stream gains. Its forgetting improves from 6.29/12.54 to 3.08/1.83 pp at identical storage. Seed 2 gains 5.33 ± 1.60 / 12.35 ± 1.01 pp. Seed 1's six-task gain is less certain (3.10 ± 2.78 pp, 5/6 wins); its ten-task gain is 13.11 ± 1.87 pp. All six improved variants gain rank; this does not claim a confidence interval from only three initialization seeds. The no-refinement seed 0 control loses 10.41 ± 2.04 / 15.74 ± 1.83 pp and wins no stream.

## Headroom, baselines and the paper's direction

The reference is at the better bound of **none** of its three scored metrics: accuracy is 71.34/64.83%, forgetting is 6.29/12.54 pp, and deployed parameter fraction is 0.1571/0.1126. The original test also had no reference ceiling, but improvement was smaller than seed variation. We expanded the original experiment to six-task streams and added a scored ten-task experiment, each weight 0.5. The longer setting exposes accumulated retention error and the accuracy cost of compression, where the paper's strict method falls short. It raises the independent-adapter burden from 5568 to 13920 values. No simple improved variant reaches a ceiling: the best observed accuracy is about 79%, leaving substantial measured headroom.

All official baselines were rerun from final code, not merely rescored:

| Method | Raw six / ten-task accuracy (%) | Raw forgetting (pp) | Stored values, six / ten | Final audit Δrank |
|---|---:|---:|---:|---:|
| Reference | 71.34 / 64.83 | 6.29 / 12.54 | 1312 / 1568 | 0 |
| Frozen base | 8.31 / 9.42 | 0 / 0 | 0 / 0 | −3.1273 (accuracy failure) |
| One sequential rank-12 state | 23.94 / 18.15 | 60.83 / 60.77 | 1392 / 1392 | −3.1273 (accuracy failure) |
| Independent rank-1 states | 35.78 / 32.21 | 0 / 0 | 696 / 1160 | −3.1273 (accuracy failure) |
| Independent rank-12 states | 73.18 / 70.96 | 0 / 0 | 8352 / 13920 | −3.1273 (storage failure) |

Share has much higher accuracy and less forgetting than sequential adaptation, with 6.37×/8.88× fewer deployed values than independent LoRA. Its accuracy deficit to independent LoRA is 1.84/6.13 pp. That direction agrees with the paper's strict GLUE comparison (78.69 versus 83.43); neither Share-full's small win nor the vision upper bound is claimed. This measures an accuracy/storage tradeoff, not the paper's 100× compression or 281× memory headline. Raw failed-run measurements remain in `_metadata.failed_runs`; their scored metrics are the failure vector.

The relevant brute force here is storing independent task models, not enumerating combinatorial candidates. Independent rank-12 states and full task matrices cannot satisfy the fixed per-task allowance. A packed independent control that really fits its counted arrays is an honest alternative: it reaches 66.58% on six-task streams but only 32.21% on ten-task streams, failing the accuracy floor. We do not reject honest fixed-basis alternatives merely for looking different from Share.

## Major shortcuts: fixes and measured scores

All final numeric ranks below use the same 38-attempt cohort. “Failed” means accuracy 0, forgetting 100 and fraction 1 in both experiments, rank **−3.1273**. Public-data poisoning is also tested by changing training labels, dimensions, sample counts and fake test answers while holding raw state fixed; both evaluators' entire score objects remain unchanged.

| Shortcut from REDTEAM | Before Δrank | Fix and final outcome |
|---|---:|---|
| Read visible test answers | +2.0616 (100% / 100%) | Hidden inputs, teachers, noise, labels and generator only in `eval/test/`; prediction-only submission fails, −3.1273. |
| Rebuild answers from public seed | +2.0616 (100% / 100%) | Public seed controls inputs only; independent private randomness controls teachers/answers. Old answer-prediction submission fails, −3.1273. |
| Omit history | +0.4672 | Every canonical deployed-state snapshot required; forgetting recomputed. Missing history fails, −3.1273. |
| Forge resource costs | +1.5446e−96; +2.2 pairwise | All state values counted; summary claims ignored. Same raw reference remains exactly rank 0, with its true 1312/1568 values and 0.1571/0.1126 fraction. No fabricated cost is credited. Exact state copying remains indistinguishable, as discussed below. |
| Inflate baseline denominator | +1.3580e−96; +2.2 pairwise | Denominator fixed to 1392×T in `eval/`. Forged claims do not change reference rank 0 or any metric. |
| Replace canonical answers | +2.0616 | Public manifest is not evaluation ground truth; poisoning cannot change scores. A zero-update learner still fails, −3.1273. |
| Shrink test size | +0.4634 | Evaluator owns counts and dimensions; public size poisoning cannot change scores. Prediction-only shortened submission fails, −3.1273. |
| Poison comparison artifact | 0 (paying tie; degraded baseline) | Fixed evaluator-owned baseline context and reference. Corrupted baseline itself fails, −3.1273; reference and comparisons stay unchanged at 0. |
| Store every independent adapter | +0.8719 | Count actual deployed state and enforce per-task budget. 1392 > 139 values/task; fails, −3.1273. |
| Independent full task models | +0.4229 | Dense updates and identity factors count too; 2320 > 139 values/task in the new raw interface; fails, −3.1273. |
| Failing method with impossible costs | +1.7054 despite 0% accuracy | Hard whole-attempt success gate; numbers cannot override raw state. Tiny failing state and overflowing reconstruction both fail, −3.1273. |
| Forge CSV labels | −3.7384 | CSVs have no scoring role; missing raw state fails, −3.1273. |
| NaN cost/state | Undefined nonfinite score | Real finite arrays, finite reconstructed logits and strict JSON required. NaN and huge finite-overflow states fail, −3.1273. |
| Direct score-file write | 0; evaluator overwrote it | Retested overwrite: forged score file has no effect. Reference remains 0, not claimed 100% accuracy. |

Additional small fixes reject noncanonical snapshot aliases (`after_task_000.npz`) and excessive expanded archive sizes, and propagate failure in either required experiment to the entire attempt. The alias and one-valid/one-failing controls both score −3.1273. Failure ordering and every normalized rank term were independently recomputed and checked. These checks do not rely on leftover processes or Python environment tricks.

## Shortcuts left and limits

**Snapshot backdating still pays:** copying the final reference state into every earlier snapshot preserves 71.34/64.83% accuracy but fabricates zero forgetting, for **+0.0399** rank. **Joint training/replay plus backdating still pays:** 86.05/88.75% accuracy, zero forgetting and **+0.5941** rank. There was no corresponding measured original-REDTEAM run; these are newly quantified residuals, not closed attacks. Both violate the explicit training/snapshot constraints. Proving chronology or the training data used requires training execution or the separate attempt grader; the light static hidden test does neither. Rejecting every constant shared basis would also reject honest fixed-representation methods.

Copying the exact reference state is inherently indistinguishable from reproducing that state, so it still ties. Ignoring fabricated metadata removes its false scientific credit but does not solve plagiarism of a valid state. This is explicitly left for attempt review. We did not replay previously rejected empty/null submissions; missing states and invalid values are covered by the new raw-state validation.

This remains a synthetic linear problem, with a shared low-rank teacher structure, known task identity and modest task counts. It does not establish the paper's transformer, multimodal, actual memory, or hundreds-of-tasks results. Development and hidden data use the same distribution and preprocessing, but there are only two six-task development streams and one ten-task development stream. The fresh reference's development/test accuracies are 69.97/71.34% and 71.42/64.83%; the 6.59 pp long-stream gap is a remaining calibration limitation. The improved seed-0 variant gives 78.08/77.53% and 78.10/79.07%, with consistent ordering. No development-tuned-overfitting experiment is claimed.

## Execution, rerun drift and packaging

All scientific and scoring fixes were selected together from the reports before the final combined batch. Earlier scaled runs supplied the saved paired variants. Job `dd9f0659-4e3` reran the reference and all four official baselines from final training code, rescored saved variants, and exercised the shortcuts together. It completed training and inference but stopped on an invalid assertion that fresh training must exactly match archived training. With fixed configured seeds and checksummed inputs, test accuracy shifted by +0.339/+0.168 pp, and development accuracy by −2.550/−0.220 pp. The cause was not isolated; exact cross-run training equality is not claimed. Both versions are preserved in [reproduction_drift.json](redteam/hardening/final/reproduction_drift.json). These shifts are smaller than the demonstrated paired improvement.

The comparison was frozen to that fresh reference, rather than changing training or data to match earlier numbers. Continuation job `d9180772-7d8` only rescored saved states and completed all checks; exit 0. [verification.json](redteam/hardening/final/verification.json) records no-argument all-method scoring, score-file overwrite, frozen data under poisoning, frozen-reference rescoring equality, failure ordering and independent rank arithmetic. `python validate.py --post-design --compare` passes. Its two heuristic warnings flag RNG-based input loaders, not detached scoring: the evaluators do load and apply each method's raw snapshots. Overflow warnings are from deliberately invalid audit arrays and those runs fail.

Canonical `scoring/scores_test.json`, `scores_train.json` and `scores.json` contain only the fresh reference and four official baselines, never shortcuts or better variants. In that five-method canonical cohort the reference rank is 0 and each failed baseline is −3.3941; future ranks are normalized over the actual methods then on disk. Paper-reported numbers are preserved unchanged under `_paper_reported`, outside scaled targets. `briefing/`, `scoring/EXPERIMENTS.md`, `TARGETS.md`, `CONSTRAINTS.md` and `DIRECTION.md` describe the final interface, metrics and scope.

`scripts/run.sh` is restored to end-to-end reference/baseline reproduction followed by both evaluations and validation. Public package versions are pinned to the tested NumPy 2.4.6 and PyTorch 2.12.0. No pretrained artifacts or external datasets are used, so `scripts/download.sh` needs no network fetch; it verifies every reproducible public array against the tracked manifest. The container builds from `environment/`. No training is performed by the hidden test. Milestone remains **core_claim_plus** for the scaled core procedure and accuracy/storage claim, not full-paper reproduction.
