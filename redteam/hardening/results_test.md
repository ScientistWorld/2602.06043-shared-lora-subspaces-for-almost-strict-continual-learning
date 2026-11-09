| Case | continual_6task_stream acc / forg / frac | continual_10task_stream acc / forg / frac | Δrank (honest cohort) | Δrank pairwise | Status |
|---|---|---|---|---|---|
| baseline_frozen_backbone | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| baseline_independent_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 1392 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 1392 > 139 parameters |
| baseline_independent_rank1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: task not solved: final average accuracy 35.78% < 40.0%; continual_10task_stream: task not solved: final average accuracy 32.21% < 40.0% |
| baseline_sequential_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: task not solved: final average accuracy 23.94% < 40.0%; continual_10task_stream: task not solved: final average accuracy 18.14% < 40.0% |
| better_phi4_seed0 | 77.53 / 3.08 / 0.157 | 79.07 / 1.83 / 0.113 | +0.352 | +2.400 | ok |
| better_phi4_seed1 | 74.44 / 4.97 / 0.157 | 77.94 / 3.09 / 0.113 | +0.282 | +2.400 | ok |
| better_phi4_seed2 | 76.66 / 2.64 / 0.157 | 77.19 / 3.54 / 0.113 | +0.308 | +2.400 | ok |
| better_uncentered_phi4_seed0 | 77.23 / 2.59 / 0.157 | 79.00 / 2.40 / 0.113 | +0.347 | +2.400 | ok |
| better_uncentered_phi4_seed1 | 77.75 / 2.03 / 0.157 | 78.69 / 2.53 / 0.113 | +0.351 | +2.400 | ok |
| better_uncentered_phi4_seed2 | 77.11 / 2.67 / 0.157 | 79.16 / 2.44 / 0.113 | +0.347 | +2.400 | ok |
| reference_seed0 | 71.00 / 6.60 / 0.157 | 64.67 / 13.21 / 0.113 | +0.000 | +0.000 | ok |
| reference_seed1 | 70.13 / 7.45 / 0.157 | 63.60 / 14.07 / 0.113 | -0.033 | -2.400 | ok |
| reference_seed2 | 70.87 / 5.89 / 0.157 | 64.81 / 13.09 / 0.113 | +0.002 | +0.400 | ok |
| shortcut_backdated_snapshots | 71.00 / 0.00 / 0.157 | 64.67 / 0.00 / 0.113 | +0.045 | +0.400 | ok |
| shortcut_forged_claims | 71.00 / 6.60 / 0.157 | 64.67 / 13.21 / 0.113 | +0.000 | +0.000 | ok |
| shortcut_full_task_models | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 2320 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 2320 > 139 parameters |
| shortcut_impossible_values | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz: task 0 weight update is not finite; continual_10task_stream: invalid submission: after_task_09.npz: task 0 weight update is not finite |
| shortcut_joint_replay_backdated | 86.05 / 0.00 / 0.157 | 88.75 / 0.00 / 0.113 | +0.632 | +2.400 | ok |
| shortcut_nan_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz:shared_A: contains NaN or infinite values; continual_10task_stream: invalid submission: after_task_09.npz:shared_A: contains NaN or infinite values |
| shortcut_old_prediction_interface | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: invalid submission: missing stream directory redteam/hardening/runs/shortcut_old_prediction_interface/t06_00; continual_10task_stream: invalid submission: missing stream directory redteam/hardening/runs/shortcut_old_prediction_interface/t10_00 |
| shortcut_omit_history | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: invalid submission: redteam/hardening/runs/shortcut_omit_history/t06_00: missing snapshot after_task_00; continual_10task_stream: invalid submission: redteam/hardening/runs/shortcut_omit_history/t10_00: missing snapshot after_task_00 |
| shortcut_packed_independent_adapters | 66.58 / 0.00 / 0.201 | 0.00 / 100.00 / 1.000 | -1.659 | -2.800 | continual_10task_stream: task not solved: final average accuracy 32.21% < 40.0% |
| shortcut_poison_comparison_baseline | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz:task_0_A: contains NaN or infinite values; continual_10task_stream: invalid submission: after_task_09.npz:task_0_A: contains NaN or infinite values |
| shortcut_store_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 1392 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 1392 > 139 parameters |
| shortcut_tiny_failing_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.246 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| weaker_no_finetune_k4_phi1_seed0 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: task not solved: final average accuracy 32.22% < 40.0%; continual_10task_stream: task not solved: final average accuracy 21.14% < 40.0% |
| weaker_no_finetune_k4_phi1_seed1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: task not solved: final average accuracy 31.04% < 40.0%; continual_10task_stream: task not solved: final average accuracy 24.56% < 40.0% |
| weaker_no_finetune_quarter_steps_seed0 | 63.71 / 2.15 / 0.157 | 56.33 / 3.98 / 0.113 | -0.206 | -1.600 | ok |
| weaker_no_finetune_quarter_steps_seed1 | 62.59 / 3.22 / 0.157 | 54.65 / 3.80 / 0.113 | -0.251 | -1.600 | ok |
| weaker_no_finetune_seed0 | 60.93 / 6.58 / 0.157 | 49.10 / 7.74 / 0.113 | -0.377 | -1.600 | ok |
| weaker_no_finetune_seed1 | 56.73 / 8.84 / 0.157 | 49.79 / 7.21 / 0.113 | -0.433 | -2.000 | ok |
| weaker_no_finetune_seed2 | 59.71 / 5.28 / 0.157 | 48.47 / 8.83 / 0.113 | -0.405 | -1.600 | ok |
| weaker_untrained | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.307 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |

Reference-seed Δrank spread: 0.035
Reference-seed final-accuracy spread (continual_6task_stream): 0.867 pp
Reference-seed final-accuracy spread (continual_10task_stream): 1.208 pp

Paired per-stream accuracy gains vs reference_seed0 (mean ± s.e., streams won):
- baseline_frozen_backbone: continual_6task_stream: -62.69 ± 1.03 (0/6); continual_10task_stream: -55.24 ± 1.66 (0/4)
- baseline_independent_lora: continual_6task_stream: +2.18 ± 1.12 (5/6); continual_10task_stream: +6.30 ± 1.58 (4/4)
- baseline_independent_rank1: continual_6task_stream: -35.22 ± 1.88 (0/6); continual_10task_stream: -32.46 ± 1.78 (0/4)
- baseline_sequential_lora: continual_6task_stream: -47.06 ± 2.44 (0/6); continual_10task_stream: -46.52 ± 2.77 (0/4)
- better_phi4_seed0: continual_6task_stream: +6.54 ± 1.71 (6/6); continual_10task_stream: +14.40 ± 1.76 (4/4)
- better_phi4_seed1: continual_6task_stream: +3.44 ± 2.73 (5/6); continual_10task_stream: +13.27 ± 2.67 (4/4)
- better_phi4_seed2: continual_6task_stream: +5.66 ± 1.59 (6/6); continual_10task_stream: +12.52 ± 1.80 (4/4)
- better_uncentered_phi4_seed0: continual_6task_stream: +6.23 ± 1.80 (6/6); continual_10task_stream: +14.33 ± 1.52 (4/4)
- better_uncentered_phi4_seed1: continual_6task_stream: +6.75 ± 1.50 (6/6); continual_10task_stream: +14.02 ± 2.13 (4/4)
- better_uncentered_phi4_seed2: continual_6task_stream: +6.11 ± 1.56 (6/6); continual_10task_stream: +14.49 ± 1.48 (4/4)
- reference_seed0: continual_6task_stream: +0.00 ± 0.00 (0/6); continual_10task_stream: +0.00 ± 0.00 (0/4)
- reference_seed1: continual_6task_stream: -0.87 ± 1.69 (2/6); continual_10task_stream: -1.06 ± 2.37 (1/4)
- reference_seed2: continual_6task_stream: -0.13 ± 1.07 (2/6); continual_10task_stream: +0.15 ± 0.40 (3/4)
- shortcut_backdated_snapshots: continual_6task_stream: +0.00 ± 0.00 (0/6); continual_10task_stream: +0.00 ± 0.00 (0/4)
- shortcut_forged_claims: continual_6task_stream: +0.00 ± 0.00 (0/6); continual_10task_stream: +0.00 ± 0.00 (0/4)
- shortcut_full_task_models: continual_6task_stream: -6.35 ± 1.03 (0/6); continual_10task_stream: -3.34 ± 1.80 (1/4)
- shortcut_joint_replay_backdated: continual_6task_stream: +15.06 ± 1.14 (6/6); continual_10task_stream: +24.09 ± 1.61 (4/4)
- shortcut_packed_independent_adapters: continual_6task_stream: -4.42 ± 1.50 (1/6); continual_10task_stream: -32.46 ± 1.78 (0/4)
- shortcut_store_independent_adapters: continual_6task_stream: +2.18 ± 1.12 (5/6); continual_10task_stream: +6.30 ± 1.58 (4/4)
- shortcut_tiny_failing_state: continual_6task_stream: -62.69 ± 1.03 (0/6); continual_10task_stream: -55.24 ± 1.66 (0/4)
- weaker_no_finetune_k4_phi1_seed0: continual_6task_stream: -38.78 ± 2.47 (0/6); continual_10task_stream: -43.52 ± 1.50 (0/4)
- weaker_no_finetune_k4_phi1_seed1: continual_6task_stream: -39.96 ± 2.58 (0/6); continual_10task_stream: -40.10 ± 2.06 (0/4)
- weaker_no_finetune_quarter_steps_seed0: continual_6task_stream: -7.29 ± 1.50 (0/6); continual_10task_stream: -8.34 ± 2.36 (0/4)
- weaker_no_finetune_quarter_steps_seed1: continual_6task_stream: -8.41 ± 1.82 (0/6); continual_10task_stream: -10.01 ± 2.94 (0/4)
- weaker_no_finetune_seed0: continual_6task_stream: -10.07 ± 2.09 (0/6); continual_10task_stream: -15.57 ± 1.62 (0/4)
- weaker_no_finetune_seed1: continual_6task_stream: -14.27 ± 4.42 (0/6); continual_10task_stream: -14.88 ± 1.63 (0/4)
- weaker_no_finetune_seed2: continual_6task_stream: -11.28 ± 1.11 (0/6); continual_10task_stream: -16.19 ± 1.67 (0/4)
- weaker_untrained: continual_6task_stream: -62.69 ± 1.03 (0/6); continual_10task_stream: -55.24 ± 1.66 (0/4)
