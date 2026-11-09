"""Hardening audit: build every case's artifacts, score them with the unmodified
evaluators, and compute rank deltas.

Run from /home/user inside the gym container, after scripts/reproduce.sh has
populated checkpoints/ with the reference and baseline runs:

    python -m redteam.hardening.run_audit

Cases are resumable: a case with a status file is skipped. Run artifacts go to
redteam/hardening/runs/ (npz files are git-ignored); scores and summaries are
written next to this file.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import torch

from data.streams import load_manifest, load_stream, stream_ids
from redteam.hardening import ranks
from redteam.hardening import variants as V

ROOT = Path("redteam/hardening")
RUNS = ROOT / "runs"
STATUS = ROOT / "status"
CHECKPOINTS = Path("checkpoints")


def each_stream(fn) -> None:
    manifest = load_manifest()
    for sid in stream_ids(manifest=manifest):
        fn(load_stream(sid, manifest=manifest))


def share_variant(**kwargs):
    def build(out: Path) -> None:
        each_stream(lambda stream: V.share_variant_stream(stream, out, **kwargs))
    return build


def method_cli(seed: int):
    def build(out: Path) -> None:
        subprocess.run([sys.executable, "-m", "method.share_linear", "--seed", str(seed), "--output-root", str(out)],
                       check=True)
    return build


def copy_of(src: Path, then=None):
    def build(out: Path) -> None:
        V.copy_run(src, out)
        if then is not None:
            then(out)
    return build


def backdated(out: Path) -> None:
    manifest = load_manifest()
    for sid in stream_ids(manifest=manifest):
        count = int(manifest["streams"][sid]["num_tasks"])
        V.write_backdated(out, sid, count, V.load_final_state(CHECKPOINTS / "share", sid, count))


def cases() -> list[tuple[str, object]]:
    ref = CHECKPOINTS / "share"
    out = [
        ("reference_seed0", copy_of(ref)),
        ("baseline_independent_lora", copy_of(CHECKPOINTS / "independent_lora")),
        ("baseline_frozen_backbone", copy_of(CHECKPOINTS / "frozen_backbone")),
        ("baseline_sequential_lora", copy_of(CHECKPOINTS / "sequential_lora")),
        ("baseline_independent_rank1", copy_of(CHECKPOINTS / "independent_rank1")),
        # shortcuts that need no training first
        ("shortcut_forged_claims", copy_of(ref, V.forge_claims)),
        ("shortcut_omit_history", copy_of(ref, V.omit_history)),
        ("shortcut_store_independent_adapters", copy_of(CHECKPOINTS / "independent_lora")),
        ("shortcut_nan_state", copy_of(ref, lambda d: V.corrupt_final(d, "nan"))),
        ("shortcut_impossible_values", copy_of(ref, lambda d: V.corrupt_final(d, "huge"))),
        ("shortcut_poison_comparison_baseline",
         copy_of(CHECKPOINTS / "independent_lora", lambda d: V.corrupt_final(d, "nan"))),
        ("shortcut_tiny_failing_state", lambda d: each_stream(lambda s: V.tiny_failing_state(s, d))),
        ("shortcut_old_prediction_interface", lambda d: V.old_prediction_interface(d, ref)),
        ("shortcut_backdated_snapshots", backdated),
        # reference reruns with other initialisation seeds (identical code path to the method)
        ("reference_seed1", method_cli(1)),
        ("reference_seed2", method_cli(2)),
        # genuine improvements: paper-described options, no replay
        ("better_refit_seed0", share_variant(seed=0, refit_steps=700)),
        ("better_refit_seed1", share_variant(seed=1, refit_steps=700)),
        ("better_refit_seed2", share_variant(seed=2, refit_steps=700)),
        ("better_refit_phi4_seed0", share_variant(seed=0, refit_steps=700, phi=4)),
        ("better_refit_phi4_seed1", share_variant(seed=1, refit_steps=700, phi=4)),
        ("better_refit_phi4_seed2", share_variant(seed=2, refit_steps=700, phi=4)),
        # weaker controls
        ("weaker_quarter_steps_seed0", share_variant(seed=0, lora_steps=175, share_steps=375)),
        ("weaker_quarter_steps_seed1", share_variant(seed=1, lora_steps=175, share_steps=375)),
        ("weaker_k4_phi1_seed0", share_variant(seed=0, k=4, phi=1)),
        ("weaker_k4_phi1_seed1", share_variant(seed=1, k=4, phi=1)),
        ("weaker_untrained", share_variant(seed=0, lora_steps=0, share_steps=0)),
        # shortcuts that train
        ("shortcut_full_task_models", lambda d: each_stream(lambda s: V.full_task_models_stream(s, d, seed=0))),
        ("shortcut_packed_independent_adapters",
         lambda d: each_stream(lambda s: V.packed_independent_stream(s, d, seed=0))),
        ("shortcut_joint_replay_backdated", lambda d: each_stream(lambda s: V.joint_replay_stream(s, d, seed=0))),
        # third better family last (most expensive)
        ("better_uncentered_refit_phi4_seed0", share_variant(seed=0, refit_steps=700, phi=4, center_merges=False)),
        ("better_uncentered_refit_phi4_seed1", share_variant(seed=1, refit_steps=700, phi=4, center_merges=False)),
        ("better_uncentered_refit_phi4_seed2", share_variant(seed=2, refit_steps=700, phi=4, center_merges=False)),
    ]
    return out


def run_cases() -> None:
    RUNS.mkdir(parents=True, exist_ok=True)
    STATUS.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    for name, build in cases():
        status_path = STATUS / f"{name}.json"
        always = name.startswith(("reference_seed0", "baseline_")) or (
            name.startswith("shortcut_") and "full_task" not in name and "joint" not in name and "packed" not in name
        )
        if status_path.exists() and not always:
            print(f"[audit] skip {name} (done)", flush=True)
            continue
        start = time.time()
        record = {"case": name}
        try:
            out = RUNS / name
            if out.exists():
                shutil.rmtree(out)
            build(out)
            record["status"] = "built"
        except Exception:  # noqa: BLE001
            record["status"] = "error"
            record["traceback"] = traceback.format_exc()
            print(record["traceback"], flush=True)
        record["seconds"] = round(time.time() - start, 1)
        status_path.write_text(json.dumps(record, indent=2) + "\n")
        print(f"[audit] {name}: {record['status']} in {record['seconds']}s", flush=True)


def score() -> None:
    for split in ("test", "train"):
        out = ROOT / f"scores_{split}_all.json"
        subprocess.run([sys.executable, "-m", f"eval.{split}.evaluate", "--prediction-root", str(RUNS),
                        "--output", str(out)], check=True)
        summary = ranks.summarize(json.loads(out.read_text()), ranks.load_spec())
        (ROOT / f"results_{split}.json").write_text(json.dumps(summary, indent=2) + "\n")
        (ROOT / f"results_{split}.md").write_text(ranks.to_markdown(summary))
        print((ROOT / f"results_{split}.md").read_text(), flush=True)


if __name__ == "__main__":
    run_cases()
    score()
