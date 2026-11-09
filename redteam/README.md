# Scoring audit

Each case has one `run.sh`, invoked from `/home/user`. It prepares ordinary saved
prediction artifacts, runs the visible evaluator, then invokes the restored
`bash scripts/evaluate_test.sh` with **no arguments**, in a fresh subprocess.
No case modifies eval/, Python packages, import resolution, or evaluator processes.
All learning and numerical work belongs in a scheduled compute job.

The audit starts from the finished gym's populated `checkpoints/` and generated
datasets. On a fresh clone, first run the original gym's `scripts/run.sh` as a
compute job to populate them. To repeat an individual case in the gym container,
run `bash redteam/<case>/run.sh` as a job; it always reruns that case, saves its
scores, and restores the starting inputs. The batch runner resumes by skipping
cases with an existing `status.json`. Its `_backup/` is local restoration state
and must be removed before auditing a different starting gym.

`run_all.sh` bundles independent cases, backs up pre-existing data, checkpoints,
and scores, and restores them even when an expected validation failure occurs.
`reference/share_linear.py` is a verbatim snapshot of the agent-visible reference
method. Shortcuts consume only visible data, code, and their own trained outputs.
The hidden scoring contract is only read by `summarize.py`, after trials finish.

Large or regenerated run artifacts live under ignored `_artifacts/`; per-case
scores, exit codes, summaries, and small prediction CSVs are retained in git.
`job_logs/` retains the two scheduler jobs' logs. `first_batch/` is superseded
evidence; final case directories and `audit_summary.json` are authoritative.
Numerical rank deltas use the reference.json metric coefficients' absolute
values, directions, experiment weights, and per-metric population standard
deviations across the explicitly declared audit cohort. A future cohort can
change scalar deltas; dominance findings do not depend on those deviations.
Control-only ranks are reported only for members of that cohort; they are not
extrapolated to resource outliers that would change the normalizers themselves.
The 15-member control cohort includes the full-model brute-force shortcut with
honest cost accounting. Its post-execution path rename is recorded in
`case_renames.json`; original status/log evidence has been preserved.
