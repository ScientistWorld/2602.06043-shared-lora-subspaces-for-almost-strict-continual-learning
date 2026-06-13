# Experiment Overview

## synthetic_continual_low_rank

This experiment tests whether a sequential learner can adapt to a stream of related low-rank classification tasks while retaining final performance on all tasks. It also measures whether the final representation is genuinely parameter-efficient compared with storing a separate adapted solution for every task in the stream.

## synthetic_continual_low_rank_seed21

This experiment repeats the same task-stream evaluation with a different deterministic seed. It is intended to reveal whether a method's accuracy and parameter-efficiency tradeoff persists across another related stream, rather than only on the selected default benchmark.
