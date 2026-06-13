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
    return json.loads(path.read_text()) if path.exists() else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--share-dir", default="checkpoints/share/predictions")
    parser.add_argument("--lora-dir", default="checkpoints/lora/predictions")
    parser.add_argument("--frozen-dir", default="checkpoints/frozen/predictions")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()

    output = {"experiments": {"synthetic_continual_low_rank": {"results": {}}}}
    for name, directory in [
        ("share", Path(args.share_dir)),
        ("independent_lora", Path(args.lora_dir)),
        ("frozen_backbone", Path(args.frozen_dir)),
    ]:
        if not directory.exists():
            continue
        accuracy, per_task = read_accuracy(directory)
        summary = read_summary(directory)
        params = summary.get("parameter_counts", {})
        if name == "share":
            trainable = params.get("share_parameters", 0)
            lora_stream = params.get("independent_lora_stream_parameters", 1)
            compression = params.get("compression_ratio_vs_lora_stream", 0.0)
        elif name == "independent_lora":
            trainable = params.get("trainable_parameters", 0)
            lora_stream = max(trainable, 1)
            compression = 1.0
        else:
            trainable = params.get("trainable_parameters", 0)
            lora_stream = 1
            compression = 0.0
        output["experiments"]["synthetic_continual_low_rank"]["results"][name] = {
            "final_average_accuracy": accuracy * 100.0,
            "trainable_parameters": float(trainable),
            "parameter_fraction_vs_lora_stream": float(trainable) / float(lora_stream),
            "compression_ratio_vs_lora_stream": float(compression),
            **{f"{task}_accuracy": value * 100.0 for task, value in per_task.items()},
        }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
