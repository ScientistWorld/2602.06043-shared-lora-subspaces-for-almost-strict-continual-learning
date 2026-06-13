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

- CPU smoke job `123ece10-17b` completed successfully.
- Scaled initial run: Share final average accuracy 86.50%, independent LoRA 91.80%, frozen backbone 29.30%.
- Share used 184 trainable/stored parameters versus 720 for the independent LoRA stream in the initial small configuration.
- CPU test job `1da339f3-80d` completed successfully on the enlarged benchmark and passed `validate.py --compare`.
- Enlarged benchmark result: Share 47.75% average accuracy, independent LoRA 75.31%, frozen backbone 8.88%.
- The enlarged result demonstrates the method runs and improves over a frozen backbone under a 10.55x parameter compression, but it is not yet strong enough to claim the core paper claim of LoRA-like performance under compression.

## What Remains

- Rerun the enlarged benchmark with a wider retained Share subspace (`k=8`) while preserving a meaningful compression constraint.
- If Share approaches independent LoRA while remaining substantially smaller, mark `core_claim` for the scaled reproduction.
- Future expansion should target Table 1 GLUE with RoBERTa-base using the same Share implementation pattern.

## Issues Encountered

- Initial scaffold was template-only.
- A sidecar inspection agent set `action.yaml` to `done`; this turn restores it to a job submission before ending.
