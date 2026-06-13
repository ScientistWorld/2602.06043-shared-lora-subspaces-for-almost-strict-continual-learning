# Progress

## What Works

- Paper analysis completed for the core Share algorithm and headline GLUE/image-classification claims.
- Implemented a compact scaled benchmark in `data/synthetic_tasks.py`.
- Implemented the paper's Share computation in `method/share_linear.py`.
- Implemented independent LoRA and frozen-backbone baselines in `baseline/lora_linear.py`.
- Implemented method-agnostic artifact evaluation in `eval/evaluate_predictions.py`.

## Deviations From Paper

- The first runnable reproduction uses a deterministic low-rank classification stream instead of RoBERTa-base on GLUE. This preserves the low-rank continual adaptation procedure while reducing setup and compute risk for the first job.
- The implementation uses one frozen linear layer instead of transformer layers. The Share algorithm is still applied to LoRA A/B factors with SVD factor extraction, temporary adaptation, merging, and coefficient reprojection.

## Results Achieved

- No compute job has completed yet. The next job runs frozen and independent LoRA baselines, Share, evaluation, and validation.

## What Remains

- Run the submitted job and inspect whether Share beats the frozen baseline while using a small fraction of independent-LoRA stream parameters.
- If successful, mark `method_runs`; if the effect is strong enough, update toward `core_claim`.
- Future expansion should target Table 1 GLUE with RoBERTa-base using the same Share implementation pattern.

## Issues Encountered

- Initial scaffold was template-only.
- A sidecar inspection agent set `action.yaml` to `done`; this turn restores it to a job submission before ending.
