# Hardening record

Final validation is prepared as one batched CPU job. Numerical tables will be finalized from `redteam/hardening/final/` after that job completes. This record supersedes the old prediction/summary-based descriptions in the historical progress log.

## Scope and scientific fidelity

The paper is *Shared LoRA Subspaces for almost Strict Continual Learning*, §3.2, Algorithm 1, Tables 1–2 and appendix §8.1. The implemented computation remains initial LoRA training, centered factor SVD, temporary top-direction adaptation, reconstruction of past adapters from retained state, SVD merging, analytical projection, and current-task-only coefficient refinement. It does not replay old data. The reference uses the appendix's two temporary directions and centered merges; four directions are the paper's main-text setting and an honest comparison. The appendix and main-text merge equations differ; the uncentered comparison preserves centered initialization.

This is a synthetic scaling of that computation, not a reproduction of RoBERTa/GLUE, ViT/CIFAR or the other modalities. The base is a frozen random 20×96 map, not a pretrained representation. Settings remain r=12, k=8, p=4, full-batch AdamW (0.03, decay 0.001), 700 initialization steps, 1500 adaptation steps and 700 current-task coefficient-refinement steps. Initial-task coefficient fitting remains a special case rather than a separate temporary-adaptation/merge pass. The reference does not reproduce the paper's optimizer schedule, explained-variance rank selection, full-model memory figures, or relaxed Share-full setting. No such results are claimed.

The original four-task, exposed-answer benchmark has been replaced by six- and ten-task streams: six and four hidden streams respectively, 1000 held-out examples per task, 76,000 test examples total. Three independent development streams follow the same generator and preprocessing, with 500 validation examples per task. Separate public and private RNG components keep hidden teachers, held-out inputs, labels, noise, and their regenerating code exclusively in `eval/test/`. The tracked manifest contains only public seeds, training labels and development validation labels.

## Defenses and ranking

- The evaluator applies raw deployed-state arrays to its own base weights and inputs; it recomputes accuracy, forgetting and stored scalar counts. Prediction CSVs, summaries, resource claims, score files and method-written verdicts have no authority.
- Every task snapshot is required. All arrays must be real, finite, correctly shaped and named. Noncanonical snapshot names and excessive expanded archives fail. Overflowing reconstructed updates or logits fail.
- Evaluator-owned dimensions, input counts, labels, resource denominator (one rank-12 adapter per task), budgets (1392 shared values, 139 per task), 40% success floor, reference metrics and baseline context cannot be changed through a method's artifacts. Visible evaluation has its own frozen manifest and loader. Train and test share no implementation or data-loader imports.
- Failure in either required experiment fails the entire attempt: both experiments receive accuracy 0, forgetting 100, parameter fraction 1. Every passing attempt dominates this scored vector, regardless of cohort normalization.
- Ranking adds `weight × abs(coefficient) × direction × (value − fixed reference) / population sd` over the methods on disk plus the fixed reference anchor. Zero-variance metrics contribute zero. Actual ranks and normalizers are emitted in `_metadata.ranking`. Coefficient signs cannot reverse the stated better direction.
- Accuracy is scored once (coefficient 1), forgetting once (0.2), and deployed parameter fraction once (0.4), with experiment weights 0.5 each. The original rubric double-counted accuracy through per-task scores and storage through fractions and inverse compression, and trusted temporary training costs. Removing overlapping rewards keeps the scientific quantities independent; temporary training costs are no longer claimed as measured. Paper values are unchanged in `_paper_reported`; scaled results are labelled as reproduced measurements.

## Shortcuts left to the separate attempt review

A static artifact scorer cannot prove training chronology without executing training. Backdating a later deployed state into earlier snapshots can erase measured forgetting; joint training/replay can produce a compact, high-accuracy state. Both are forbidden in `scoring/CONSTRAINTS.md` and `scoring/DIRECTION.md`, explicitly demonstrated in the audit, and left to the separate shortcut grader. This is a remaining limitation, not a claim that those attacks are fixed. Rejecting every constant shared basis would also reject honest fixed-representation methods.

An independent low-rank method that actually fits the counted budget is an honest alternative, not a loophole. The packed independent control is retained to check that such a method is below the reference. Full independent rank-12 adapters or full task matrices exceed the budget and fail. Copying the exact reference state is inherently indistinguishable from reproducing that state; ignoring forged metadata cannot detect such copying and awards no improvement.

No defenses depend on leftover processes, interpreter modification, elapsed time or wall-clock performance. The hidden test performs inference and metric arithmetic only, never retraining.

## Validation plan

All fixes were selected before the final job. It reruns the reference and official baselines from final training code, rescores the saved better/weaker variants without retraining, exercises the repaired shortcuts together, poisons public answers/test size/dimensions, checks no-argument scoring and score-file overwrite, independently checks every rank term and failure ordering, and runs `python validate.py --post-design --compare`. Canonical score files are then regenerated from only the reference method and official baseline runs. Full audit scores remain under `redteam/`, separate from the gym reference.
