| Case | continual_6task_stream acc / forg / frac | continual_10task_stream acc / forg / frac | Δrank (honest cohort) | Δrank pairwise | Status |
|---|---|---|---|---|---|
| baseline_frozen_backbone | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| baseline_independent_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 1392 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 1392 > 139 parameters |
| baseline_independent_rank1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: task not solved: final average accuracy 35.78% < 40.0%; continual_10task_stream: task not solved: final average accuracy 32.21% < 40.0% |
| baseline_sequential_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: task not solved: final average accuracy 23.94% < 40.0%; continual_10task_stream: task not solved: final average accuracy 18.14% < 40.0% |
| better_refit_phi4_seed0 | 77.53 / 3.08 / 0.157 | 79.07 / 1.83 / 0.113 | +0.730 | +2.400 | ok |
| better_refit_phi4_seed1 | 74.44 / 4.97 / 0.157 | 77.94 / 3.09 / 0.113 | +0.659 | +2.400 | ok |
| better_refit_phi4_seed2 | 76.66 / 2.64 / 0.157 | 77.19 / 3.54 / 0.113 | +0.685 | +2.400 | ok |
| better_refit_seed0 | 71.00 / 6.60 / 0.157 | 64.67 / 13.21 / 0.113 | +0.377 | +1.600 | ok |
| better_refit_seed1 | 70.13 / 7.45 / 0.157 | 63.60 / 14.07 / 0.113 | +0.344 | +1.600 | ok |
| better_refit_seed2 | 70.87 / 5.89 / 0.157 | 64.81 / 13.09 / 0.113 | +0.379 | +2.000 | ok |
| better_uncentered_refit_phi4_seed0 | 77.23 / 2.59 / 0.157 | 79.00 / 2.40 / 0.113 | +0.724 | +2.400 | ok |
| better_uncentered_refit_phi4_seed1 | 77.75 / 2.03 / 0.157 | 78.69 / 2.53 / 0.113 | +0.728 | +2.400 | ok |
| better_uncentered_refit_phi4_seed2 | 77.11 / 2.67 / 0.157 | 79.16 / 2.44 / 0.113 | +0.724 | +2.400 | ok |
| reference_seed0 | 60.93 / 6.58 / 0.157 | 49.10 / 7.74 / 0.113 | +0.000 | +0.000 | ok |
| reference_seed1 | 56.73 / 8.84 / 0.157 | 49.79 / 7.21 / 0.113 | -0.056 | +0.000 | ok |
| reference_seed2 | 59.71 / 5.28 / 0.157 | 48.47 / 8.83 / 0.113 | -0.027 | -2.000 | ok |
| shortcut_backdated_snapshots | 60.93 / 0.00 / 0.157 | 49.10 / 0.00 / 0.113 | +0.032 | +0.400 | ok |
| shortcut_forged_claims | 60.93 / 6.58 / 0.157 | 49.10 / 7.74 / 0.113 | +0.000 | +0.000 | ok |
| shortcut_full_task_models | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 2320 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 2320 > 139 parameters |
| shortcut_impossible_values | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz: task 0 weight update is not finite; continual_10task_stream: invalid submission: after_task_09.npz: task 0 weight update is not finite |
| shortcut_joint_replay_backdated | 86.05 / 0.00 / 0.157 | 88.75 / 0.00 / 0.113 | +1.003 | +2.400 | ok |
| shortcut_nan_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz:shared_A: contains NaN or infinite values; continual_10task_stream: invalid submission: after_task_09.npz:shared_A: contains NaN or infinite values |
| shortcut_old_prediction_interface | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: invalid submission: missing stream directory redteam/hardening/runs/shortcut_old_prediction_interface/t06_00; continual_10task_stream: invalid submission: missing stream directory redteam/hardening/runs/shortcut_old_prediction_interface/t10_00 |
| shortcut_omit_history | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: invalid submission: redteam/hardening/runs/shortcut_omit_history/t06_00: missing snapshot after_task_00; continual_10task_stream: invalid submission: redteam/hardening/runs/shortcut_omit_history/t10_00: missing snapshot after_task_00 |
| shortcut_packed_independent_adapters | 66.58 / 0.00 / 0.201 | 0.00 / 100.00 / 1.000 | -1.283 | -0.800 | continual_10task_stream: task not solved: final average accuracy 32.21% < 40.0% |
| shortcut_poison_comparison_baseline | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz:task_0_A: contains NaN or infinite values; continual_10task_stream: invalid submission: after_task_09.npz:task_0_A: contains NaN or infinite values |
| shortcut_store_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 1392 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 1392 > 139 parameters |
| shortcut_tiny_failing_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.875 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| weaker_k4_phi1_seed0 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: task not solved: final average accuracy 32.22% < 40.0%; continual_10task_stream: task not solved: final average accuracy 21.14% < 40.0% |
| weaker_k4_phi1_seed1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: task not solved: final average accuracy 31.04% < 40.0%; continual_10task_stream: task not solved: final average accuracy 24.56% < 40.0% |
| weaker_quarter_steps_seed0 | 63.71 / 2.15 / 0.157 | 56.33 / 3.98 / 0.113 | +0.171 | +2.400 | ok |
| weaker_quarter_steps_seed1 | 62.59 / 3.22 / 0.157 | 54.65 / 3.80 / 0.113 | +0.126 | +2.400 | ok |
| weaker_untrained | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.930 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |

Reference-seed Δrank spread: 0.056
Reference-seed final-accuracy spread (continual_6task_stream): 4.203 pp
Reference-seed final-accuracy spread (continual_10task_stream): 1.315 pp

Paired per-stream accuracy gains vs reference_seed0 (mean ± s.e., streams won):
- baseline_frozen_backbone: continual_6task_stream: -52.62 ± 1.58 (0/6); continual_10task_stream: -39.67 ± 2.22 (0/4)
- baseline_independent_lora: continual_6task_stream: +12.25 ± 1.49 (6/6); continual_10task_stream: +21.87 ± 2.04 (4/4)
- baseline_independent_rank1: continual_6task_stream: -25.15 ± 1.84 (0/6); continual_10task_stream: -16.89 ± 2.08 (0/4)
- baseline_sequential_lora: continual_6task_stream: -36.99 ± 2.20 (0/6); continual_10task_stream: -30.95 ± 3.67 (0/4)
- better_refit_phi4_seed0: continual_6task_stream: +16.61 ± 1.65 (6/6); continual_10task_stream: +29.97 ± 2.22 (4/4)
- better_refit_phi4_seed1: continual_6task_stream: +13.51 ± 3.11 (5/6); continual_10task_stream: +28.84 ± 3.46 (4/4)
- better_refit_phi4_seed2: continual_6task_stream: +15.73 ± 1.16 (6/6); continual_10task_stream: +28.09 ± 1.91 (4/4)
- better_refit_seed0: continual_6task_stream: +10.07 ± 2.09 (6/6); continual_10task_stream: +15.57 ± 1.62 (4/4)
- better_refit_seed1: continual_6task_stream: +9.20 ± 1.18 (6/6); continual_10task_stream: +14.51 ± 2.09 (4/4)
- better_refit_seed2: continual_6task_stream: +9.94 ± 1.60 (6/6); continual_10task_stream: +15.71 ± 1.90 (4/4)
- better_uncentered_refit_phi4_seed0: continual_6task_stream: +16.30 ± 2.08 (6/6); continual_10task_stream: +29.90 ± 1.75 (4/4)
- better_uncentered_refit_phi4_seed1: continual_6task_stream: +16.82 ± 1.28 (6/6); continual_10task_stream: +29.59 ± 2.64 (4/4)
- better_uncentered_refit_phi4_seed2: continual_6task_stream: +16.18 ± 1.47 (6/6); continual_10task_stream: +30.06 ± 1.91 (4/4)
- reference_seed0: continual_6task_stream: +0.00 ± 0.00 (0/6); continual_10task_stream: +0.00 ± 0.00 (0/4)
- reference_seed1: continual_6task_stream: -4.20 ± 3.07 (2/6); continual_10task_stream: +0.69 ± 1.00 (3/4)
- reference_seed2: continual_6task_stream: -1.21 ± 1.49 (1/6); continual_10task_stream: -0.62 ± 1.45 (2/4)
- shortcut_backdated_snapshots: continual_6task_stream: +0.00 ± 0.00 (0/6); continual_10task_stream: +0.00 ± 0.00 (0/4)
- shortcut_forged_claims: continual_6task_stream: +0.00 ± 0.00 (0/6); continual_10task_stream: +0.00 ± 0.00 (0/4)
- shortcut_full_task_models: continual_6task_stream: +3.72 ± 1.22 (6/6); continual_10task_stream: +12.23 ± 2.37 (4/4)
- shortcut_joint_replay_backdated: continual_6task_stream: +25.12 ± 1.58 (6/6); continual_10task_stream: +39.66 ± 2.05 (4/4)
- shortcut_packed_independent_adapters: continual_6task_stream: +5.65 ± 1.47 (6/6); continual_10task_stream: -16.89 ± 2.08 (0/4)
- shortcut_store_independent_adapters: continual_6task_stream: +12.25 ± 1.49 (6/6); continual_10task_stream: +21.87 ± 2.04 (4/4)
- shortcut_tiny_failing_state: continual_6task_stream: -52.62 ± 1.58 (0/6); continual_10task_stream: -39.67 ± 2.22 (0/4)
- weaker_k4_phi1_seed0: continual_6task_stream: -28.71 ± 2.24 (0/6); continual_10task_stream: -27.95 ± 1.75 (0/4)
- weaker_k4_phi1_seed1: continual_6task_stream: -29.89 ± 2.42 (0/6); continual_10task_stream: -24.53 ± 3.23 (0/4)
- weaker_quarter_steps_seed0: continual_6task_stream: +2.78 ± 1.76 (5/6); continual_10task_stream: +7.23 ± 1.80 (4/4)
- weaker_quarter_steps_seed1: continual_6task_stream: +1.66 ± 1.75 (5/6); continual_10task_stream: +5.56 ± 3.39 (3/4)
- weaker_untrained: continual_6task_stream: -52.62 ± 1.58 (0/6); continual_10task_stream: -39.67 ± 2.22 (0/4)
