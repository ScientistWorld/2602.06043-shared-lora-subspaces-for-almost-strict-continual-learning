# Evaluation

## Metrics

Use task-appropriate benefit metrics and continual-learning constraint metrics.

For natural language understanding, report Matthews correlation for CoLA, Pearson correlation for STS-B, and accuracy for MRPC, RTE, QNLI, and SST-2. The aggregate GLUE score is the unweighted average of the six task scores, with higher values better.

For image classification, report final top-1 accuracy after the complete task stream, with higher values better.

For continual-learning constraints, report trainable parameter count, stored model or adapter size, and forgetting. Forgetting is the drop from each task's best historical score to its score after the final task, averaged where applicable; lower is better. Parameter count and stored size are also lower-is-better constraint metrics.

## Baselines and Targets

Reference comparisons should include an upper-bound setting that is not constrained by continual learning, a sequential full-finetuning or linear-head baseline where applicable, and parameter-efficient non-continual or task-specific-adapter baselines when available. The paper's reported headline targets are stored in `scoring/reference.json`.

For a scaled reproduction, the absolute numbers may be lower if smaller datasets, fewer tasks, or shorter training are used. The scoring should still preserve the same comparison shape: benefit metrics must be evaluated together with parameter, memory, and forgetting constraints.

## Evaluation Protocol

Evaluate after a fixed task order and report final performance on all tasks in the stream. Do not use previous task training data during later-task training unless the experimental condition explicitly permits replay. Use the same preprocessing for training and evaluation, fixed random seeds, and the same backbone and data splits across all methods being compared.

For GLUE-style scaled runs, keep the six-task structure when feasible and report per-task scores plus their average. For image-classification scaled runs, split each dataset into class-incremental tasks and report final accuracy and forgetting after all tasks are learned.
