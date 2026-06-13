"""Score the visible evaluation slice from saved prediction artifacts.

This module deliberately reads only generic prediction CSVs and summary JSON
metadata. It does not import method code, so any future method that writes the
same artifacts can be scored here.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


SLICE_NAME = "train"
EXPERIMENT_BY_SEED = {
    13: "synthetic_continual_low_rank",
    21: "synthetic_continual_low_rank_seed21",
}
KNOWN_RUN_NAMES = {
    "share": "share",
    "lora": "independent_lora",
    "frozen": "frozen_backbone",
}


def row_in_slice(row: dict[str, str]) -> bool:
    """Split each task's prediction rows into a stable visible half."""

    task_id = int(row.get("task_id", 0))
    example_id = int(row["example_id"])
    return ((task_id * 1_000_003 + example_id) % 2) == 0


def read_summary(prediction_dir: Path) -> dict:
    path = prediction_dir / "summary.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing required parameter metadata: {path}")
    return json.loads(path.read_text())


def read_accuracy(prediction_dir: Path) -> tuple[float, dict[str, float]]:
    per_task = {}
    total = 0
    correct = 0
    for csv_path in sorted(prediction_dir.glob("task_*.csv")):
        task_total = 0
        task_correct = 0
        with csv_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                if not row_in_slice(row):
                    continue
                task_total += 1
                task_correct += int(row["prediction"] == row["label"])
        if task_total == 0:
            raise ValueError(f"No {SLICE_NAME} rows found in {csv_path}")
        per_task[csv_path.stem] = task_correct / task_total
        total += task_total
        correct += task_correct
    if total == 0:
        raise FileNotFoundError(f"No task_*.csv files found in {prediction_dir}")
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
    return EXPERIMENT_BY_SEED.get(seed)


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


def score_method(method_name: str, prediction_dir: Path) -> dict[str, float]:
    accuracy, per_task = read_accuracy(prediction_dir)
    summary = read_summary(prediction_dir)
    params = summary.get("parameter_counts", {})
    if "share_parameters" in params:
        trainable = require_number(params, "share_parameters", prediction_dir)
        lora_stream = require_number(params, "independent_lora_stream_parameters", prediction_dir)
        compression = require_number(params, "compression_ratio_vs_lora_stream", prediction_dir)
    elif method_name == "independent_lora":
        trainable = require_number(params, "trainable_parameters", prediction_dir)
        lora_stream = max(trainable, 1.0)
        compression = 1.0
    else:
        trainable = require_number(params, "trainable_parameters", prediction_dir)
        lora_stream = require_number(params, "independent_lora_stream_parameters", prediction_dir) if (
            "independent_lora_stream_parameters" in params
        ) else max(trainable, 1.0)
        compression = float(params.get("compression_ratio_vs_lora_stream", 0.0))

    return {
        "final_average_accuracy": accuracy * 100.0,
        "average_forgetting": read_average_forgetting(summary) * 100.0,
        "trainable_parameters": float(trainable),
        "parameter_fraction_vs_lora_stream": float(trainable) / float(lora_stream),
        "compression_ratio_vs_lora_stream": float(compression),
        **{f"{task}_accuracy": value * 100.0 for task, value in per_task.items()},
    }


def build_scores(prediction_root: Path) -> dict:
    discovered = discover_prediction_dirs(prediction_root)
    output = {
        "_metadata": {
            "slice": SLICE_NAME,
            "split_rule": "Rows where (task_id * 1000003 + example_id) % 2 == 0.",
        },
        "experiments": {},
    }
    for experiment_name, method_dirs in sorted(discovered.items()):
        output["experiments"][experiment_name] = {
            "_metadata": {"slice": SLICE_NAME},
            "results": {
                method_name: score_method(method_name, prediction_dir)
                for method_name, prediction_dir in sorted(method_dirs.items())
            },
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction-root", default="checkpoints")
    parser.add_argument("--output", default="scoring/scores_train.json")
    args = parser.parse_args()

    output = build_scores(Path(args.prediction_root))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
