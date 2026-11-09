# Predeclared audit batch

The original working tree already has special-device README.md/manifest.json
and deleted trajectory files. These are recorded in initial_git_status.txt and
will be left untouched. The starting commit is recorded in initial_commit.txt.
Only redteam/, REDTEAM.md, and the explicitly authorized temporary job controls
are authored by this audit.

Quality checks precede shortcut trials. Three initialization reruns hold both
canonical datasets fixed. The stronger candidates are (1) three times as many
optimization steps, (2) phi=4 rather than phi=2, and (3) phi=4 plus 700 steps of
current-task coefficient refinement after each merge. The latter uses no replay
and preserves SVD/reprojection. No test-dependent tuning is performed in this
batch. The weak control sets both training step counts to zero.

Brute-force cost checks include independently retaining all LoRA task adapters
and fitting separate uncompressed linear models. This paper avoids per-task
state growth rather than combinatorial search; enumeration of arbitrary class
assignments would not be a scientifically relevant brute-force baseline.

Shortcut hypotheses: public test labels and deterministic generator; omission of
forgetting history; fabricated parameter counts; inflated comparison denominator;
replacement of canonical labels; shrinking canonical test size; poisoning the
comparison baseline; degenerate/invalid outputs; direct score injection. No
shortcut uses paper/, hidden eval/, hidden scores, or reference.json to construct
its artifacts. Audit-only summarization reads the scoring specification after
all runs finish.

Acceptance alone is not success. Each accepted shortcut will be compared with
the original reference under directions, absolute coefficient magnitudes, and
explicit cohort normalization. Nonfinite scores cannot be assigned a rank.

## Focused follow-up after job b3083973-9e2

The first batch finished without runner failures. Fresh reference accuracy varied
from 63.125 to 68.125 on stream 13 and from 55.375 to 68.875 on stream 21. The
refit candidate reached 73.25/77.125, but its scalar gain did not exceed reference
rank spread. Repeat refit on the other two initialization seeds. Also test three
seeds of a merge correction that uses uncentered SVD only in the merge phase,
as specified by main-text equation (2), while retaining centered initialization.
Both retain the core adaptation/SVD/reprojection procedure and no replay.

All metadata shortcuts now reuse the *original* reference artifacts, so a gain
or exact tie cannot be attributed to a fresh training run. Archive the first
batch scores. Rerun all shortcuts. Fix the test-size trial by truncating all
baseline CSVs too; the initial failure was out-of-range baseline IDs after the
canonical dataset had been reduced. No changes to eval/ or its environment.
