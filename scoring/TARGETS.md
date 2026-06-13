# Evaluation Targets

## synthetic_continual_low_rank

Tests the paper's central claim in a scaled setting: a method must learn a stream of related tasks without replaying previous task data, retain final performance across the stream, and report parameter-efficiency constraints.

- **Primary metric:** `final_average_accuracy` (higher is better)
- **Benefit metrics:** final average accuracy and per-task final accuracies (`task_0_accuracy` through `task_3_accuracy`)
- **Constraint metrics:** `trainable_parameters` and `parameter_fraction_vs_lora_stream` (lower is better), plus `compression_ratio_vs_lora_stream` (higher is better)
- **How to run:** `bash scripts/reproduce.sh`, or run method/baseline scripts followed by `bash scripts/evaluate.sh`
