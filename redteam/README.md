# Scoring audit

Each case has one `run.sh`, invoked from `/home/user`. It prepares ordinary saved
prediction artifacts, runs the visible evaluator, then invokes the restored
`bash scripts/evaluate_test.sh` with **no arguments**, in a fresh subprocess.
No case modifies eval/, Python packages, import resolution, or evaluator processes.
All learning and numerical work belongs in a scheduled compute job.

`run_all.sh` bundles independent cases, backs up pre-existing data, checkpoints,
and scores, and restores them even when an expected validation failure occurs.
`reference/share_linear.py` is a verbatim snapshot of the agent-visible reference
method. Shortcuts consume only visible data, code, and their own trained outputs.
The hidden scoring contract is only read by `summarize.py`, after trials finish.

Large or regenerated run artifacts live under ignored `_artifacts/`; per-case
scores, exit codes, summaries, and small prediction CSVs are retained in git.
Numerical rank deltas use the reference.json metric coefficients' absolute
values, directions, experiment weights, and per-metric population standard
deviations across the explicitly declared audit cohort. A future cohort can
change scalar deltas; dominance findings do not depend on those deviations.
