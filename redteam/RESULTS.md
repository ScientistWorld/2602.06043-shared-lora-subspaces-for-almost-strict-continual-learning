| Case | Accuracy stream 13 / 21 (%) | Rank delta, all | Rank delta, quality | Pairwise delta | Status |
|---|---:|---:|---:|---:|---|
| reference_existing | 66.000 / 68.500 | +0 | +0.0000 | +0.0000 | accepted |
| reference_seed0 | 66.250 / 68.875 | +0.21238 | +0.1735 | +2.2000 | accepted |
| reference_seed1 | 68.125 / 55.375 | -0.61582 | -0.6394 | -1.2000 | accepted |
| reference_seed2 | 63.125 / 57.375 | -1.9576 | -1.7700 | -3.6000 | accepted |
| better_more_training | 63.875 / 63.375 | -0.43075 | -0.4571 | -4.0000 | accepted |
| better_phi4 | 75.750 / 66.500 | -0.1122 | -0.0889 | +0.4000 | accepted |
| better_refit | 73.250 / 77.125 | +0.32002 | +0.3915 | +2.2000 | accepted |
| better_refit_seed1 | 76.375 / 73.875 | +0.58009 | +0.5916 | +3.2000 | accepted |
| better_refit_seed2 | 79.500 / 76.500 | +0.81589 | +0.8719 | +3.2000 | accepted |
| better_stable_seed0 | 74.750 / 76.750 | +0.63539 | +0.6562 | +4.0000 | accepted |
| better_stable_seed1 | 76.000 / 76.000 | +0.66154 | +0.6862 | +3.8000 | accepted |
| better_stable_seed2 | 78.125 / 74.500 | +0.63537 | +0.6737 | +2.8000 | accepted |
| weaker_untrained | 9.500 / 8.250 | -3.1954 | -4.4145 | -2.8000 | accepted |
| baseline_frozen | 9.500 / 8.250 | -3.1954 | -5.2108 | -2.2000 | accepted |
| shortcut_bruteforce_full_task_models | 65.000 / 68.125 | +0.42287 | -3.5143 | -4.2000 | accepted |
| shortcut_store_independent_adapters | 71.625 / 75.750 | +0.87186 | — | +2.2000 | accepted |
| shortcut_read_visible_labels | 100.000 / 100.000 | +2.0616 | — | +3.6000 | accepted |
| shortcut_rebuild_seed_answers | 100.000 / 100.000 | +2.0616 | — | +3.6000 | accepted |
| shortcut_omit_history | 66.000 / 68.500 | +0.46718 | — | +0.8000 | accepted |
| shortcut_forge_parameter_cost | 66.000 / 68.500 | +1.5446e-96 | — | +2.2000 | accepted |
| shortcut_inflate_baseline_denominator | 66.000 / 68.500 | +1.358e-96 | — | +2.2000 | accepted |
| shortcut_replace_canonical_labels | 100.000 / 100.000 | +2.0616 | — | +3.6000 | accepted |
| shortcut_shrink_test_to_one | 50.000 / 100.000 | +0.46343 | — | +0.8000 | accepted |
| shortcut_poison_comparison_baseline | 66.000 / 68.500 | +0 | — | +0.0000 | accepted |
| shortcut_constant_zero | 8.250 / 6.875 | -3.7384 | — | -3.6000 | accepted |
| shortcut_failing_method_impossible_cost | 0.000 / 0.000 | +1.7054 | — | -1.4000 | accepted |
| shortcut_empty_predictions | — | — | — | — | rejected_or_not_run |
| shortcut_csv_label_forgery | 8.250 / 6.875 | -3.7384 | — | -3.6000 | accepted |
| shortcut_null_cost | — | — | — | — | rejected_or_not_run |
| shortcut_nan_cost | — | — | — | — | accepted_nonfinite |
| shortcut_direct_score_write | 66.000 / 68.500 | +0 | — | +0.0000 | accepted |
