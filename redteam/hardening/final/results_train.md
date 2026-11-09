| Case | continual_10task_stream acc / forg / frac | continual_6task_stream acc / forg / frac | Δrank (honest cohort) | Δrank pairwise | Status |
|---|---|---|---|---|---|
| baseline_frozen_backbone | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: task not solved: final average accuracy 7.85% < 40.0% |
| baseline_independent_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: parameter budget violated (55x), e.g. d10_00 after task 0: task 0 state 1392 > 139 parameters; continual_6task_stream: parameter budget violated (42x), e.g. d06_00 after task 0: task 0 state 1392 > 139 parameters |
| baseline_independent_rank1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: task not solved: final average accuracy 38.80% < 40.0%; continual_6task_stream: task not solved: final average accuracy 27.63% < 40.0% |
| baseline_sequential_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: task not solved: final average accuracy 18.22% < 40.0%; continual_6task_stream: task not solved: final average accuracy 20.42% < 40.0% |
| better_phi4_seed0 | 78.10 / 3.04 / 0.113 | 78.08 / 1.32 / 0.157 | +0.248 | +2.400 | ok |
| better_phi4_seed1 | 78.38 / 2.38 / 0.113 | 76.75 / 2.56 / 0.157 | +0.231 | +2.400 | ok |
| better_phi4_seed2 | 77.72 / 2.47 / 0.113 | 77.38 / 3.06 / 0.157 | +0.229 | +2.400 | ok |
| better_uncentered_phi4_seed0 | 79.30 / 2.00 / 0.113 | 77.07 / 2.26 / 0.157 | +0.251 | +2.400 | ok |
| better_uncentered_phi4_seed1 | 78.22 / 3.04 / 0.113 | 74.98 / 4.70 / 0.157 | +0.196 | +2.400 | ok |
| better_uncentered_phi4_seed2 | 78.88 / 2.31 / 0.113 | 77.37 / 1.98 / 0.157 | +0.249 | +2.400 | ok |
| reference_seed0 | 71.42 / 8.00 / 0.113 | 69.97 / 8.60 / 0.157 | +0.000 | +0.000 | ok |
| reference_seed1 | 69.72 / 9.69 / 0.113 | 72.32 / 5.16 / 0.157 | +0.014 | -0.000 | ok |
| reference_seed2 | 69.96 / 8.38 / 0.113 | 73.67 / 5.50 / 0.157 | +0.040 | -0.000 | ok |
| shortcut_backdated_snapshots | 71.64 / 0.00 / 0.113 | 72.52 / 0.00 / 0.157 | +0.079 | +2.400 | ok |
| shortcut_csv_label_forgery | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_csv_label_forgery/d10_00; continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_csv_label_forgery/d06_00 |
| shortcut_forged_claims | 71.42 / 8.00 / 0.113 | 69.97 / 8.60 / 0.157 | +0.000 | +0.000 | ok |
| shortcut_full_task_models | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: parameter budget violated (55x), e.g. d10_00 after task 0: task 0 state 2320 > 139 parameters; continual_6task_stream: parameter budget violated (42x), e.g. d06_00 after task 0: task 0 state 2320 > 139 parameters |
| shortcut_impossible_values | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: after_task_09.npz: task 0 weight update is not finite; continual_6task_stream: invalid submission: after_task_05.npz: task 0 weight update is not finite |
| shortcut_joint_replay_backdated | 88.72 / 0.00 / 0.113 | 86.77 / 0.00 / 0.157 | +0.541 | +2.400 | ok |
| shortcut_nan_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: after_task_09.npz:shared_A: contains NaN or infinite values; continual_6task_stream: invalid submission: after_task_05.npz:shared_A: contains NaN or infinite values |
| shortcut_noncanonical_snapshot | 71.42 / 8.00 / 0.113 | 69.97 / 8.60 / 0.157 | +0.000 | +0.000 | ok |
| shortcut_old_prediction_interface | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_old_prediction_interface/d10_00; continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_old_prediction_interface/d06_00 |
| shortcut_omit_history | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: checkpoints/shortcut_omit_history/d10_00: missing snapshot after_task_00; continual_6task_stream: invalid submission: checkpoints/shortcut_omit_history/d06_00: missing snapshot after_task_00 |
| shortcut_packed_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: task not solved: final average accuracy 38.80% < 40.0%; continual_6task_stream: attempt failed another required experiment: continual_10task_stream |
| shortcut_partial_failure | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: attempt failed another required experiment: continual_10task_stream |
| shortcut_poison_comparison_baseline | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: after_task_09.npz:task_0_A: contains NaN or infinite values; continual_6task_stream: invalid submission: after_task_05.npz:task_0_A: contains NaN or infinite values |
| shortcut_read_visible_labels | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_read_visible_labels/d10_00; continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_read_visible_labels/d06_00 |
| shortcut_rebuild_seed_answers | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_rebuild_seed_answers/d10_00; continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_rebuild_seed_answers/d06_00 |
| shortcut_store_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: parameter budget violated (55x), e.g. d10_00 after task 0: task 0 state 1392 > 139 parameters; continual_6task_stream: parameter budget violated (42x), e.g. d06_00 after task 0: task 0 state 1392 > 139 parameters |
| shortcut_tiny_failing_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.303 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: task not solved: final average accuracy 7.85% < 40.0% |
| weaker_no_finetune_k4_phi1_seed0 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: task not solved: final average accuracy 37.32% < 40.0%; continual_6task_stream: task not solved: final average accuracy 32.32% < 40.0% |
| weaker_no_finetune_k4_phi1_seed1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: task not solved: final average accuracy 34.36% < 40.0%; continual_6task_stream: task not solved: final average accuracy 25.22% < 40.0% |
| weaker_no_finetune_quarter_steps_seed0 | 59.02 / 2.89 / 0.113 | 58.20 / 3.60 / 0.157 | -0.338 | -1.600 | ok |
| weaker_no_finetune_quarter_steps_seed1 | 61.00 / 4.38 / 0.113 | 62.65 / 3.64 / 0.157 | -0.246 | -1.600 | ok |
| weaker_no_finetune_seed0 | 58.34 / 5.40 / 0.113 | 58.72 / 7.14 / 0.157 | -0.354 | -1.600 | ok |
| weaker_no_finetune_seed1 | 57.38 / 5.00 / 0.113 | 60.03 / 3.74 / 0.157 | -0.340 | -1.600 | ok |
| weaker_no_finetune_seed2 | 51.76 / 6.67 / 0.113 | 55.57 / 7.16 / 0.157 | -0.502 | -1.600 | ok |
| weaker_untrained | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.367 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: task not solved: final average accuracy 7.85% < 40.0% |

Reference-seed Δrank spread: 0.040
Reference-seed final-accuracy spread (continual_10task_stream): 1.700 pp
Reference-seed final-accuracy spread (continual_6task_stream): 3.700 pp

Paired per-stream accuracy gains vs reference_seed0 (mean ± s.e., streams won):
- baseline_frozen_backbone: continual_10task_stream: -60.02 ± unavailable (0/1); continual_6task_stream: -62.12 ± 2.9833333333333343 (0/2)
- baseline_independent_lora: continual_10task_stream: -0.22 ± unavailable (0/1); continual_6task_stream: +1.25 ± 0.48333333333332007 (2/2)
- baseline_independent_rank1: continual_10task_stream: -32.62 ± unavailable (0/1); continual_6task_stream: -42.33 ± 4.400000000000006 (0/2)
- baseline_sequential_lora: continual_10task_stream: -53.20 ± unavailable (0/1); continual_6task_stream: -49.55 ± 4.950000000000003 (0/2)
- better_phi4_seed0: continual_10task_stream: +6.68 ± unavailable (1/1); continual_6task_stream: +8.12 ± 0.4833333333333343 (2/2)
- better_phi4_seed1: continual_10task_stream: +6.96 ± unavailable (1/1); continual_6task_stream: +6.78 ± 1.01666666666668 (2/2)
- better_phi4_seed2: continual_10task_stream: +6.30 ± unavailable (1/1); continual_6task_stream: +7.42 ± 2.6166666666666742 (2/2)
- better_uncentered_phi4_seed0: continual_10task_stream: +7.88 ± unavailable (1/1); continual_6task_stream: +7.10 ± 0.26666666666667993 (2/2)
- better_uncentered_phi4_seed1: continual_10task_stream: +6.80 ± unavailable (1/1); continual_6task_stream: +5.02 ± 1.8833333333333329 (2/2)
- better_uncentered_phi4_seed2: continual_10task_stream: +7.46 ± unavailable (1/1); continual_6task_stream: +7.40 ± 0.1666666666666714 (2/2)
- reference_seed0: continual_10task_stream: +0.00 ± unavailable (0/1); continual_6task_stream: +0.00 ± 0.0 (0/2)
- reference_seed1: continual_10task_stream: -1.70 ± unavailable (0/1); continual_6task_stream: +2.35 ± 0.28333333333333854 (2/2)
- reference_seed2: continual_10task_stream: -1.46 ± unavailable (0/1); continual_6task_stream: +3.70 ± 1.9333333333333442 (2/2)
- shortcut_backdated_snapshots: continual_10task_stream: +0.22 ± unavailable (1/1); continual_6task_stream: +2.55 ± 0.7499999999999929 (2/2)
- shortcut_forged_claims: continual_10task_stream: +0.00 ± unavailable (0/1); continual_6task_stream: +0.00 ± 0.0 (0/2)
- shortcut_full_task_models: continual_10task_stream: -10.16 ± unavailable (0/1); continual_6task_stream: -7.83 ± 1.1666666666666679 (0/2)
- shortcut_joint_replay_backdated: continual_10task_stream: +17.30 ± unavailable (1/1); continual_6task_stream: +16.80 ± 1.0333333333333385 (2/2)
- shortcut_noncanonical_snapshot: continual_10task_stream: +0.00 ± unavailable (0/1); continual_6task_stream: +0.00 ± 0.0 (0/2)
- shortcut_packed_independent_adapters: continual_10task_stream: -32.62 ± unavailable (0/1); continual_6task_stream: -5.70 ± 0.56666666666667 (0/2)
- shortcut_partial_failure: continual_10task_stream: -60.02 ± unavailable (0/1); continual_6task_stream: +0.00 ± 0.0 (0/2)
- shortcut_store_independent_adapters: continual_10task_stream: -0.22 ± unavailable (0/1); continual_6task_stream: +1.25 ± 0.48333333333332007 (2/2)
- shortcut_tiny_failing_state: continual_10task_stream: -60.02 ± unavailable (0/1); continual_6task_stream: -62.12 ± 2.9833333333333343 (0/2)
- weaker_no_finetune_k4_phi1_seed0: continual_10task_stream: -34.10 ± unavailable (0/1); continual_6task_stream: -37.65 ± 5.3166666666666735 (0/2)
- weaker_no_finetune_k4_phi1_seed1: continual_10task_stream: -37.06 ± unavailable (0/1); continual_6task_stream: -44.75 ± 4.550000000000004 (0/2)
- weaker_no_finetune_quarter_steps_seed0: continual_10task_stream: -12.40 ± unavailable (0/1); continual_6task_stream: -11.77 ± 3.0000000000000036 (0/2)
- weaker_no_finetune_quarter_steps_seed1: continual_10task_stream: -10.42 ± unavailable (0/1); continual_6task_stream: -7.32 ± 1.1833333333333265 (0/2)
- weaker_no_finetune_seed0: continual_10task_stream: -13.08 ± unavailable (0/1); continual_6task_stream: -11.25 ± 1.9833333333333272 (0/2)
- weaker_no_finetune_seed1: continual_10task_stream: -14.04 ± unavailable (0/1); continual_6task_stream: -9.93 ± 1.1666666666666643 (0/2)
- weaker_no_finetune_seed2: continual_10task_stream: -19.66 ± unavailable (0/1); continual_6task_stream: -14.40 ± 0.56666666666667 (0/2)
- weaker_untrained: continual_10task_stream: -60.02 ± unavailable (0/1); continual_6task_stream: -62.12 ± 2.9833333333333343 (0/2)
