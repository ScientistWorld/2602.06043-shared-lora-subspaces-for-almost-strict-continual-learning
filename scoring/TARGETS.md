# Evaluation Targets

Both experiments are scored by the same evaluator rules (see `briefing/evaluation.md`). Every number is recomputed from the deployed-state snapshots in `checkpoints/<method_name>/<stream_id>/after_task_XX.npz`. A run that has a malformed or non-finite snapshot, exceeds the parameter budget (shared state > 1392 values, or any task > 139 values), or whose final average accuracy is below 40% receives the failure values in both experiments: accuracy 0, forgetting 100, parameter fraction 1.

## continual_6task_stream

The paper's central claim at its language-benchmark stream length: a replay-free continual learner keeps final performance across a six-task stream with a deployed state far smaller than one adapter per task.

- **Primary metric:** `final_average_accuracy` (higher is better, coefficient 1.0)
- **Constraint metrics:** `average_forgetting` (lower is better, coefficient 0.2); `parameter_fraction_vs_lora_stream` (lower is better, coefficient 0.4)
- **Reported only:** `compression_ratio_vs_lora_stream`, `stored_parameters`, `worst_task_accuracy`
- **Hard constraints (failure gates):** parameter budget; at least 40% final average accuracy
- **Scored on:** 6 hidden six-task streams, 1000 held-out examples per task (visible counterpart: 2 development streams, 500 validation examples per task)
- **How to run:** `bash scripts/reproduce.sh` (all baselines and the reference method), then `bash scripts/evaluate_train.sh`; the hidden test runs `bash scripts/evaluate_test.sh` with no arguments

## continual_10task_stream

The same claim at the paper's image-classification stream length. Here storage savings should be larger, and retention has to survive more updates of the shared state.

- **Primary metric:** `final_average_accuracy` (higher is better, coefficient 1.0)
- **Constraint metrics:** `average_forgetting` (lower is better, coefficient 0.2); `parameter_fraction_vs_lora_stream` (lower is better, coefficient 0.4)
- **Reported only:** `compression_ratio_vs_lora_stream`, `stored_parameters`, `worst_task_accuracy`
- **Hard constraints (failure gates):** parameter budget; at least 40% final average accuracy
- **Scored on:** 4 hidden ten-task streams, 1000 held-out examples per task (visible counterpart: 1 development stream)
- **How to run:** as above; both experiments come from one run directory per method
