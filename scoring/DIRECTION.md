# Research Direction

## Research Problem

The research problem is replay-free parameter-efficient continual adaptation. A method should learn a stream of tasks with small incremental parameter cost while preserving final performance on earlier tasks.

## Core Contribution

This benchmark is about compact reusable structure across task adaptations. Valid improvements should still address how task-specific adaptation information is represented, merged, compressed, or reused across a task stream.

## Approach Scope

Methods may change the representation update rule, adaptation training, capacity allocation, regularization, merge schedule, or compression strategy. They may also add diagnostics or better parameter accounting, as long as the method remains a parameter-efficient continual adaptation method for the same task stream.

## Out of Bounds

Do not replace the problem with full independent models per task, external-data pretraining, test-set transduction, or a classifier that ignores the continual parameter-efficiency objective. A method that improves accuracy only by storing one full task-specific state or model per task without reporting that cost does not address the paper's research direction.
