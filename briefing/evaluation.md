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

A run fails an experiment, and receives bounded worst values for it (accuracy 0, forgetting 100, parameter fraction 1), if any of the following holds:

- a snapshot is missing or malformed, or contains NaN, infinite or overflowing values;
- any snapshot's shared arrays exceed 1392 values, or any task's arrays exceed 139 values;
- its final average accuracy is below 40%, meaning the task is not solved.

## Experiments and Splits

- `continual_6task_stream`: streams of 6 tasks.
- `continual_10task_stream`: streams of 10 tasks.

The visible evaluation (`bash scripts/evaluate_train.sh`, or `bash scripts/evaluate.sh`) scores the development streams on their labelled validation splits. The hidden test scores separate streams (6 six-task and 4 ten-task streams), whose training data is in the manifest, on 1,000 held-out examples per task that only the hidden evaluator can produce. Both use the same interface, rules and metrics. The rank combines each scored metric's improvement over the reference with weights from `scoring/reference.json`.

## Baselines

- `frozen_backbone`: no update.
- `sequential_lora`: one rank-12 adapter fine-tuned through the stream.
- `independent_rank1`: a separate rank-1 adapter per task.
- `independent_lora`: a separate rank-12 adapter per task. This is the non-continual reference. It exceeds the per-task budget, so it scores as failed; its measured accuracy is listed in the score file's `_metadata.failed_runs`.

## Protocol

Learn the tasks of each stream in order, using only the current task's training data and the state carried forward. Produce snapshots as you go: the snapshot after task *t* must be the state that was actually deployed after task *t*. Use the same frozen `W0` and inputs for every method.
