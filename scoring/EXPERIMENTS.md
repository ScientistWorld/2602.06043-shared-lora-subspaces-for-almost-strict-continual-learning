# Experiment Overview

Both experiments use the same problem: a frozen linear classifier adapted continually to a stream of related tasks. No earlier task's data is replayed, and the stored state must fit a budget of one adapter's worth of shared parameters plus a small per-task allowance. Each experiment is scored on hidden streams with held-out examples that a method never sees. Scores are averaged over several streams, so a result reflects the method rather than one lucky stream or initialisation.

## continual_6task_stream

This experiment asks whether a learner can absorb a six-task stream (the length of the paper's language-understanding stream) and end with one compact deployed state that still performs well on every task. Three things are measured together: final accuracy over all tasks, forgetting, and the size of the deployed state relative to storing a separate adapter for every task. A method can gain only by being more accurate or more compact while still solving the tasks. Storing per-task models, exceeding the budget, or failing to learn the tasks scores as a failure.

## continual_10task_stream

This experiment repeats the measurement on longer ten-task streams (the length of the paper's image-classification streams). Longer streams test the claim that the storage advantage of a shared state grows with the number of tasks. They also make retention harder: earlier tasks have to survive many more updates of the shared state, so weaknesses in how new knowledge is integrated show up as forgetting and lower final accuracy.
