| Case | continual_10task_stream acc / forg / frac | continual_6task_stream acc / forg / frac | Δrank (honest cohort) | Δrank pairwise | Status |
|---|---|---|---|---|---|
| baseline_frozen_backbone | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: task not solved: final average accuracy 7.85% < 40.0% |
| baseline_independent_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: parameter budget violated (55x), e.g. d10_00 after task 0: task 0 state 1392 > 139 parameters; continual_6task_stream: parameter budget violated (42x), e.g. d06_00 after task 0: task 0 state 1392 > 139 parameters |
| baseline_independent_rank1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: task not solved: final average accuracy 38.80% < 40.0%; continual_6task_stream: task not solved: final average accuracy 27.63% < 40.0% |
| baseline_sequential_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: task not solved: final average accuracy 18.22% < 40.0%; continual_6task_stream: task not solved: final average accuracy 20.42% < 40.0% |
| better_refit_phi4_seed0 | 78.10 / 3.04 / 0.113 | 78.08 / 1.32 / 0.157 | +0.602 | +2.400 | ok |
| better_refit_phi4_seed1 | 78.38 / 2.38 / 0.113 | 76.75 / 2.56 / 0.157 | +0.585 | +2.400 | ok |
| better_refit_phi4_seed2 | 77.72 / 2.47 / 0.113 | 77.38 / 3.06 / 0.157 | +0.583 | +2.400 | ok |
| better_refit_seed0 | 71.64 / 6.44 / 0.113 | 72.52 / 4.90 / 0.157 | +0.407 | +2.000 | ok |
| better_refit_seed1 | 69.72 / 9.69 / 0.113 | 72.32 / 5.16 / 0.157 | +0.367 | +2.000 | ok |
| better_refit_seed2 | 69.96 / 8.38 / 0.113 | 73.67 / 5.50 / 0.157 | +0.393 | +2.000 | ok |
| better_uncentered_refit_phi4_seed0 | 79.30 / 2.00 / 0.113 | 77.07 / 2.26 / 0.157 | +0.604 | +2.400 | ok |
| better_uncentered_refit_phi4_seed1 | 78.22 / 3.04 / 0.113 | 74.98 / 4.70 / 0.157 | +0.550 | +2.400 | ok |
| better_uncentered_refit_phi4_seed2 | 78.88 / 2.31 / 0.113 | 77.37 / 1.98 / 0.157 | +0.603 | +2.400 | ok |
| reference_seed0 | 58.34 / 5.40 / 0.113 | 58.72 / 7.14 / 0.157 | +0.000 | +0.000 | ok |
| reference_seed1 | 57.38 / 5.00 / 0.113 | 60.03 / 3.74 / 0.157 | +0.014 | +0.400 | ok |
| reference_seed2 | 51.76 / 6.67 / 0.113 | 55.57 / 7.16 / 0.157 | -0.148 | -2.400 | ok |
| shortcut_backdated_snapshots | 58.34 / 0.00 / 0.113 | 58.72 / 0.00 / 0.157 | +0.028 | +0.400 | ok |
| shortcut_forged_claims | 58.34 / 5.40 / 0.113 | 58.72 / 7.14 / 0.157 | +0.000 | +0.000 | ok |
| shortcut_full_task_models | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: parameter budget violated (55x), e.g. d10_00 after task 0: task 0 state 2320 > 139 parameters; continual_6task_stream: parameter budget violated (42x), e.g. d06_00 after task 0: task 0 state 2320 > 139 parameters |
| shortcut_impossible_values | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: invalid submission: after_task_09.npz: task 0 weight update is not finite; continual_6task_stream: invalid submission: after_task_05.npz: task 0 weight update is not finite |
| shortcut_joint_replay_backdated | 88.72 / 0.00 / 0.113 | 86.77 / 0.00 / 0.157 | +0.890 | +2.400 | ok |
| shortcut_nan_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: invalid submission: after_task_09.npz:shared_A: contains NaN or infinite values; continual_6task_stream: invalid submission: after_task_05.npz:shared_A: contains NaN or infinite values |
| shortcut_old_prediction_interface | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: invalid submission: missing stream directory redteam/hardening/runs/shortcut_old_prediction_interface/d10_00; continual_6task_stream: invalid submission: missing stream directory redteam/hardening/runs/shortcut_old_prediction_interface/d06_00 |
| shortcut_omit_history | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: invalid submission: redteam/hardening/runs/shortcut_omit_history/d10_00: missing snapshot after_task_00; continual_6task_stream: invalid submission: redteam/hardening/runs/shortcut_omit_history/d06_00: missing snapshot after_task_00 |
| shortcut_packed_independent_adapters | 0.00 / 100.00 / 1.000 | 64.27 / 0.00 / 0.201 | -1.398 | -0.800 | continual_10task_stream: task not solved: final average accuracy 38.80% < 40.0% |
| shortcut_poison_comparison_baseline | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: invalid submission: after_task_09.npz:task_0_A: contains NaN or infinite values; continual_6task_stream: invalid submission: after_task_05.npz:task_0_A: contains NaN or infinite values |
| shortcut_store_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: parameter budget violated (55x), e.g. d10_00 after task 0: task 0 state 1392 > 139 parameters; continual_6task_stream: parameter budget violated (42x), e.g. d06_00 after task 0: task 0 state 1392 > 139 parameters |
| shortcut_tiny_failing_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -2.952 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: task not solved: final average accuracy 7.85% < 40.0% |
| weaker_k4_phi1_seed0 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: task not solved: final average accuracy 37.32% < 40.0%; continual_6task_stream: task not solved: final average accuracy 32.32% < 40.0% |
| weaker_k4_phi1_seed1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: task not solved: final average accuracy 34.36% < 40.0%; continual_6task_stream: task not solved: final average accuracy 25.22% < 40.0% |
| weaker_quarter_steps_seed0 | 59.02 / 2.89 / 0.113 | 58.20 / 3.60 / 0.157 | +0.016 | +0.400 | ok |
| weaker_quarter_steps_seed1 | 61.00 / 4.38 / 0.113 | 62.65 / 3.64 / 0.157 | +0.108 | +2.400 | ok |
| weaker_untrained | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.009 | -3.200 | continual_10task_stream: task not solved: final average accuracy 11.40% < 40.0%; continual_6task_stream: task not solved: final average accuracy 7.85% < 40.0% |

Reference-seed Δrank spread: 0.162
Reference-seed final-accuracy spread (continual_10task_stream): 6.580 pp
Reference-seed final-accuracy spread (continual_6task_stream): 4.467 pp

Paired per-stream accuracy gains vs reference_seed0 (mean ± s.e., streams won):
- baseline_frozen_backbone: continual_10task_stream: -46.94 ± nan (0/1); continual_6task_stream: -50.87 ± 4.97 (0/2)
- baseline_independent_lora: continual_10task_stream: +12.86 ± nan (1/1); continual_6task_stream: +12.50 ± 1.50 (2/2)
- baseline_independent_rank1: continual_10task_stream: -19.54 ± nan (0/1); continual_6task_stream: -31.08 ± 6.38 (0/2)
- baseline_sequential_lora: continual_10task_stream: -40.12 ± nan (0/1); continual_6task_stream: -38.30 ± 6.93 (0/2)
- better_refit_phi4_seed0: continual_10task_stream: +19.76 ± nan (1/1); continual_6task_stream: +19.37 ± 2.47 (2/2)
- better_refit_phi4_seed1: continual_10task_stream: +20.04 ± nan (1/1); continual_6task_stream: +18.03 ± 3.00 (2/2)
- better_refit_phi4_seed2: continual_10task_stream: +19.38 ± nan (1/1); continual_6task_stream: +18.67 ± 4.60 (2/2)
- better_refit_seed0: continual_10task_stream: +13.30 ± nan (1/1); continual_6task_stream: +13.80 ± 1.23 (2/2)
- better_refit_seed1: continual_10task_stream: +11.38 ± nan (1/1); continual_6task_stream: +13.60 ± 2.27 (2/2)
- better_refit_seed2: continual_10task_stream: +11.62 ± nan (1/1); continual_6task_stream: +14.95 ± 3.92 (2/2)
- better_uncentered_refit_phi4_seed0: continual_10task_stream: +20.96 ± nan (1/1); continual_6task_stream: +18.35 ± 2.25 (2/2)
- better_uncentered_refit_phi4_seed1: continual_10task_stream: +19.88 ± nan (1/1); continual_6task_stream: +16.27 ± 3.87 (2/2)
- better_uncentered_refit_phi4_seed2: continual_10task_stream: +20.54 ± nan (1/1); continual_6task_stream: +18.65 ± 2.15 (2/2)
- reference_seed0: continual_10task_stream: +0.00 ± nan (0/1); continual_6task_stream: +0.00 ± 0.00 (0/2)
- reference_seed1: continual_10task_stream: -0.96 ± nan (0/1); continual_6task_stream: +1.32 ± 0.82 (2/2)
- reference_seed2: continual_10task_stream: -6.58 ± nan (0/1); continual_6task_stream: -3.15 ± 1.42 (0/2)
- shortcut_backdated_snapshots: continual_10task_stream: +0.00 ± nan (0/1); continual_6task_stream: +0.00 ± 0.00 (0/2)
- shortcut_forged_claims: continual_10task_stream: +0.00 ± nan (0/1); continual_6task_stream: +0.00 ± 0.00 (0/2)
- shortcut_full_task_models: continual_10task_stream: +2.92 ± nan (1/1); continual_6task_stream: +3.42 ± 0.82 (2/2)
- shortcut_joint_replay_backdated: continual_10task_stream: +30.38 ± nan (1/1); continual_6task_stream: +28.05 ± 3.02 (2/2)
- shortcut_packed_independent_adapters: continual_10task_stream: -19.54 ± nan (0/1); continual_6task_stream: +5.55 ± 2.55 (2/2)
- shortcut_store_independent_adapters: continual_10task_stream: +12.86 ± nan (1/1); continual_6task_stream: +12.50 ± 1.50 (2/2)
- shortcut_tiny_failing_state: continual_10task_stream: -46.94 ± nan (0/1); continual_6task_stream: -50.87 ± 4.97 (0/2)
- weaker_k4_phi1_seed0: continual_10task_stream: -21.02 ± nan (0/1); continual_6task_stream: -26.40 ± 7.30 (0/2)
- weaker_k4_phi1_seed1: continual_10task_stream: -23.98 ± nan (0/1); continual_6task_stream: -33.50 ± 6.53 (0/2)
- weaker_quarter_steps_seed0: continual_10task_stream: +0.68 ± nan (1/1); continual_6task_stream: -0.52 ± 4.98 (1/2)
- weaker_quarter_steps_seed1: continual_10task_stream: +2.66 ± nan (1/1); continual_6task_stream: +3.93 ± 0.80 (2/2)
- weaker_untrained: continual_10task_stream: -46.94 ± nan (0/1); continual_6task_stream: -50.87 ± 4.97 (0/2)
