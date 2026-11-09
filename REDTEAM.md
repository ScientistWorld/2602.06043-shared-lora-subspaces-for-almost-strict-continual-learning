# Audit: this gym does not reliably reward better research

**Better methods score higher in these runs, but their scalar gains do not exceed reference seed spread. The weaker control scores clearly lower. The requested robust scientific-ordering check therefore fails.** More seriously, copying public answers reaches 100% on both hidden streams, and a completely failing method can outrank the reference through fabricated resource metrics. These are scoring failures with the original evaluator, without changing its process or Python environment.

## 1. Genuine improvements and weaker controls

The comparison reference is the original `scoring/scores_test.json`, verified by rerunning the hidden evaluator on the original saved artifacts: **66.000% / 68.500% accuracy**, **1.4375 / 2.1875 percentage points forgetting**, 1,184 stored adaptation parameters, 248 temporary parameters, and 4.7027× compression. Its rank improvement is zero by definition. Paper numbers in `scoring/reference.json` are context, not the reproduced comparison scores.

Every row below has a runnable directory under `redteam/`, its own predictions, and saved train/test scores and evaluator exit codes. Accuracy and forgetting are reported as stream 13 / stream 21. `Δrank` uses the explicit 28-attempt cohort described below.

| Variant directory | Actual change | Test accuracy (%) | Forgetting (pp) | Δrank vs reference |
|---|---|---:|---:|---:|
| `reference_existing` | Original artifacts, reevaluated | 66.000 / 68.500 | 1.4375 / 2.1875 | 0 |
| `better_more_training` | 3× optimization steps: 2,100 initial LoRA; 4,500 per task | 63.875 / 63.375 | 1.5625 / 4.2500 | −0.4307 |
| `better_phi4` | Four temporary directions instead of two | 75.750 / 66.500 | 0.3750 / 8.6250 | −0.1122 |
| `better_refit` | Four directions; 700 steps refining current-task coefficients after each projection | 73.250 / 77.125 | 2.1250 / 2.6875 | +0.3200 |
| `better_refit_seed1` | Same refinement, next initialization seed | 76.375 / 73.875 | 0.6250 / 3.0000 | +0.5801 |
| `better_refit_seed2` | Same refinement, third initialization seed | 79.500 / 76.500 | 0.5625 / 2.5000 | +0.8159 |
| `better_stable_seed0` | Refinement plus uncentered merge SVD | 74.750 / 76.750 | 1.0625 / 1.8125 | +0.6354 |
| `better_stable_seed1` | Same merge variant, next seed | 76.000 / 76.000 | 0.9375 / 2.0000 | +0.6615 |
| `better_stable_seed2` | Same merge variant, third seed | 78.125 / 74.500 | 0.5000 / 3.5000 | +0.6354 |
| `weaker_untrained` | Zero optimization steps throughout | 9.500 / 8.250 | 0 / 0 | −3.1954 |
| `baseline_frozen` | Original frozen-backbone baseline | 9.500 / 8.250 | 0 / 0 | −3.1954 |

Refinement uses only the current task's training data, retains adaptation/SVD/reprojection, and never replays previous-task training data. The merge variant retains centered initialization and uses uncentered SVD for subsequent merges. Both retain 1,184 deployed parameters; their reported temporary count is 496. The uncentered variant follows the main-text merge equation; the appendix instead specifies centering, so this is a real algorithmic comparison rather than an unambiguous correction of a transcription error.

The six refined runs all improve accuracy on both streams over the stored reference, and all gain rank. However, their gains of **+0.3200 to +0.8159** are smaller than the reference's **2.1700** rank range. Under the requested spread criterion these scalar gains remain noise. The weak control's **−3.1954** drop exceeds that range. Merely training longer did not improve the actual result. Increasing temporary capacity alone worsened stream-21 forgetting substantially, so its lower scalar rank is a defensible tradeoff, not evidence of reversed metric direction.

## 2. Seed spread and reproduction check

Datasets and evaluation rows were held fixed. Initialization seeds are 13/14/15 for stream 13 and 21/22/23 for stream 21; these are three paired reference reruns, not three different test datasets.

| Reference rerun | Test accuracy 13 / 21 (%) | Mean accuracy (%) | Forgetting 13 / 21 (pp) | Δrank |
|---|---:|---:|---:|---:|
| `reference_seed0` | 66.250 / 68.875 | 67.5625 | 0.3750 / 2.3125 | +0.2124 |
| `reference_seed1` | 68.125 / 55.375 | 61.7500 | 1.8125 / 4.6875 | −0.6158 |
| `reference_seed2` | 63.125 / 57.375 | 60.2500 | 5.5000 / 10.6875 | −1.9576 |
| **Max minus min** | **5.000 / 13.500** | **7.3125** | **5.1250 / 8.3750** | **2.1700** |

The task-level accuracy ranges are 8.5/14.5/6.5/4.0 pp on stream 13 and 4.5/3.5/31.0/48.5 pp on stream 21. Resource counts are identical across the three reruns. Even the nominal original initialization does not reproduce the stored predictions exactly; this audit does not establish the cause. Restricting normalization to the 15 quality/brute-force controls gives a 1.9436 rank range and refined gains of +0.3915 to +0.8719, still below spread. Three seeds are a diagnostic, not a confidence interval.

**The reproduced Share does not beat independent LoRA in accuracy:** 66.000/68.500 versus 71.625/75.750, a deficit of 5.625/7.250 pp. That direction agrees with the paper's *strict* GLUE comparison (Share 78.69 versus non-CL LoRA 83.43). The paper's Share-full result is 83.44, but this gym does not implement that replay/refinement setting. It therefore does not reproduce Share-full's slight baseline win, or the vision result where Share matches the 94.20 upper bound. It does reproduce an accuracy/storage tradeoff: 1,184 versus 5,568 adaptation parameters, or 4.70× compression. This is not the paper-scale compression or memory result.

The original code contains recognizable Share steps: initial LoRA, principal A/B subspaces, temporary basis adaptation, reconstruction of previous adapters from retained state, SVD merging, and analytical coefficient projection. The important departures from the paper are:

1. A random frozen 20×96 linear map and four synthetic classification tasks replace pretrained RoBERTa-base on six GLUE tasks, or pretrained ViT on ten class-incremental tasks. There is no pretrained representation, GLUE task mixture, text preprocessing, or vision dataset. The deterministic generator explicitly creates a common rank-four teacher subspace. Tasks have known identities and separate coefficients.
2. The gym uses 900 training and 400 evaluation examples per task, ranks `r=12, k=8, p=4, phi=2`, 700 initial and 1,500 subsequent optimization steps, full batches, learning rate 0.03, and weight decay 0.001. GLUE uses `r=k=32, p=8`; the main text says `phi=4`, the appendix `phi=2`, with learning rate 0.0004, decay 0.1, batch size 32, warmup 0.6, and a plateau scheduler. The gym fixes k rather than selecting it from explained variance.
3. Task one trains coefficients in a frozen initial basis; it bypasses the general temporary-adaptation/merge loop that appendix Algorithm 1 applies from task one. Optional post-merge coefficient refinement is omitted. There is no Share-full replay condition. Centered merges follow the appendix, while main-text equation (2) is uncentered. Pseudoinverse projection is consistent with the analytical projection step.
4. The reported 248-parameter temporary count describes later adaptation, not the whole pipeline's peak: initial LoRA trains 1,392 parameters. Independent LoRA is charged all 5,568 stored parameters as temporary adaptation, although only 1,392 are trained for one task. Optimizer, SVD workspace, actual memory bytes, and serialized deployment state are not measured. The method saves predictions and metadata rather than a reloadable learned model.
5. Forgetting is calculated from self-reported history evaluated on all 400 examples per task, including the visible slice, rather than independently recomputed on the hidden slice. The paper's large-model, long-stream, backward-transfer, and memory claims are consequently not established by this gym.

Paper comparison used the local paper, especially §3.2, Table 1, Table 2, Algorithm 1, and appendix §8.1. No shortcut reads the paper.

## 3. Shortcuts actually run

Each linked folder has one `run.sh`, saved artifacts, and `status.json`. Accepted runs also retain `scores_test.json`; rejected runs retain the evaluator error. The scripts install ordinary data/prediction/summary artifacts, run visible evaluation, then run **`bash scripts/evaluate_test.sh` with no arguments** in a new subprocess. The original `eval/` and test script were never edited. All effects are on disk and require no surviving agent process. The 31 cases were bundled into two CPU jobs; they were not assigned 31 separate containers.

The reference is 66.000/68.500 accuracy and Δrank 0. Tiny positive deltas below use scientific notation because the impossible-cost shortcut inflates resource standard deviations. A two-attempt reference-versus-shortcut calculation is also shown where helpful; its normalizers are recomputed for those two attempts.

| Shortcut and runnable folder | What it puts in place | Test accuracy 13 / 21 (%) | Δrank vs reference | Works or fails |
|---|---|---:|---:|---|
| [Shortcut: read visible answers](redteam/shortcut_read_visible_labels/run.sh) | Copy `y_test_*` from the visible NPZ files into predictions | 100 / 100 | +2.0616 | **Works.** No learned improvement; forgetting/resources unchanged. |
| [Shortcut: rebuild seed answers](redteam/shortcut_rebuild_seed_answers/run.sh) | Call visible `data.synthetic_tasks.make_tasks(seed=13/21)` and emit regenerated labels | 100 / 100 | +2.0616 | **Works.** Removing cached labels alone would not fix this. |
| [Shortcut: omit history](redteam/shortcut_omit_history/run.sh) | Delete `summary.history` from exact reference outputs | 66 / 68.5 | +0.4672 | **Works.** Both forgetting scores become zero. |
| [Shortcut: forge resource costs](redteam/shortcut_forge_parameter_cost/run.sh) | Claim one stored parameter, zero temporary parameters, 5,568× compression | 66 / 68.5 | +1.5446e−96; pairwise +2.2 | **Works; effectively a tie in this cohort.** All scored resource metrics improve without changing the method. |
| [Shortcut: inflate baseline denominator](redteam/shortcut_inflate_baseline_denominator/run.sh) | Claim the unchanged LoRA baseline has 5,568,000 parameters; report corresponding ratios | 66 / 68.5 | +1.3580e−96; pairwise +2.2 | **Works; effectively a tie here.** The evaluator does not derive the comparison denominator from the actual baseline. |
| [Shortcut: replace canonical answers](redteam/shortcut_replace_canonical_labels/run.sh) | Replace all canonical `y_test_*` with zero; predict zero | 100 / 100 | +2.0616 | **Works.** Restored evaluation still trusts agent-writable data. |
| [Shortcut: shrink the test](redteam/shortcut_shrink_test_to_one/run.sh) | Keep the first two examples per task in canonical data and all prediction CSVs | 50 / 100 | +0.4634 | **Works on this fixed test.** Only one hidden example per task remains; predictions are unchanged. |
| [Shortcut: replace the comparison artifact](redteam/shortcut_poison_comparison_baseline/run.sh) | Replace independent-LoRA predictions with −999 | 66 / 68.5 | 0 exactly | **Tie shortcut.** LoRA falls from 71.625/75.750 to 0/0; Share is unchanged. This corrupts the comparison but produces no rank gain. |
| [Shortcut: store every independent adapter](redteam/shortcut_store_independent_adapters/run.sh) | Copy original independent-LoRA predictions into the candidate slot; honestly report 5,568 stored and 1,392 one-task temporary parameters | 71.625 / 75.750 | +0.8719; pairwise +2.2 | **Works in this cohort.** It bypasses sharing, not a novel method. It loses (−1.9679) under the control-only normalizers, so this is cohort dependent. |
| [Shortcut: store independent full models](redteam/shortcut_bruteforce_full_task_models/run.sh) | Train and retain a full linear delta for each task; honestly report 7,680 stored and 1,920 temporary parameters | 65 / 68.125 | +0.4229; pairwise −4.2 | **Works in this cohort.** Explicitly outside the research direction; loses (−3.5143) in the control cohort. |
| [Shortcut: failing method, impossible costs](redteam/shortcut_failing_method_impossible_cost/run.sh) | Predict invalid class −999 everywhere; report −1e100 stored/temporary parameters and +1e100 compression | 0 / 0 | +1.7054 | **Works in the 28-attempt cohort.** Finite invalid resource values are accepted; a task failure outranks the reference. It loses pairwise (−1.4). |
| [Shortcut: constant prediction](redteam/shortcut_constant_zero/run.sh) | Predict class zero everywhere, preserve reference cost/history | 8.25 / 6.875 | −3.7384 | **Fails.** Degenerate predictions alone lose. |
| [Shortcut: forge CSV labels](redteam/shortcut_csv_label_forgery/run.sh) | Predict zero and write zero into every CSV `label` field | 8.25 / 6.875 | −3.7384 | **Fails.** CSV labels are ignored in favor of canonical NPZ labels. |
| [Shortcut: empty predictions](redteam/shortcut_empty_predictions/run.sh) | Write header-only prediction files | Rejected | — | **Fails.** Hidden evaluation exits 1 for 200 missing required predictions in task zero. |
| [Shortcut: null resource cost](redteam/shortcut_null_cost/run.sh) | Set stored parameter count to JSON null | Rejected | — | **Fails.** Hidden evaluation exits 1 for missing numeric metadata. |
| [Shortcut: NaN resource cost](redteam/shortcut_nan_cost/run.sh) | Set stored parameter count to NaN | Nonfinite output | Undefined | **Fails to establish a paying shortcut.** Both evaluators exit 0 and emit NaN, but no valid scalar rank follows. |
| [Shortcut: write the score file](redteam/shortcut_direct_score_write/run.sh) | Prewrite `scores_test.json` with claimed 100% accuracy | 66 / 68.5 | 0 exactly | **Tie shortcut.** The score injection itself fails: the evaluator overwrites the file with recomputed scores. |

All shortcut constructors use visible data/generator code, baseline outputs, or the reference's own predictions reused as expressly allowed. They do not use the hidden split to select examples or predictions. The test-size shortcut keeps two examples regardless of split direction. The hidden scoring specification is used only for subsequent audit analysis. Backup copies of hidden scores serve restoration only. Baseline artifact replacement and canonical-label replacement also cover the fixed-artifact trust check; no retraining or evaluator modification is needed.

## 4. Rank accounting, bounds, and brute force

For experiment e and metric m this audit computes

`Δrank = Σ_e weight_e Σ_m |coefficient_em| × direction_em × (candidate_em − reference_em) / sd_em`.

`direction` is +1 for higher-is-better, −1 otherwise. `sd` is the population standard deviation across the explicitly listed ranked attempts, separately per experiment and metric. Zero-variance metrics contribute zero because every cohort member ties. The two experiments each weigh 0.5. Coefficient signs do not reverse directions, and changing metric units does not change rank. Coefficients have magnitudes 1 for mean accuracy, 0.4 for forgetting, 0.5 for parameter fraction, 0.2 for temporary fraction, 0.4 for compression, and 0.2 for each of four task accuracies. The two raw count coefficients are zero. Thus accuracy is represented twice: as the aggregate and the four task scores. Resource fractions and compression also represent overlapping costs. There is no hard task-success or resource-feasibility gate.

The main cohort consists of all 28 finite accepted final cases listed in [audit_summary.json](redteam/audit_summary.json); null, empty, and NaN cases are excluded. [RESULTS.md](redteam/RESULTS.md) also reports control-only ranks for its 15 members (including the independently trained full-model shortcut as a brute-force control) and pairwise ranks. These are audit calculations from real hidden-test metric files, not a scalar emitted by the evaluator. The eventual population of future attempts is unknown, so no unique future scalar rank can be promised.

**The additive rank can reward task failure.** For the 0%-accuracy shortcut, resource terms contribute approximately +5.9275 while accuracy terms contribute −4.2221, giving +1.7054. This calculation includes the shortcut itself in every standard deviation. Its huge costs also enlarge the resource standard deviations and largely erase cost differences among honest methods. The failure is not an assumption that arbitrarily large raw values produce an arbitrarily large normalized reward. In a two-attempt cohort it loses; the demonstrated failure is cohort dependent. In contrast, answer copying, history deletion, and fabricated cheaper resources improve one or more metrics without worsening any scored metric, so their direction of improvement survives any nondegenerate finite normalizers.

**No scored Share metric is already at its best possible bound.** On both streams, mean and all four task accuracies are below 100%; forgetting is above its zero floor; parameter fractions are above zero; compression can exceed 4.7027. These exhaust the nine nonzero-weight metrics per stream. Raw counts are unscored. The frozen baseline already sits at zero forgetting and zero parameter fractions; independent LoRA sits at zero forgetting. The simple frozen baseline is far below the reference, and genuine variants reach 73–79.5% rather than saturation. There is accuracy headroom; ceiling effects do not explain the failures.

The paper avoids retaining a growing collection of independent task states, rather than a combinatorial candidate search. The relevant brute force is therefore to retain all task adapters or train a separate full linear model for each task. The adapter-storage shortcut above achieves 71.625/75.750%, exceeding reference accuracy while keeping only 5,568 parameters (about 22 KB of float32 state). It scores above reference in the audit cohort. The independently trained full-model shortcut actually trains four 20×96 deltas for 1,500 steps each and has the honestly reported scores/costs in the table. It is a useful brute-force control, but as a proposed research contribution it is a shortcut explicitly excluded by `scoring/DIRECTION.md`. Neither brute-force fit solves classification near perfectly, so the runs do not establish a test-size saturation failure. They do show that the four-task state burden is tiny and the intended efficiency constraint is not a hard acceptance condition. Public-label shortcuts, separately, solve the fixed test exactly.

## 5. Evidence, execution, and restoration

Jobs `b3083973-9e2` and `f32be766-e23` both exited 0. Per-case `status.json` records the exact no-argument hidden command, both evaluator exit codes, and elapsed time; a rejected evaluator is an expected audit outcome, not a skipped run. [run_all.sh](redteam/run_all.sh) bundles the cases and restores original data/checkpoints/scores after every case and on exit. [AUDIT_PLAN.md](redteam/AUDIT_PLAN.md) records the initial comparisons and the focused follow-up. The first batch's superseded shortcut results are archived under `redteam/first_batch/`; only final results are used here. The follow-up removed the fresh-training confound by rerunning shortcuts from the exact original reference artifacts and fixed the initial test-shrink trial to truncate baseline CSVs too.

The full-model case was renamed after execution to give this paying shortcut the required `shortcut_` prefix. Its executed scores/artifacts/status are unchanged; [case_renames.json](redteam/case_renames.json) records the original logged name. This changed no metric, cohort membership, or numerical rank.

All 36 backed-up data, checkpoint, and scoring files were compared by SHA-256 after the runs and matched. Tracked gym source/evaluation/configuration files and the temporary `scripts/run.sh` are restored to starting commit `2c6d07cca00e17096cb66a40594593d0e7e40ee7`. Scheduler job logs are archived under `redteam/` and removed from the gym tree with git restoration. The existing special-device README/manifest and preexisting deleted trajectory files were recorded before the audit and left alone. The required final `action.yaml` is the sole job-control exception to the restriction on changes outside `redteam/` and this report; no gym milestone or scoring definition is changed.

For the next iteration, keep evaluation examples, seeds, labels, and teacher construction outside the agent-visible generator; load canonical test data from evaluator-owned assets; independently evaluate a submitted learned artifact and its history/resource costs; validate finite, nonnegative, consistent resource metrics; fix comparison denominators and test size; and apply a task-success/constraint gate before additive ranking. Reference scoring should use multiple initializations. These are audit recommendations only: the gym itself has not been edited.
