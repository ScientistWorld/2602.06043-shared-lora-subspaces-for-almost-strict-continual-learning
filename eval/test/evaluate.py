"""Score the held-out evaluation slice from saved prediction artifacts.

This is intentionally independent from eval/train. It reads the same generic
prediction interface and, when train scores exist, evaluates the same method
entries on the held-out row split.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np


SLICE_NAME = "test"
EXPERIMENTS_BY_SEED = {
    13: {
        "name": "synthetic_continual_low_rank",
        "data": Path("data/synthetic_share_tasks.npz"),
    },
    21: {
        "name": "synthetic_continual_low_rank_seed21",
        "data": Path("data/synthetic_share_tasks_seed21.npz"),
    },
}
KNOWN_RUN_NAMES = {
    "share": "share",
    "lora": "independent_lora",
    "frozen": "frozen_backbone",
}


def row_in_slice(row: dict[str, str]) -> bool:
    """Split each task's prediction rows into a stable held-out half."""

    task_id = int(row.get("task_id", 0))
    example_id = int(row["example_id"])
    return ((task_id * 1_000_003 + example_id) % 2) == 1


def read_summary(prediction_dir: Path) -> dict:
    path = prediction_dir / "summary.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing required parameter metadata: {path}")
    return json.loads(path.read_text())


def read_truth_labels(data_path: Path) -> dict[str, dict[int, int]]:
    if not data_path.exists():
        raise FileNotFoundError(f"Missing canonical evaluation labels: {data_path}")
    data = np.load(data_path)
    num_tasks = int(data["meta_num_tasks"])
    return {
        f"task_{task_id}": {
            example_id: int(label)
            for example_id, label in enumerate(data[f"y_test_{task_id}"].tolist())
        }
        for task_id in range(num_tasks)
    }


def read_predictions(csv_path: Path) -> dict[int, int]:
    predictions: dict[int, int] = {}
    with csv_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            example_id = int(row["example_id"])
            if example_id in predictions:
                raise ValueError(f"Duplicate prediction for example_id={example_id} in {csv_path}")
            predictions[example_id] = int(row["prediction"])
    return predictions


def read_accuracy(prediction_dir: Path, truth_labels: dict[str, dict[int, int]]) -> tuple[float, dict[str, float]]:
    per_task = {}
    total = 0
    correct = 0
    for task_name, labels in sorted(truth_labels.items()):
        csv_path = prediction_dir / f"{task_name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing predictions for {task_name}: {csv_path}")
        predictions = read_predictions(csv_path)
        invalid = sorted(set(predictions) - set(labels))
        if invalid:
            raise ValueError(
                f"{csv_path} contains {len(invalid)} prediction IDs outside canonical labels; "
                f"first invalid example_id={invalid[0]}"
            )
        expected_ids = [
            example_id
            for example_id in labels
            if row_in_slice({"task_id": task_name.removeprefix("task_"), "example_id": str(example_id)})
        ]
        missing = sorted(set(expected_ids) - set(predictions))
        if missing:
            raise ValueError(
                f"{csv_path} is missing {len(missing)} required {SLICE_NAME} predictions; "
                f"first missing example_id={missing[0]}"
            )

        task_total = len(expected_ids)
        task_correct = sum(int(predictions[example_id] == labels[example_id]) for example_id in expected_ids)
        if task_total == 0:
            raise ValueError(f"No {SLICE_NAME} rows found in {csv_path}")
        per_task[task_name] = task_correct / task_total
        total += task_total
        correct += task_correct
    if total == 0:
        raise FileNotFoundError(f"No canonical task labels found for {prediction_dir}")
    return correct / total, per_task


def require_number(mapping: dict, key: str, source: Path) -> float:
    value = mapping.get(key)
    if not isinstance(value, (int, float)):
        raise ValueError(f"{source / 'summary.json'} missing numeric parameter_counts.{key}")
    return float(value)


def read_average_forgetting(summary: dict) -> float:
    history = summary.get("history", [])
    if not history:
        return 0.0

    best: dict[str, float] = {}
    final: dict[str, float] = {}
    for step in history:
        for task_name, accuracy in step.get("seen_task_accuracy", {}).items():
            best[task_name] = max(best.get(task_name, 0.0), float(accuracy))
            final[task_name] = float(accuracy)

    drops = [max(0.0, best[name] - final.get(name, best[name])) for name in best]
    return sum(drops) / len(drops) if drops else 0.0


def method_name_from_run(run_name: str) -> str:
    base_name = re.sub(r"_seed\d+$", "", run_name)
    return KNOWN_RUN_NAMES.get(base_name, base_name)


def experiment_from_summary(summary: dict, prediction_dir: Path) -> str | None:
    seed = summary.get("meta", {}).get("seed")
    if not isinstance(seed, int):
        raise ValueError(f"{prediction_dir / 'summary.json'} missing integer meta.seed")
    experiment = EXPERIMENTS_BY_SEED.get(seed)
    return experiment["name"] if experiment else None


def data_path_from_summary(summary: dict, prediction_dir: Path) -> Path:
    seed = summary.get("meta", {}).get("seed")
    if not isinstance(seed, int):
        raise ValueError(f"{prediction_dir / 'summary.json'} missing integer meta.seed")
    experiment = EXPERIMENTS_BY_SEED.get(seed)
    if experiment is None:
        raise ValueError(f"No canonical train/test labels registered for seed={seed}")
    return experiment["data"]


def discover_prediction_dirs(prediction_root: Path) -> dict[str, dict[str, Path]]:
    discovered: dict[str, dict[str, Path]] = {}
    for prediction_dir in sorted(prediction_root.glob("*/predictions")):
        if not prediction_dir.is_dir():
            continue
        summary = read_summary(prediction_dir)
        experiment_name = experiment_from_summary(summary, prediction_dir)
        if experiment_name is None:
            continue
        method_name = method_name_from_run(prediction_dir.parent.name)
        methods = discovered.setdefault(experiment_name, {})
        if method_name in methods:
            raise ValueError(
                f"Multiple prediction directories map to {experiment_name}.{method_name}: "
                f"{methods[method_name]} and {prediction_dir}"
            )
        methods[method_name] = prediction_dir
    return discovered


def requested_methods(train_scores_path: Path, discovered: dict[str, dict[str, Path]]) -> dict[str, set[str]]:
    if not train_scores_path.exists():
        return {experiment_name: set(methods) for experiment_name, methods in discovered.items()}

    data = json.loads(train_scores_path.read_text())
    experiments = data.get("experiments", {})
    requested: dict[str, set[str]] = {}
    for experiment_name, exp_data in experiments.items():
        if experiment_name.startswith("_") or not isinstance(exp_data, dict):
            continue
        methods = exp_data.get("results", exp_data)
        if not isinstance(methods, dict):
            continue
        requested[experiment_name] = {
            method_name
            for method_name in methods
            if not method_name.startswith("_")
        }
    return requested


def score_method(method_name: str, prediction_dir: Path) -> dict[str, float]:
    summary = read_summary(prediction_dir)
    truth_labels = read_truth_labels(data_path_from_summary(summary, prediction_dir))
    accuracy, per_task = read_accuracy(prediction_dir, truth_labels)
    params = summary.get("parameter_counts", {})
    if "share_parameters" in params:
        trainable = require_number(params, "share_parameters", prediction_dir)
        lora_stream = require_number(params, "independent_lora_stream_parameters", prediction_dir)
        compression = require_number(params, "compression_ratio_vs_lora_stream", prediction_dir)
        temporary = float(params.get("temporary_adaptation_parameters", trainable))
    elif method_name == "independent_lora":
        trainable = require_number(params, "trainable_parameters", prediction_dir)
        lora_stream = max(trainable, 1.0)
        compression = 1.0
        temporary = trainable
    else:
        trainable = require_number(params, "trainable_parameters", prediction_dir)
        lora_stream = require_number(params, "independent_lora_stream_parameters", prediction_dir) if (
            "independent_lora_stream_parameters" in params
        ) else max(trainable, 1.0)
        compression = float(params.get("compression_ratio_vs_lora_stream", 0.0))
        temporary = float(params.get("temporary_adaptation_parameters", trainable))

    return {
        "final_average_accuracy": accuracy * 100.0,
        "average_forgetting": read_average_forgetting(summary) * 100.0,
        "trainable_parameters": float(trainable),
        "temporary_adaptation_parameters": float(temporary),
        "parameter_fraction_vs_lora_stream": float(trainable) / float(lora_stream),
        "temporary_parameter_fraction_vs_lora_stream": float(temporary) / float(lora_stream),
        "compression_ratio_vs_lora_stream": float(compression),
        **{f"{task}_accuracy": value * 100.0 for task, value in per_task.items()},
    }


def build_scores(prediction_root: Path, train_scores_path: Path) -> dict:
    discovered = discover_prediction_dirs(prediction_root)
    requested = requested_methods(train_scores_path, discovered)
    output = {
        "_metadata": {
            "slice": SLICE_NAME,
            "split_rule": "Rows where (task_id * 1000003 + example_id) % 2 == 1.",
            "matched_to": str(train_scores_path),
        },
        "experiments": {},
    }

    for experiment_name, method_names in sorted(requested.items()):
        method_dirs = discovered.get(experiment_name, {})
        missing = sorted(method_names - set(method_dirs))
        if missing:
            raise FileNotFoundError(
                f"Missing prediction artifacts for {experiment_name}: {', '.join(missing)}"
            )
        output["experiments"][experiment_name] = {
            "_metadata": {"slice": SLICE_NAME},
            "results": {
                method_name: score_method(method_name, method_dirs[method_name])
                for method_name in sorted(method_names)
            },
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction-root", default="checkpoints")
    parser.add_argument("--train-scores", default="scoring/scores_train.json")
    parser.add_argument("--output", default="scoring/scores_test.json")
    args = parser.parse_args()

    output = build_scores(Path(args.prediction_root), Path(args.train_scores))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
