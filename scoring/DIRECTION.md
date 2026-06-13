# Research Direction

## Research Problem

The research problem is replay-free parameter-efficient continual adaptation. A method should learn a stream of tasks with small incremental parameter cost while preserving final performance on earlier tasks.

## Core Contribution

This benchmark is about shared low-rank structure across task adaptations. Valid improvements should still address how task-specific low-rank information is represented, merged, compressed, or reused across a task stream.

## Approach Scope

Methods may change the basis update rule, coefficient training, rank allocation, regularization, merge schedule, or analytical projection strategy. They may also add diagnostics or better parameter accounting, as long as the method remains a parameter-efficient continual adaptation method for the same task stream.

## Out of Bounds

Do not replace the problem with full independent models per task, external-data pretraining, test-set transduction, or a classifier that ignores the continual parameter-efficiency objective. A method that improves accuracy only by storing one full adapter or model per task without reporting that cost does not address the paper's research direction.
