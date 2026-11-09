# Overview

- **Paper ID:** 2602.06043
- **Title:** Shared LoRA Subspaces for almost Strict Continual Learning
- **Domain:** Parameter-efficient continual learning
- **TL;DR:** Share continually updates a shared low-rank adapter subspace so a pretrained model can learn task streams with far less adapter storage and limited forgetting.

## Short Summary

The paper studies replay-free parameter-efficient continual finetuning for pretrained models. It proposes Share, which derives shared LoRA factor bases with SVD, trains small task coefficients and temporary basis directions for new tasks, then merges new knowledge by recomputing principal factors and reprojecting task coefficients analytically. Reported experiments cover GLUE, image classification, 3D pose estimation, text-to-image adaptation, and large collections of LoRA adapters.

## Reproduction Scope

This workspace implements the actual Share computation (LoRA initialisation, centered-SVD principal factors, temporary top-phi basis adaptation, SVD merge with analytical coefficient reprojection, and the merging-phase finetuning of the current task's coefficients on its own data) for a frozen linear classifier on a synthetic continual low-rank benchmark. Streams of 6 tasks (the paper's GLUE stream length) and 10 tasks (its image-classification stream length) share a hidden low-rank structure. The benchmark is scaled down from the paper's pretrained backbones but keeps its claim and its constraints: replay-free sequential learning, one compact shared state plus small per-task coefficients, measured accuracy, forgetting and storage. Methods submit their deployed state after every task. The evaluator rebuilds each task's weights, scores held-out examples of hidden streams, and counts the stored parameters itself.

---

# Problem Definition

## Research Question

How can a pretrained model be adapted to a sequence of new tasks while retaining earlier task performance, without replaying earlier task data, and while keeping the stored adaptation state small enough that it does not grow by a full adapter per task?

The benchmark problem is parameter-efficient continual finetuning. A solution receives the tasks of a stream one at a time. While learning task *t* it may use task *t*'s training data and whatever state it carried forward from tasks *0..t-1*; it may not revisit earlier tasks' data or look at later tasks. After every task the solution has a deployed state that must serve every task seen so far, and after the last task it is evaluated on all tasks of the stream.

## The Benchmark

Each *stream* consists of a frozen base linear classifier `W0` (20 classes x 96 input features) and an ordered sequence of related classification tasks (6 or 10 tasks per stream). Each task has 900 labelled training examples and its own input distribution. Tasks of a stream are related, but each needs its own update of the frozen weights to be solved well; the frozen classifier alone is close to chance.

A solution adapts `W0` by a low-rank weight update per task, `W_t = W0 + L_t R_t^T`, where the factors may be built from state shared by all tasks of the stream and state specific to each task. Deployed state is limited the way an almost-strict continual learner must be: the shared part may be at most the size of one rank-12 adapter (12 x (20 + 96) = 1392 parameters) and each task may add at most 139 parameters (10% of one adapter). Storing a separate full-size adapter or a dense weight update for every task does not fit.

Development streams come with a labelled validation split for each task. The scored streams provide only training data; their held-out examples are never visible.

## Why It Matters

Real deployments need to keep adapting large pretrained models as new domains and users arrive. Storing and serving a separate adaptation per task grows without bound and shares no knowledge across tasks; fine-tuning one shared adaptation sequentially forgets earlier tasks. A good solution lets one compact deployed state keep improving over a long task stream.

## Success Criteria

A good solution reaches high final accuracy on every task of every stream after the whole stream has been learned, forgets little of what it once knew, and stays well inside the storage budget. Accuracy alone is not enough: storage cost and forgetting are measured from the deployed state itself.

---

# Paper's Method

## Key Contribution

Share proposes a replay-free, parameter-efficient continual finetuning method that maintains one evolving shared low-rank subspace instead of storing an independent LoRA adapter for every task. The method targets almost strict continual learning: no past task data replay, no growing set of deployed adapters, and minimal parameter growth.

## Approach

Share starts from one or more LoRA adapters, or from an adapter trained on the first task, and forms shared principal factors for the LoRA A and B matrices. For each layer, task adapters are stacked, centered, and decomposed with SVD. The top shared directions become frozen basis factors, while lightweight task coefficients are trained.

When new task data arrives, Share temporarily expands with a small number of basis directions initialized from the existing subspace and trains those temporary factors and coefficients on the current task. When a new adapter arrives directly, it can be merged without data. The merge step reconstructs previously represented adapters, stacks them with the new information, recomputes the shared basis with truncated SVD, and analytically updates coefficients using projection or pseudoinverse operations. In the same merging & fine-tuning phase the current task's coefficients are then optimised on the current task's data (Algorithm 1, lines 40-41); earlier tasks' coefficients are only recalculated analytically. The relaxed Share-full setting additionally finetunes earlier tasks' coefficients with access to their data, which breaks the replay-free condition.

## Main Claims

The primary claim is that a single continually updated shared low-rank representation can retain task performance close to separate-adapter or joint-training references while using orders of magnitude fewer trainable and stored parameters.

Secondary claims are that the same mechanism works across language, image classification, 3D pose estimation, and generative-model settings; that the shared subspace can support forward and sometimes backward transfer; and that storage savings grow as the number of tasks increases because the deployed representation does not require one full adapter per task.

---

# Evaluation

## What a Method Submits

A run is a directory `checkpoints/<method_name>/`. For every stream listed in `data/streams/manifest.json` it holds one snapshot of the deployed state after each task, in stream order:

```
checkpoints/<method_name>/<stream_id>/after_task_00.npz
checkpoints/<method_name>/<stream_id>/after_task_01.npz
...
```

Each snapshot is an `.npz` of real-valued 2-D arrays with these names only:

| Array | Shape | Meaning |
|---|---|---|
| `shared_A` (optional) | 96 x kA | shared input-side factor |
| `shared_B` (optional) | 20 x kB | shared output-side factor |
| `task_<j>_A` | kA x p_j (or 96 x p_j without `shared_A`) | task *j*'s input-side coefficients |
| `task_<j>_B` | kB x p_j (or 20 x p_j without `shared_B`) | task *j*'s output-side coefficients |

The weight update for task *j* is `L_j R_j^T` with `R_j = shared_A @ task_j_A` and `L_j = shared_B @ task_j_B`. A missing shared factor stands for the identity. If task *j* has no arrays, the shared factors are used directly, which requires kA = kB. If there is no state at all, the update is zero. A snapshot taken after task *t* may hold task arrays only for tasks *0..t*. `data/streams.py` provides `load_stream` and `save_snapshot`. Nothing else in the run directory is read: no self-reported costs, predictions or scores.

## Metrics

The evaluator rebuilds every task's weights from the snapshots, runs the frozen classifier plus update on that task's evaluation examples, and computes:

- `final_average_accuracy` (higher is better, primary): accuracy (%) of the state deployed after the last task, averaged over all tasks of the stream, then over streams.
- `average_forgetting` (lower is better): for each task except the last, the drop from its best accuracy across the snapshots taken after it was learned to its final accuracy, averaged over tasks and then streams (percentage points).
- `parameter_fraction_vs_lora_stream` (lower is better): number of values in the final snapshot divided by the cost of storing one rank-12 adapter per task, `T x 12 x (20 + 96)`. The denominator is fixed by the evaluator.
- Reported but not scored: `compression_ratio_vs_lora_stream` (the inverse of the parameter fraction), `stored_parameters`, `worst_task_accuracy`.

## Constraints and Failure

A run fails the entire attempt, and receives bounded worst values in both experiments (accuracy 0, forgetting 100, parameter fraction 1), if any of the following holds:

- a snapshot is missing or malformed, or contains NaN, infinite or overflowing values;
- any snapshot's shared arrays exceed 1392 values, or any task's arrays exceed 139 values;
- its final average accuracy is below 40%, meaning the task is not solved.

## Experiments and Splits

- `continual_6task_stream`: streams of 6 tasks.
- `continual_10task_stream`: streams of 10 tasks.

The visible evaluation (`bash scripts/evaluate_train.sh`, or `bash scripts/evaluate.sh`) scores the development streams on their labelled validation splits. The hidden test scores separate streams (6 six-task and 4 ten-task streams), whose training data is in the manifest, on 1,000 held-out examples per task that only the hidden evaluator can produce. Both use the same interface, rules and metrics. Evaluation data, labels, base weights, dimensions and test size are fixed within each evaluator, independently of the method's data files.

The rank is `sum_e weight_e sum_m abs(coefficient_em) * direction_em * (metric_em - reference_em) / sd_em`. Direction is +1 for higher-is-better and -1 otherwise. Each `sd` is the population standard deviation across all methods currently scored plus the fixed reference anchor; a constant metric contributes zero. The evaluator owns the reference metric vector and the ranking specification, matching the coefficients in `scoring/reference.json`. The computed ranks and normalizers are in `_metadata.ranking`. A failure in either experiment replaces the scored metrics in both with the worst values, so every successful attempt outranks every failed attempt. Scalar magnitudes depend on the cohort; the reference always has improvement zero.

The hard resource denominator does not depend on any baseline submission. Fixed baseline measurements are also retained in evaluator-owned comparison data. Changing a baseline's artifacts changes its own result only.

Snapshots let the evaluator recompute forgetting, but do not prove when an artifact was written or which training data was used. The separate attempt review must enforce the replay, look-ahead and snapshot chronology rules. Published resource scores measure deployed values, not training memory or peak trainable parameters.

## Baselines

- `frozen_backbone`: no update.
- `sequential_lora`: one rank-12 adapter fine-tuned through the stream.
- `independent_rank1`: a separate rank-1 adapter per task.
- `independent_lora`: a separate rank-12 adapter per task. This is the non-continual reference. It exceeds the per-task budget, so it scores as failed; its measured accuracy is listed in the score file's `_metadata.failed_runs`.

## Protocol

Learn the tasks of each stream in order, using only the current task's training data and the state carried forward. Produce snapshots as you go: the snapshot after task *t* must be the state that was actually deployed after task *t*. Use the same frozen `W0` and inputs for every method.

---

# Reproduction Log

### Iteration 1: gpt-5.5
- **Milestone**: `core_claim` | **Status**: done
- **Working time**: 17m | **GPU**: 0.0h
- **Jobs**: 6 total (6 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 00:00] - none
- Read the paper and identified Share's required algorithmic steps: LoRA factor SVD initialization, temporary basis adaptation, SVD merge, and analytical coefficient reprojection.
- Implemented a scaled deterministic continual low-rank benchmark and runnable Share/LoRA/frozen pipelines.

### [2026-06-13 19:12] - method_runs
- CPU test job `123ece10-17b` ran the Share method, independent LoRA baseline, frozen baseline, evaluator, and validator end-to-end.
- Initial scaled scores: Share 86.50% average accuracy, independent LoRA 91.80%, frozen backbone 29.30%.

### [2026-06-13 19:13] - method_runs
- CPU test job `1da339f3-80d` reran the enlarged benchmark and passed validation.
- Enlarged scores: Share 47.75% average accuracy, independent LoRA 75.31%, frozen backbone 8.88%, with 10.55x compression versus the LoRA stream.
- Kept the milestone at `method_runs` because Share is still too far below independent LoRA on this stricter setting.

### [2026-06-13 19:23] - method_runs
- CPU test job `d7e7f5b1-9fb` reran the enlarged benchmark with `k=8` and passed validation.
- Scores improved modestly: Share 50.56% average accuracy, independent LoRA 75.31%, frozen backbone 8.88%, with 5.27x compression versus the LoRA stream.
- Kept the milestone at `method_runs`; the next run increases pseudo-rank to test whether per-task rank was the bottleneck.

### [2026-06-13 19:26] - method_runs
- CPU test job `9fc78eed-b55` reran the enlarged benchmark with `p=4` and passed validation.
- Scores moved close to the target tradeoff: Share 68.63% average accuracy, independent LoRA 75.31%, frozen backbone 8.88%, with 4.70x compression versus the LoRA stream.
- Kept the milestone at `method_runs` for one more capacity test with `p=6`; `p=4` is close but still leaves a 6.69 point gap to independent LoRA.

### [2026-06-13 19:29] - method_runs
- CPU test job `02054de3-b85` reran the enlarged benchmark with `p=6` and passed validation.
- Scores regressed: Share 65.75% average accuracy, independent LoRA 75.31%, frozen backbone 8.88%, with 4.24x compression versus the LoRA stream.
- Reverted the default to the stronger `p=4` setting and queued a final selected-configuration rerun before milestone promotion.

### [2026-06-13 19:31] - core_claim
- CPU test job `86ee5401-88b` reran the selected `k=8`, `p=4` configuration and passed validation.
- Final selected scores: Share 68.63% average accuracy, independent LoRA 75.31%, frozen backbone 8.88%.
- Share used 1184 parameters versus 5568 for the independent LoRA stream, a 4.70x compression ratio, reproducing the paper's core accuracy/parameter-efficiency tradeoff on the scaled benchmark.

</details>

### Iteration 2: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 7 total (7 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 00:00] - core_claim_plus
- Audit confirmed the existing implementation is the paper's Share procedure at scaled linear-layer scope, not a surrogate: it trains LoRA factors, extracts SVD bases, adapts temporary basis directions, recomputes the shared basis, and projects coefficients analytically.
- Added a second deterministic continual stream (`synthetic_continual_low_rank_seed21`) to test the same benefit/constraint metrics beyond the selected seed-13 stream.
- Job `61982c19-66d` completed successfully and wrote seed-21 scores: Share 67.31% final average accuracy versus 75.06% independent LoRA and 7.94% frozen backbone, with the same 4.70x compression ratio.

### [2026-06-13 00:00] - core_claim
- Implemented Share's LoRA-factor SVD initialization, temporary basis adaptation, SVD merge, and analytical coefficient reprojection on a scaled continual low-rank benchmark.
- Reproduced the core performance/efficiency tradeoff: Share reaches 68.63% final average accuracy versus 75.31% for independent LoRA and 8.88% for a frozen backbone, while using 1184 parameters versus 5568 for the independent LoRA stream.
- Evaluation reports both benefit and constraint metrics: final/per-task accuracy, average forgetting, parameter fraction, and compression ratio.

</details>

### Iteration 3: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 8m | **GPU**: 0.0h
- **Jobs**: 8 total (8 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

</details>

### Iteration 4: gpt-5.5 (designer_stage_1)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 8 total (8 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

</details>

### Iteration 5: gpt-5.5 (designer_stage_2)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 8 total (8 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

</details>

### Iteration 6: gpt-5.5 (designer_stage_3)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h
- **Jobs**: 11 total (10 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

</details>

### Iteration 7: gpt-5.5 (packager)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 3m | **GPU**: 0.0h
- **Jobs**: 11 total (10 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

</details>

### Iteration 8: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

### [2026-06-13 20:20] - core_claim_plus
- Regenerated `scoring/scores.json` from existing prediction artifacts to include the declared temporary-parameter constraint metrics.
- `python validate.py --compare` passes after the final packaging audit.

</details>

### Iteration 9: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

### [2026-06-13 20:20] - core_claim_plus
- Regenerated `scoring/scores.json` from existing prediction artifacts to include the declared temporary-parameter constraint metrics.
- `python validate.py --compare` passes after the final packaging audit.

</details>

### Iteration 10: gpt-6.1-sol (redteam)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 9m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

### [2026-06-13 20:20] - core_claim_plus
- Regenerated `scoring/scores.json` from existing prediction artifacts to include the declared temporary-parameter constraint metrics.
- `python validate.py --compare` passes after the final packaging audit.

</details>

### Iteration 11: claude-opus-5-5 (hardener)
- **Milestone**: `core_claim_plus` | **Status**: error
- **Working time**: 30m | **GPU**: 0.0h
- **Jobs**: 2 total (2 completed, 0 failed)

<details>
<summary>Progress Log</summary>

### [2026-06-13 19:43] - none
- Started from an existing partial workspace and audited the paper, scripts, method code, evaluation code, and current scores.
- Confirmed the target paper is Share: SVD-derived shared LoRA subspaces for replay-free parameter-efficient continual finetuning.

### [2026-06-13 19:43] - method_runs
- `method/share_linear.py` implements the paper's actual core computation on a compact low-rank benchmark: LoRA initialization, centered SVD factor extraction, temporary factor adaptation, SVD merge, and analytical coefficient reprojection.
- `scripts/reproduce.sh` runs frozen, independent LoRA, and Share pipelines end-to-end and writes prediction artifacts for evaluation.

### [2026-06-13 19:43] - core_claim
- The default deterministic stream supports the core claim in a scaled setting: Share reaches 68.63% final average accuracy versus 8.88% for the frozen backbone, while using 1184 stored/trainable parameters versus 5568 for independent LoRA.
- The method-independent evaluator reports final accuracy, per-task accuracy, forgetting, parameter fraction, and compression ratio.

### [2026-06-13 19:43] - core_claim_plus
- Added and scored a second deterministic task stream (`synthetic_continual_low_rank_seed21`).
- Seed 21 reproduces the same comparison shape: Share reaches 67.31% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression versus the LoRA stream.

### [2026-06-13 19:55] - none
- Audit found the prior Share loop retained dense past task adapters during merging, which is not strict enough for the paper's shared-state procedure.
- Patched the method to reconstruct previous adapters from the current shared factors and coefficients before each SVD merge, then discard dense temporary merge factors.
- A fresh compute job is required before claiming `method_runs` or higher for the corrected implementation.

### [2026-06-13 19:49] - none
- Continuation audit confirmed `scoring/scores.json` and prediction summaries still predate the strict-merge patch.
- Kept the milestone below `method_runs` and prepared another CPU test submission to regenerate scores from the corrected implementation.

### [2026-06-13 19:51] - core_claim_plus
- CPU job `11ed4ca8-276` reran `scripts/reproduce.sh` from the corrected strict Share merge implementation and exited successfully.
- `validate.py --compare` passed: reference/scores structure is valid, `eval/` and `data/` remain independent of `method/`, and evaluation reads method artifacts rather than regenerating the method.
- Corrected default stream: Share reaches 68.25% final average accuracy versus 8.88% frozen and 75.31% independent LoRA, while using 1184 parameters versus 5568 for the LoRA stream (4.70x compression).
- Corrected seed-21 stream: Share reaches 67.56% final average accuracy versus 7.94% frozen and 75.06% independent LoRA, with the same 4.70x compression.

### [2026-06-13 20:20] - core_claim_plus
- Regenerated `scoring/scores.json` from existing prediction artifacts to include the declared temporary-parameter constraint metrics.
- `python validate.py --compare` passes after the final packaging audit.

</details>


---

# Reproduction Milestones

**Current: core_claim_plus**

## Stop Justification
- Completed at milestone `core_claim_plus`.
