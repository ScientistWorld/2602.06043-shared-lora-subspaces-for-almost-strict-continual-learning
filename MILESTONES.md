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

## Stop Justification
- Stopped at `core_claim_plus`: the corrected strict Share implementation supports the scaled core claim on two deterministic continual streams. Higher milestones would require reproducing additional paper settings such as full RoBERTa-base GLUE or the vision/text-to-image extensions, which are outside the compact CPU reproduction completed here.
