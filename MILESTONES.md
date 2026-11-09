# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

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

### [2026-11-09] - core_claim_plus
- Final training batch reran the actual Share procedure, including current-task coefficient refinement, and all four official baselines on six- and ten-task streams.
- Reference hidden accuracy is 71.34% / 64.83%, with 6.37x / 8.88x deployed-state compression against independent LoRA. This is a synthetic scaled accuracy/storage result, not the paper-scale model results.
- Added longer-stream headroom, independent hidden inputs/answers, raw-state inference, evaluator-owned comparisons, storage/task success gates and cohort-normalized ranking.
- Successful final audit job `d9180772-7d8` checked 38 cases and passed `validate.py --post-design --compare`. Better variants exceed measured reference seed variation; weaker controls score lower.
- Residual snapshot chronology/replay shortcuts and development/test calibration limits are quantified in HARDENING.md. Canonical scores contain only fresh reference and official baseline runs.

## Stop Justification
- Completed at milestone `core_claim_plus`.
