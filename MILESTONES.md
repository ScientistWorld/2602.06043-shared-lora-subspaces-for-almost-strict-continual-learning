# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-06-13 00:00] - core_claim_plus
- Audit confirmed the existing implementation is the paper's Share procedure at scaled linear-layer scope, not a surrogate: it trains LoRA factors, extracts SVD bases, adapts temporary basis directions, recomputes the shared basis, and projects coefficients analytically.
- Added a second deterministic continual stream (`synthetic_continual_low_rank_seed21`) to test the same benefit/constraint metrics beyond the selected seed-13 stream.
- Submitting an expanded reproduction job; `core_claim_plus` should only be considered reached if that job completes and writes seed-21 scores.

### [2026-06-13 00:00] - core_claim
- Implemented Share's LoRA-factor SVD initialization, temporary basis adaptation, SVD merge, and analytical coefficient reprojection on a scaled continual low-rank benchmark.
- Reproduced the core performance/efficiency tradeoff: Share reaches 68.63% final average accuracy versus 75.31% for independent LoRA and 8.88% for a frozen backbone, while using 1184 parameters versus 5568 for the independent LoRA stream.
- Evaluation reports both benefit and constraint metrics: final/per-task accuracy, average forgetting, parameter fraction, and compression ratio.

## Stop Justification
- Not stopping; submitting an expanded two-stream reproduction job.
