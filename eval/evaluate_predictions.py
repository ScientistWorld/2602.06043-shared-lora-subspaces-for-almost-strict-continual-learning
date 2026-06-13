"""Evaluate prediction artifacts without importing method code."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_accuracy(prediction_dir: Path) -> tuple[float, dict[str, float]]:
    per_task = {}
    total = 0
    correct = 0
    for csv_path in sorted(prediction_dir.glob("task_*.csv")):
        task_total = 0
        task_correct = 0
        with csv_path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                task_total += 1
                task_correct += int(row["prediction"] == row["label"])
        if task_total == 0:
            raise ValueError(f"No predictions in {csv_path}")
        per_task[csv_path.stem] = task_correct / task_total
        total += task_total
        correct += task_correct
    if total == 0:
        raise FileNotFoundError(f"No task_*.csv files found in {prediction_dir}")
    return correct / total, per_task


def read_summary(prediction_dir: Path) -> dict:
    path = prediction_dir / "summary.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing required parameter metadata: {path}")
    return json.loads(path.read_text())


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


def add_experiment(output: dict, experiment_name: str, directories: list[tuple[str, Path]]) -> None:
    results = {}
    for name, directory in [
        *directories,
    ]:
        if not directory.exists():
            continue
        accuracy, per_task = read_accuracy(directory)
        summary = read_summary(directory)
        params = summary.get("parameter_counts", {})
        if name == "share":
            trainable = require_number(params, "share_parameters", directory)
            lora_stream = require_number(params, "independent_lora_stream_parameters", directory)
            compression = require_number(params, "compression_ratio_vs_lora_stream", directory)
            temporary = float(params.get("temporary_adaptation_parameters", trainable))
        elif name == "independent_lora":
            trainable = require_number(params, "trainable_parameters", directory)
            lora_stream = max(trainable, 1)
            compression = 1.0
            temporary = trainable
        else:
            trainable = require_number(params, "trainable_parameters", directory)
            lora_stream = require_number(params, "independent_lora_stream_parameters", directory) if (
                "independent_lora_stream_parameters" in params
            ) else max(trainable, 1)
            compression = float(params.get("compression_ratio_vs_lora_stream", 0.0))
            temporary = float(params.get("temporary_adaptation_parameters", trainable))
        results[name] = {
            "final_average_accuracy": accuracy * 100.0,
            "average_forgetting": read_average_forgetting(summary) * 100.0,
            "trainable_parameters": float(trainable),
            "temporary_adaptation_parameters": float(temporary),
            "parameter_fraction_vs_lora_stream": float(trainable) / float(lora_stream),
            "temporary_parameter_fraction_vs_lora_stream": float(temporary) / float(lora_stream),
            "compression_ratio_vs_lora_stream": float(compression),
            **{f"{task}_accuracy": value * 100.0 for task, value in per_task.items()},
        }
    if results:
        output["experiments"][experiment_name] = {"results": results}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--share-dir", default="checkpoints/share/predictions")
    parser.add_argument("--lora-dir", default="checkpoints/lora/predictions")
    parser.add_argument("--frozen-dir", default="checkpoints/frozen/predictions")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()

    output = {"experiments": {}}
    add_experiment(
        output,
        "synthetic_continual_low_rank",
        [
            ("share", Path(args.share_dir)),
            ("independent_lora", Path(args.lora_dir)),
            ("frozen_backbone", Path(args.frozen_dir)),
        ],
    )
    add_experiment(
        output,
        "synthetic_continual_low_rank_seed21",
        [
            ("share", Path("checkpoints/share_seed21/predictions")),
            ("independent_lora", Path("checkpoints/lora_seed21/predictions")),
            ("frozen_backbone", Path("checkpoints/frozen_seed21/predictions")),
        ],
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
