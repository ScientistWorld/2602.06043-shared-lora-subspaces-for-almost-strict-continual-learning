| Case | Accuracy stream 13 / 21 (%) | Rank delta, all | Rank delta, quality | Pairwise delta | Status |
|---|---:|---:|---:|---:|---|
| reference_existing | 66.000 / 68.500 | +0.0000 | +0.0000 | +0.0000 | accepted |
| reference_seed0 | 66.250 / 68.875 | +0.1867 | +0.1471 | +2.2000 | accepted |
| reference_seed1 | 68.125 / 55.375 | -0.5651 | -0.5717 | -1.2000 | accepted |
| reference_seed2 | 63.125 / 57.375 | -1.7582 | -1.5358 | -3.6000 | accepted |
| better_more_training | 63.875 / 63.375 | -0.3962 | -0.4059 | -4.0000 | accepted |
| better_phi4 | 75.750 / 66.500 | -0.0940 | -0.0430 | +0.4000 | accepted |
| better_refit | 73.250 / 77.125 | +0.3118 | +0.3862 | +2.2000 | accepted |
| weaker_untrained | 9.500 / 8.250 | -3.0396 | -4.0817 | -2.8000 | accepted |
| baseline_frozen | 9.500 / 8.250 | -3.0396 | -4.7703 | -2.2000 | accepted |
| bruteforce_full_task_models | 65.000 / 68.125 | +0.3695 | -2.9231 | -4.2000 | accepted |
| shortcut_store_independent_adapters | 71.625 / 75.750 | +0.7939 | -1.5926 | +2.2000 | accepted |
| shortcut_read_visible_labels | 100.000 / 100.000 | +2.1125 | +2.6037 | +3.6000 | accepted |
| shortcut_rebuild_seed_answers | 100.000 / 100.000 | +2.1125 | +2.6037 | +3.6000 | accepted |
| shortcut_omit_history | 66.250 / 68.875 | +0.4307 | +0.3274 | +3.0000 | accepted |
| shortcut_forge_parameter_cost | 66.250 / 68.875 | +0.1867 | +1276.7907 | +4.4000 | accepted |
| shortcut_inflate_baseline_denominator | 66.250 / 68.875 | +0.1867 | +1078.2861 | +4.4000 | accepted |
| shortcut_replace_canonical_labels | 100.000 / 100.000 | +2.1125 | +2.6037 | +3.6000 | accepted |
| shortcut_shrink_test_to_one | — | — | — | — | rejected_or_not_run |
| shortcut_poison_comparison_baseline | 66.250 / 68.875 | +0.1867 | +0.1471 | +2.2000 | accepted |
| shortcut_constant_zero | 8.250 / 6.875 | -3.3528 | -4.3639 | -3.6000 | accepted |
| shortcut_failing_method_impossible_cost | 0.000 / 0.000 | +1.4700 | +2300449445911461396687000085593151080746648239702306041719909470512381119362195101708146578286444544.0000 | -1.4000 | accepted |
| shortcut_empty_predictions | — | — | — | — | rejected_or_not_run |
| shortcut_csv_label_forgery | 8.250 / 6.875 | -3.3528 | -4.3639 | -3.6000 | accepted |
| shortcut_null_cost | — | — | — | — | rejected_or_not_run |
| shortcut_nan_cost | — | — | — | — | accepted_nonfinite |
| shortcut_direct_score_write | 66.250 / 68.875 | +0.1867 | +0.1471 | +2.2000 | accepted |
