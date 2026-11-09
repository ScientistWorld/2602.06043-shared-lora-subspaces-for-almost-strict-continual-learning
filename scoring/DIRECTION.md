# Research Direction

## Research Problem

Replay-free, parameter-efficient continual adaptation. A method learns a stream of tasks one at a time, adds only a small amount of stored state per task, and must keep performing on every earlier task without revisiting its data.

## Core Contribution

This benchmark is about compact reusable structure across task adaptations. Valid improvements change how the knowledge in each new task's adaptation is represented, integrated into the state carried forward, compressed or reused, so that the deployed state serves the whole stream better or more cheaply.

## Approach Scope

Methods may change any of these, as long as tasks are learned in order from their own data and the deployed state stays within the budget:

- the representation of shared and task-specific state;
- how each new task is learned on top of the carried state;
- how new information is merged into the shared state, and how earlier tasks' parts are kept consistent;
- capacity allocation, regularisation, initialisation, optimisation schedules and hyperparameters.

Better accounting or diagnostics are welcome.

## Out of Bounds

- Replay, joint or multi-task training over several tasks' data, and using a later task's data before that task arrives.
- Back-dating a later state into earlier snapshots, or otherwise writing snapshots that were not the deployed state at that time.
- Storing independent per-task models or adapters outside the counted arrays.
- External data or pretraining, training on development validation labels, and modifying the evaluator, budgets or data.

A method that wins only by breaking these rules is not a contribution to this direction, even when its scores are higher.
