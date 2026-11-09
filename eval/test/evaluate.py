"""Held-out test scorer for the continual low-rank adaptation benchmark.

Every scored number is recomputed here from the raw deployed state a method
saved. Nothing a method writes besides those arrays (summaries, claimed costs,
prediction files, score files) is read.

Interface (identical to eval/train): a *run* is a directory under the
prediction root (default ``checkpoints/``). For every stream it holds
``<stream_id>/after_task_XX.npz`` snapshots, one after each task in stream
order, each containing the deployed low-rank state (see
briefing/evaluation.md). The run's directory name is its method name.

Test inputs and labels are regenerated at test time from the hidden registry in
``eval/test/streams.py``; the frozen base weight is regenerated there too.
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

from eval.test.ranking import finalize

import eval.test.streams as S

SLICE_NAME = "test"

# Comparison constants fixed by the evaluator (never read from a run).
REFERENCE_ADAPTER_RANK = 12  # rank of the independent per-task adapter stream used as the cost denominator
ONE_ADAPTER = REFERENCE_ADAPTER_RANK * (S.NUM_CLASSES + S.INPUT_DIM)  # 1392 parameters
SHARED_BUDGET = ONE_ADAPTER  # shared deployed state may be at most one adapter's size
PER_TASK_BUDGET = int(0.10 * ONE_ADAPTER)  # each task may add at most 10% of one adapter (139)
MIN_FINAL_ACCURACY = {  # task-success floor on the stream-averaged final accuracy (%)
    "continual_6task_stream": 40.0,
    "continual_10task_stream": 40.0,
}
MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
FAILED_METRICS = {  # bounded worst values: every passing run dominates these
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


def _as_matrix(name: str, value: np.ndarray) -> np.ndarray:
    if value.dtype.kind not in "fiu":
        raise SubmissionError(f"{name}: dtype {value.dtype} is not a real numeric type")
    if value.ndim != 2:
        raise SubmissionError(f"{name}: expected a 2-D array, got shape {value.shape}")
    matrix = value.astype(np.float64)
    if not np.all(np.isfinite(matrix)):
        raise SubmissionError(f"{name}: contains NaN or infinite values")
    return matrix


def load_snapshot(path: Path, after_task: int) -> tuple[list[np.ndarray], int, list[int]]:
    """Return (per-task weight deltas for tasks 0..after_task, shared params, per-task params)."""

    if path.stat().st_size > MAX_SNAPSHOT_BYTES:
        raise SubmissionError(f"{path}: snapshot larger than {MAX_SNAPSHOT_BYTES} bytes")
    try:
        with zipfile.ZipFile(path) as zipped:
            if sum(info.file_size for info in zipped.infolist()) > MAX_SNAPSHOT_BYTES:
                raise SubmissionError(f"{path}: expanded snapshot exceeds byte limit")
        with np.load(path, allow_pickle=False) as archive:
            raw = {key: archive[key] for key in archive.files}
    except Exception as exc:  # noqa: BLE001 - any unreadable archive is a malformed submission
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
    if shared_a is not None and shared_a.shape[0] != S.INPUT_DIM:
        raise SubmissionError(f"{path.name}: shared_A must have {S.INPUT_DIM} rows, got {shared_a.shape}")
    if shared_b is not None and shared_b.shape[0] != S.NUM_CLASSES:
        raise SubmissionError(f"{path.name}: shared_B must have {S.NUM_CLASSES} rows, got {shared_b.shape}")
    shared_params = int(sum(a.size for a in (shared_a, shared_b) if a is not None))

    deltas, task_params = [], []
    for task in range(after_task + 1):
        keys = task_keys.get(task, set())
        if keys and keys != {"A", "B"}:
            raise SubmissionError(f"{path.name}: task {task} must provide both task_{task}_A and task_{task}_B")
        if keys:
            coef_a, coef_b = arrays[f"task_{task}_A"], arrays[f"task_{task}_B"]
            rows_a = shared_a.shape[1] if shared_a is not None else S.INPUT_DIM
            rows_b = shared_b.shape[1] if shared_b is not None else S.NUM_CLASSES
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
            right = np.zeros((S.INPUT_DIM, 0))
            left = np.zeros((S.NUM_CLASSES, 0))
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


_DATA_CACHE: dict[str, dict] = {}


def _stream_data(stream_id: str) -> dict:
    if stream_id not in _DATA_CACHE:
        _DATA_CACHE[stream_id] = S.test_split(stream_id)
    return _DATA_CACHE[stream_id]


def score_stream(run_dir: Path, stream_id: str) -> tuple[dict, list[str]]:
    count = S.num_tasks(stream_id)
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

    data = _stream_data(stream_id)
    violations: list[str] = []
    history = [[math.nan] * count for _ in range(count)]  # history[t][j]: accuracy on task j after task t
    shared_params = 0
    task_params: list[int] = []
    for t in range(count):
        deltas, shared_params, task_params = load_snapshot(present[t], t)
        if shared_params > SHARED_BUDGET:
            violations.append(f"{stream_id} after task {t}: shared state {shared_params} > {SHARED_BUDGET} parameters")
        for j, used in enumerate(task_params):
            if used > PER_TASK_BUDGET:
                violations.append(f"{stream_id} after task {t}: task {j} state {used} > {PER_TASK_BUDGET} parameters")
        for j in range(t + 1):
            history[t][j] = _accuracy(data["base"], deltas[j], data["x_test"][j], data["y_test"][j])

    final = [history[count - 1][j] for j in range(count)]
    drops = [max(history[t][j] for t in range(j, count)) - final[j] for j in range(count - 1)]
    stored = shared_params + sum(task_params)
    return {
        "final_average_accuracy": 100.0 * float(np.mean(final)),
        "worst_task_accuracy": 100.0 * float(np.min(final)),
        "average_forgetting": 100.0 * float(np.mean(drops)),
        "stored_parameters": float(stored),
        "lora_stream_parameters": float(count * ONE_ADAPTER),
    }, violations


def score_run(run_dir: Path, experiment: str) -> tuple[dict, dict | None, dict]:
    """Return (metrics, failure-or-None, per-stream accuracy)."""

    per_stream, violations = {}, []
    try:
        for sid in S.stream_ids(SLICE_NAME, experiment):
            per_stream[sid], stream_violations = score_stream(run_dir, sid)
            violations.extend(stream_violations)
    except SubmissionError as exc:
        return dict(FAILED_METRICS, stored_parameters=0.0), {"reason": f"invalid submission: {exc}"}, {}
    except Exception as exc:  # noqa: BLE001 - never let one run crash the whole scoring pass
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
    runs = discover_runs(prediction_root)
    output = {
        "_metadata": {
            "slice": SLICE_NAME,
            "streams": {exp: S.stream_ids(SLICE_NAME, exp) for exp in S.EXPERIMENTS},
            "test_examples_per_task": S.TEST_PER_TASK,
            "shared_parameter_budget": SHARED_BUDGET,
            "per_task_parameter_budget": PER_TASK_BUDGET,
            "minimum_final_average_accuracy": MIN_FINAL_ACCURACY,
            "lora_stream_rank": REFERENCE_ADAPTER_RANK,
        },
        "experiments": {},
    }
    for experiment in S.EXPERIMENTS:
        results, failures, by_stream = {}, {}, {}
        for run_dir in runs:
            metrics, failure, accuracy_by_stream = score_run(run_dir, experiment)
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
    parser.add_argument("--output", default="scoring/scores_test.json")
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
