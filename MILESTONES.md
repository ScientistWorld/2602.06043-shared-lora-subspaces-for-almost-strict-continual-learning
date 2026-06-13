# Reproduction Milestones

**Current: method_runs**

## Progress Log

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
