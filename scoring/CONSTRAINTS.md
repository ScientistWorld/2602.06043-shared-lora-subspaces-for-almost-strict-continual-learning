# Scientist Constraints

## Data

- Use only the streams in `data/streams/manifest.json`, loaded through `data/streams.py`.
- While learning task *t* of a stream, use only task *t*'s training examples and the state carried forward from tasks *0..t-1*.
- Do not replay or re-read an earlier task's data. Do not look at a later task's data. Do not train jointly on several tasks of a stream.
- Never train on development-stream validation labels. They exist to measure progress.
- Do not use external data.

## Evaluation

- Score only through `scripts/evaluate.sh` / `scripts/evaluate_train.sh`. The hidden test runs `scripts/evaluate_test.sh` with no arguments.
- Do not modify `eval/`, the manifest, stream generation, the metric definitions or the budgets.
- The evaluator reads only the snapshot arrays. Self-reported numbers are ignored.

## Snapshots

- Write one snapshot after each task, in stream order (`after_task_00.npz`, `after_task_01.npz`, ...).
- The snapshot after task *t* must be the state the method actually deployed at that point. Do not back-date a later state into earlier snapshots or rewrite earlier snapshots afterwards: forgetting is measured from these snapshots.

## Resource Accounting

- Everything a deployed task depends on must be in the snapshot arrays. The evaluator counts every value.
- Shared arrays may hold at most 1392 values (one rank-12 adapter), and each task's arrays at most 139 values.
- The frozen base classifier is not counted. Nothing else may be stored outside the snapshot.

## Compliance Checklist

- [ ] Tasks learned strictly in order, each from its own training data and the carried state only (no replay, no look-ahead, no joint training)
- [ ] One genuine snapshot per task, written as the stream is learned
- [ ] All deployed state is in the snapshot arrays and within budget
- [ ] Scores produced by the provided evaluators, with no edits to `eval/` or `data/streams/`
