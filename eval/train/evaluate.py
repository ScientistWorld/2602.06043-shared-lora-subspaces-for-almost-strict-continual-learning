"""Visible (development) scorer for the continual low-rank adaptation benchmark.

Scores the development streams listed in ``data/streams/manifest.json`` on
their labelled validation splits. The interface and every rule are the same as
for the held-out test: a *run* is a directory under the prediction root
(default ``checkpoints/``) holding ``<stream_id>/after_task_XX.npz`` deployed
state snapshots, one after each task in stream order; the directory name is the
method name. Every number is recomputed from those arrays; nothing else a run
writes is read. See briefing/evaluation.md for the artifact format.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import traceback
import zipfile
from pathlib import Path

import numpy as np

from eval.train.ranking import finalize

from eval.train.streams import load_manifest, load_stream, stream_ids

SLICE_NAME = "train"
ROLE = "dev"

REFERENCE_ADAPTER_RANK = 12
MIN_FINAL_ACCURACY = {
    "continual_6task_stream": 40.0,
    "continual_10task_stream": 40.0,
}
MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
FAILED_METRICS = {
    "final_average_accuracy": 0.0,
    "worst_task_accuracy": 0.0,
    "average_forgetting": 100.0,
    "parameter_fraction_vs_lora_stream": 1.0,
    "compression_ratio_vs_lora_stream": 0.0,
}

_SNAPSHOT_RE = re.compile(r"^after_task_(\d+)\.npz$")
_TASK_KEY_RE = re.compile(r"^task_(0|[1-9][0-9]*)_(A|B)$")


class SubmissionError(Exception):
    """The run's artifacts are missing, malformed or contain impossible values."""


class Limits:
    def __init__(self, classes: int, dim: int):
        self.classes = classes
        self.dim = dim
        self.one_adapter = REFERENCE_ADAPTER_RANK * (classes + dim)
        self.shared_budget = self.one_adapter
        self.per_task_budget = int(0.10 * self.one_adapter)


def _as_matrix(name: str, value: np.ndarray) -> np.ndarray:
    if value.dtype.kind not in "fiu":
        raise SubmissionError(f"{name}: dtype {value.dtype} is not a real numeric type")
    if value.ndim != 2:
        raise SubmissionError(f"{name}: expected a 2-D array, got shape {value.shape}")
    matrix = value.astype(np.float64)
    if not np.all(np.isfinite(matrix)):
        raise SubmissionError(f"{name}: contains NaN or infinite values")
    return matrix


def load_snapshot(path: Path, after_task: int, limits: Limits) -> tuple[list[np.ndarray], int, list[int]]:
    if path.stat().st_size > MAX_SNAPSHOT_BYTES:
        raise SubmissionError(f"{path}: snapshot larger than {MAX_SNAPSHOT_BYTES} bytes")
    try:
        with zipfile.ZipFile(path) as zipped:
            if sum(info.file_size for info in zipped.infolist()) > MAX_SNAPSHOT_BYTES:
                raise SubmissionError(f"{path}: expanded snapshot exceeds byte limit")
        with np.load(path, allow_pickle=False) as archive:
            raw = {key: archive[key] for key in archive.files}
    except Exception as exc:  # noqa: BLE001
        raise SubmissionError(f"{path}: unreadable snapshot ({exc.__class__.__name__}: {exc})") from exc

    arrays: dict[str, np.ndarray] = {}
    task_keys: dict[int, set[str]] = {}
    for key, value in raw.items():
        if key in ("shared_A", "shared_B"):
            arrays[key] = _as_matrix(f"{path.name}:{key}", value)
            continue
        match = _TASK_KEY_RE.match(key)
        if not match:
            raise SubmissionError(f"{path.name}: unexpected array '{key}'")
        task = int(match.group(1))
        if task > after_task:
            raise SubmissionError(f"{path.name}: holds state for task {task}, which comes after task {after_task}")
        arrays[key] = _as_matrix(f"{path.name}:{key}", value)
        task_keys.setdefault(task, set()).add(match.group(2))

    shared_a, shared_b = arrays.get("shared_A"), arrays.get("shared_B")
    if shared_a is not None and shared_a.shape[0] != limits.dim:
        raise SubmissionError(f"{path.name}: shared_A must have {limits.dim} rows, got {shared_a.shape}")
    if shared_b is not None and shared_b.shape[0] != limits.classes:
        raise SubmissionError(f"{path.name}: shared_B must have {limits.classes} rows, got {shared_b.shape}")
    shared_params = int(sum(a.size for a in (shared_a, shared_b) if a is not None))

    deltas, task_params = [], []
    for task in range(after_task + 1):
        keys = task_keys.get(task, set())
        if keys and keys != {"A", "B"}:
            raise SubmissionError(f"{path.name}: task {task} must provide both task_{task}_A and task_{task}_B")
        if keys:
            coef_a, coef_b = arrays[f"task_{task}_A"], arrays[f"task_{task}_B"]
            rows_a = shared_a.shape[1] if shared_a is not None else limits.dim
            rows_b = shared_b.shape[1] if shared_b is not None else limits.classes
            if coef_a.shape[0] != rows_a or coef_b.shape[0] != rows_b or coef_a.shape[1] != coef_b.shape[1]:
                raise SubmissionError(
                    f"{path.name}: task {task} shapes {coef_a.shape}/{coef_b.shape} do not match the shared state"
                )
            right = shared_a @ coef_a if shared_a is not None else coef_a
            left = shared_b @ coef_b if shared_b is not None else coef_b
            task_params.append(int(coef_a.size + coef_b.size))
        elif shared_a is not None and shared_b is not None:
            if shared_a.shape[1] != shared_b.shape[1]:
                raise SubmissionError(f"{path.name}: task {task} has no state and shared_A/shared_B widths differ")
            right, left = shared_a, shared_b
            task_params.append(0)
        elif shared_a is None and shared_b is None:
            right = np.zeros((limits.dim, 0))
            left = np.zeros((limits.classes, 0))
            task_params.append(0)
        else:
            raise SubmissionError(f"{path.name}: task {task} has no state and only one shared factor is present")
        delta = left @ right.T
        if not np.all(np.isfinite(delta)):
            raise SubmissionError(f"{path.name}: task {task} weight update is not finite")
        deltas.append(delta)
    return deltas, shared_params, task_params


def _accuracy(base: np.ndarray, delta: np.ndarray, x: np.ndarray, y: np.ndarray) -> float:
    logits = x.astype(np.float64) @ (base.astype(np.float64) + delta).T
    if not np.all(np.isfinite(logits)):
        raise SubmissionError("non-finite logits")
    return float((logits.argmax(axis=1) == y).mean())


_STREAM_CACHE: dict[str, object] = {}


def _stream(stream_id: str, manifest: dict):
    if stream_id not in _STREAM_CACHE:
        _STREAM_CACHE[stream_id] = load_stream(stream_id, manifest=manifest)
    return _STREAM_CACHE[stream_id]


def score_stream(run_dir: Path, stream_id: str, manifest: dict, limits: Limits) -> tuple[dict, list[str]]:
    stream = _stream(stream_id, manifest)
    count = len(stream.tasks)
    stream_dir = run_dir / stream_id
    if not stream_dir.is_dir():
        raise SubmissionError(f"missing stream directory {stream_dir}")
    present = {}
    for item in stream_dir.iterdir():
        match = _SNAPSHOT_RE.match(item.name)
        if match:
            task_index = int(match.group(1))
            if item.name != f"after_task_{task_index:02d}.npz":
                raise SubmissionError(f"{stream_dir}: noncanonical snapshot filename {item.name}")
            present[task_index] = item
    extra = sorted(t for t in present if t >= count)
    if extra:
        raise SubmissionError(f"{stream_dir}: snapshot after_task_{extra[0]:02d} beyond the stream's {count} tasks")
    missing = [t for t in range(count) if t not in present]
    if missing:
        raise SubmissionError(f"{stream_dir}: missing snapshot after_task_{missing[0]:02d}")

    violations: list[str] = []
    history = [[math.nan] * count for _ in range(count)]
    shared_params = 0
    task_params: list[int] = []
    for t in range(count):
        deltas, shared_params, task_params = load_snapshot(present[t], t, limits)
        if shared_params > limits.shared_budget:
            violations.append(f"{stream_id} after task {t}: shared state {shared_params} > {limits.shared_budget} parameters")
        for j, used in enumerate(task_params):
            if used > limits.per_task_budget:
                violations.append(f"{stream_id} after task {t}: task {j} state {used} > {limits.per_task_budget} parameters")
        for j in range(t + 1):
            task = stream.tasks[j]
            history[t][j] = _accuracy(stream.base, deltas[j], task.x_val, task.y_val)

    final = [history[count - 1][j] for j in range(count)]
    drops = [max(history[t][j] for t in range(j, count)) - final[j] for j in range(count - 1)]
    stored = shared_params + sum(task_params)
    return {
        "final_average_accuracy": 100.0 * float(np.mean(final)),
        "worst_task_accuracy": 100.0 * float(np.min(final)),
        "average_forgetting": 100.0 * float(np.mean(drops)),
        "stored_parameters": float(stored),
        "lora_stream_parameters": float(count * limits.one_adapter),
    }, violations


def score_run(run_dir: Path, experiment: str, manifest: dict, limits: Limits) -> tuple[dict, dict | None, dict]:
    per_stream, violations = {}, []
    try:
        for sid in stream_ids(ROLE, experiment, manifest):
            per_stream[sid], stream_violations = score_stream(run_dir, sid, manifest, limits)
            violations.extend(stream_violations)
    except SubmissionError as exc:
        return dict(FAILED_METRICS, stored_parameters=0.0), {"reason": f"invalid submission: {exc}"}, {}
    except Exception as exc:  # noqa: BLE001
        detail = traceback.format_exception_only(type(exc), exc)[-1].strip()
        return dict(FAILED_METRICS, stored_parameters=0.0), {"reason": f"unreadable submission: {detail}"}, {}

    def mean(key: str) -> float:
        return float(np.mean([m[key] for m in per_stream.values()]))

    stored, lora_stream = mean("stored_parameters"), mean("lora_stream_parameters")
    measured = {
        "final_average_accuracy": mean("final_average_accuracy"),
        "worst_task_accuracy": mean("worst_task_accuracy"),
        "average_forgetting": mean("average_forgetting"),
        "parameter_fraction_vs_lora_stream": stored / lora_stream,
        "compression_ratio_vs_lora_stream": lora_stream / stored if stored > 0 else 0.0,
        "stored_parameters": stored,
    }
    accuracy_by_stream = {sid: m["final_average_accuracy"] for sid, m in per_stream.items()}
    if violations:
        reason = f"parameter budget violated ({len(violations)}x), e.g. {violations[0]}"
        return dict(FAILED_METRICS, stored_parameters=stored), {"reason": reason, "measured": measured}, accuracy_by_stream
    floor = MIN_FINAL_ACCURACY[experiment]
    if measured["final_average_accuracy"] < floor:
        reason = f"task not solved: final average accuracy {measured['final_average_accuracy']:.2f}% < {floor}%"
        return dict(FAILED_METRICS, stored_parameters=stored), {"reason": reason, "measured": measured}, accuracy_by_stream
    return measured, None, accuracy_by_stream


def discover_runs(prediction_root: Path) -> list[Path]:
    if not prediction_root.is_dir():
        raise FileNotFoundError(f"Prediction root not found: {prediction_root}")
    return sorted(
        path for path in prediction_root.iterdir() if path.is_dir() and not path.name.startswith((".", "_"))
    )


def build_scores(prediction_root: Path) -> dict:
    manifest = load_manifest()
    limits = Limits(int(manifest["num_classes"]), int(manifest["input_dim"]))
    runs = discover_runs(prediction_root)
    experiments = sorted(manifest["experiments"])
    output = {
        "_metadata": {
            "slice": SLICE_NAME,
            "streams": {exp: stream_ids(ROLE, exp, manifest) for exp in experiments},
            "validation_examples_per_task": manifest["val_per_task"],
            "shared_parameter_budget": limits.shared_budget,
            "per_task_parameter_budget": limits.per_task_budget,
            "minimum_final_average_accuracy": MIN_FINAL_ACCURACY,
            "lora_stream_rank": REFERENCE_ADAPTER_RANK,
        },
        "experiments": {},
    }
    for experiment in experiments:
        results, failures, by_stream = {}, {}, {}
        for run_dir in runs:
            metrics, failure, accuracy_by_stream = score_run(run_dir, experiment, manifest, limits)
            results[run_dir.name] = metrics
            by_stream[run_dir.name] = accuracy_by_stream
            if failure is not None:
                failures[run_dir.name] = failure
        output["experiments"][experiment] = {
            "_metadata": {"slice": SLICE_NAME, "failed_runs": failures, "final_accuracy_by_stream": by_stream},
            "results": results,
        }
    return finalize(output, FAILED_METRICS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction-root", default="checkpoints")
    parser.add_argument("--output", default="scoring/scores_train.json")
    args = parser.parse_args()

    output = build_scores(Path(args.prediction_root))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    for experiment, block in output["experiments"].items():
        for name, metrics in block["results"].items():
            status = "FAILED" if name in block["_metadata"]["failed_runs"] else "ok"
            print(f"{experiment:26s} {name:32s} acc={metrics['final_average_accuracy']:7.3f} "
                  f"forg={metrics['average_forgetting']:7.3f} frac={metrics['parameter_fraction_vs_lora_stream']:.4f} {status}")


if __name__ == "__main__":
    main()
