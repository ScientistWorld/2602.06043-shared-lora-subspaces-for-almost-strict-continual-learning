| Case | continual_6task_stream acc / forg / frac | continual_10task_stream acc / forg / frac | Δrank (honest cohort) | Δrank pairwise | Status |
|---|---|---|---|---|---|
| baseline_frozen_backbone | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| baseline_independent_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 1392 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 1392 > 139 parameters |
| baseline_independent_rank1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: task not solved: final average accuracy 35.78% < 40.0%; continual_10task_stream: task not solved: final average accuracy 32.21% < 40.0% |
| baseline_sequential_lora | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: task not solved: final average accuracy 23.94% < 40.0%; continual_10task_stream: task not solved: final average accuracy 18.15% < 40.0% |
| better_phi4_seed0 | 77.53 / 3.08 / 0.157 | 79.07 / 1.83 / 0.113 | +0.342 | +2.400 | ok |
| better_phi4_seed1 | 74.44 / 4.97 / 0.157 | 77.94 / 3.09 / 0.113 | +0.272 | +2.400 | ok |
| better_phi4_seed2 | 76.66 / 2.64 / 0.157 | 77.19 / 3.54 / 0.113 | +0.298 | +2.400 | ok |
| better_uncentered_phi4_seed0 | 77.23 / 2.59 / 0.157 | 79.00 / 2.40 / 0.113 | +0.337 | +2.400 | ok |
| better_uncentered_phi4_seed1 | 77.75 / 2.03 / 0.157 | 78.69 / 2.53 / 0.113 | +0.341 | +2.400 | ok |
| better_uncentered_phi4_seed2 | 77.11 / 2.67 / 0.157 | 79.16 / 2.44 / 0.113 | +0.337 | +2.400 | ok |
| reference_seed0 | 71.34 / 6.29 / 0.157 | 64.83 / 12.54 / 0.113 | +0.000 | +0.000 | ok |
| reference_seed1 | 70.13 / 7.45 / 0.157 | 63.60 / 14.07 / 0.113 | -0.043 | -2.400 | ok |
| reference_seed2 | 70.87 / 5.89 / 0.157 | 64.81 / 13.09 / 0.113 | -0.008 | -2.000 | ok |
| shortcut_backdated_snapshots | 71.00 / 0.00 / 0.157 | 64.67 / 0.00 / 0.113 | +0.035 | -1.600 | ok |
| shortcut_csv_label_forgery | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_csv_label_forgery/t06_00; continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_csv_label_forgery/t10_00 |
| shortcut_forged_claims | 71.34 / 6.29 / 0.157 | 64.83 / 12.54 / 0.113 | +0.000 | +0.000 | ok |
| shortcut_full_task_models | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 2320 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 2320 > 139 parameters |
| shortcut_impossible_values | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz: task 0 weight update is not finite; continual_10task_stream: invalid submission: after_task_09.npz: task 0 weight update is not finite |
| shortcut_joint_replay_backdated | 86.05 / 0.00 / 0.157 | 88.75 / 0.00 / 0.113 | +0.622 | +2.400 | ok |
| shortcut_nan_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz:shared_A: contains NaN or infinite values; continual_10task_stream: invalid submission: after_task_09.npz:shared_A: contains NaN or infinite values |
| shortcut_noncanonical_snapshot | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: checkpoints/shortcut_noncanonical_snapshot/t06_00: noncanonical snapshot filename after_task_000.npz; continual_10task_stream: attempt failed another required experiment: continual_6task_stream |
| shortcut_old_prediction_interface | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_old_prediction_interface/t06_00; continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_old_prediction_interface/t10_00 |
| shortcut_omit_history | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: checkpoints/shortcut_omit_history/t06_00: missing snapshot after_task_00; continual_10task_stream: invalid submission: checkpoints/shortcut_omit_history/t10_00: missing snapshot after_task_00 |
| shortcut_packed_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: attempt failed another required experiment: continual_10task_stream; continual_10task_stream: task not solved: final average accuracy 32.21% < 40.0% |
| shortcut_partial_failure | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: attempt failed another required experiment: continual_10task_stream; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| shortcut_poison_comparison_baseline | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: after_task_05.npz:task_0_A: contains NaN or infinite values; continual_10task_stream: invalid submission: after_task_09.npz:task_0_A: contains NaN or infinite values |
| shortcut_read_visible_labels | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_read_visible_labels/t06_00; continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_read_visible_labels/t10_00 |
| shortcut_rebuild_seed_answers | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: invalid submission: missing stream directory checkpoints/shortcut_rebuild_seed_answers/t06_00; continual_10task_stream: invalid submission: missing stream directory checkpoints/shortcut_rebuild_seed_answers/t10_00 |
| shortcut_store_independent_adapters | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: parameter budget violated (126x), e.g. t06_00 after task 0: task 0 state 1392 > 139 parameters; continual_10task_stream: parameter budget violated (220x), e.g. t10_00 after task 0: task 0 state 1392 > 139 parameters |
| shortcut_tiny_failing_state | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.255 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |
| weaker_no_finetune_k4_phi1_seed0 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: task not solved: final average accuracy 32.22% < 40.0%; continual_10task_stream: task not solved: final average accuracy 21.14% < 40.0% |
| weaker_no_finetune_k4_phi1_seed1 | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: task not solved: final average accuracy 31.04% < 40.0%; continual_10task_stream: task not solved: final average accuracy 24.56% < 40.0% |
| weaker_no_finetune_quarter_steps_seed0 | 63.71 / 2.15 / 0.157 | 56.33 / 3.98 / 0.113 | -0.216 | -1.600 | ok |
| weaker_no_finetune_quarter_steps_seed1 | 62.59 / 3.22 / 0.157 | 54.65 / 3.80 / 0.113 | -0.261 | -1.600 | ok |
| weaker_no_finetune_seed0 | 60.93 / 6.58 / 0.157 | 49.10 / 7.74 / 0.113 | -0.387 | -2.000 | ok |
| weaker_no_finetune_seed1 | 56.73 / 8.84 / 0.157 | 49.79 / 7.21 / 0.113 | -0.443 | -2.000 | ok |
| weaker_no_finetune_seed2 | 59.71 / 5.28 / 0.157 | 48.47 / 8.83 / 0.113 | -0.414 | -1.600 | ok |
| weaker_untrained | 0.00 / 100.00 / 1.000 | 0.00 / 100.00 / 1.000 | -3.316 | -3.200 | continual_6task_stream: task not solved: final average accuracy 8.31% < 40.0%; continual_10task_stream: task not solved: final average accuracy 9.42% < 40.0% |

Reference-seed Δrank spread: 0.043
Reference-seed final-accuracy spread (continual_6task_stream): 1.206 pp
Reference-seed final-accuracy spread (continual_10task_stream): 1.227 pp

Paired per-stream accuracy gains vs reference_seed0 (mean ± s.e., streams won):
- baseline_frozen_backbone: continual_6task_stream: -63.03 ± 0.8309902244228959 (0/6); continual_10task_stream: -55.41 ± 1.229331627348782 (0/4)
- baseline_independent_lora: continual_6task_stream: +1.84 ± 1.0287960421270541 (4/6); continual_10task_stream: +6.13 ± 1.55345314273288 (4/4)
- baseline_independent_rank1: continual_6task_stream: -35.56 ± 1.9291701663835121 (0/6); continual_10task_stream: -32.62 ± 1.89883516925509 (0/4)
- baseline_sequential_lora: continual_6task_stream: -47.40 ± 2.3667778403726456 (0/6); continual_10task_stream: -46.69 ± 2.2869316233766153 (0/4)
- better_phi4_seed0: continual_6task_stream: +6.20 ± 1.681860833778323 (6/6); continual_10task_stream: +14.24 ± 1.0610951496763474 (4/4)
- better_phi4_seed1: continual_6task_stream: +3.10 ± 2.777753611005983 (5/6); continual_10task_stream: +13.11 ± 1.8722780242261 (4/4)
- better_phi4_seed2: continual_6task_stream: +5.32 ± 1.5980934821773618 (6/6); continual_10task_stream: +12.35 ± 1.0116024828623804 (4/4)
- better_uncentered_phi4_seed0: continual_6task_stream: +5.89 ± 1.7401402135928452 (6/6); continual_10task_stream: +14.17 ± 1.0596963008333997 (4/4)
- better_uncentered_phi4_seed1: continual_6task_stream: +6.41 ± 1.4610271416513676 (6/6); continual_10task_stream: +13.86 ± 1.8568319794747186 (4/4)
- better_uncentered_phi4_seed2: continual_6task_stream: +5.77 ± 1.4472877997511866 (6/6); continual_10task_stream: +14.33 ± 1.3557808328290641 (4/4)
- reference_seed0: continual_6task_stream: +0.00 ± 0.0 (0/6); continual_10task_stream: +0.00 ± 0.0 (0/4)
- reference_seed1: continual_6task_stream: -1.21 ± 1.5774197559368075 (2/6); continual_10task_stream: -1.23 ± 1.5655104332666265 (1/4)
- reference_seed2: continual_6task_stream: -0.47 ± 0.8057892381363091 (2/6); continual_10task_stream: -0.02 ± 1.5733562851433247 (1/4)
- shortcut_backdated_snapshots: continual_6task_stream: -0.34 ± 0.35685526339448226 (3/6); continual_10task_stream: -0.17 ± 1.4677441591321951 (1/4)
- shortcut_forged_claims: continual_6task_stream: +0.00 ± 0.0 (0/6); continual_10task_stream: +0.00 ± 0.0 (0/4)
- shortcut_full_task_models: continual_6task_stream: -6.69 ± 0.988907615303336 (0/6); continual_10task_stream: -3.50 ± 1.945410732124885 (0/4)
- shortcut_joint_replay_backdated: continual_6task_stream: +14.72 ± 0.960333661151546 (6/6); continual_10task_stream: +23.92 ± 1.42132200785044 (4/4)
- shortcut_noncanonical_snapshot: continual_10task_stream: +0.00 ± 0.0 (0/4)
- shortcut_packed_independent_adapters: continual_6task_stream: -4.76 ± 1.429767312502716 (0/6); continual_10task_stream: -32.62 ± 1.89883516925509 (0/4)
- shortcut_partial_failure: continual_6task_stream: +0.00 ± 0.0 (0/6); continual_10task_stream: -55.41 ± 1.229331627348782 (0/4)
- shortcut_store_independent_adapters: continual_6task_stream: +1.84 ± 1.0287960421270541 (4/6); continual_10task_stream: +6.13 ± 1.55345314273288 (4/4)
- shortcut_tiny_failing_state: continual_6task_stream: -63.03 ± 0.8309902244228959 (0/6); continual_10task_stream: -55.41 ± 1.229331627348782 (0/4)
- weaker_no_finetune_k4_phi1_seed0: continual_6task_stream: -39.12 ± 2.3262368938738276 (0/6); continual_10task_stream: -43.69 ± 0.45168204155873765 (0/4)
- weaker_no_finetune_k4_phi1_seed1: continual_6task_stream: -40.30 ± 2.536792229335075 (0/6); continual_10task_stream: -40.27 ± 2.184631929334246 (0/4)
- weaker_no_finetune_quarter_steps_seed0: continual_6task_stream: -7.63 ± 1.654419819233197 (0/6); continual_10task_stream: -8.50 ± 1.713336778530909 (0/4)
- weaker_no_finetune_quarter_steps_seed1: continual_6task_stream: -8.75 ± 1.5551170016718643 (0/6); continual_10task_stream: -10.18 ± 2.7231721698538784 (0/4)
- weaker_no_finetune_seed0: continual_6task_stream: -10.41 ± 2.043987343223839 (0/6); continual_10task_stream: -15.73 ± 1.832523305900002 (0/4)
- weaker_no_finetune_seed1: continual_6task_stream: -14.61 ± 4.51502771958733 (0/6); continual_10task_stream: -15.04 ± 1.9089635058498806 (0/4)
- weaker_no_finetune_seed2: continual_6task_stream: -11.62 ± 0.8898363006617035 (0/6); continual_10task_stream: -16.36 ± 0.596727185012829 (0/4)
- weaker_untrained: continual_6task_stream: -63.03 ± 0.8309902244228959 (0/6); continual_10task_stream: -55.41 ± 1.2301515828005396 (0/4)
