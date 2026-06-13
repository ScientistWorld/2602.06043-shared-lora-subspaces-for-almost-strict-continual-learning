"""Deterministic continual low-rank classification benchmark.

The paper evaluates Share on large pretrained backbones. This compact benchmark
keeps the same problem structure: a frozen base linear map is adapted to a
stream of related tasks by low-rank updates, with no replay during training.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch


@dataclass(frozen=True)
class TaskData:
    name: str
    x_train: torch.Tensor
    y_train: torch.Tensor
    x_test: torch.Tensor
    y_test: torch.Tensor


def make_tasks(
    *,
    seed: int = 13,
    num_tasks: int = 4,
    input_dim: int = 24,
    num_classes: int = 6,
    shared_rank: int = 3,
    train_per_task: int = 900,
    test_per_task: int = 500,
) -> tuple[torch.Tensor, list[TaskData], dict[str, int]]:
    """Create related tasks whose optima live mostly in one low-rank subspace."""

    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)

    base = torch.tensor(rng.normal(0.0, 0.35, size=(num_classes, input_dim)), dtype=torch.float32)
    shared_left = torch.tensor(rng.normal(0.0, 1.0, size=(num_classes, shared_rank)), dtype=torch.float32)
    shared_right = torch.tensor(rng.normal(0.0, 1.0, size=(shared_rank, input_dim)), dtype=torch.float32)

    tasks: list[TaskData] = []
    for task_id in range(num_tasks):
        coeff = torch.tensor(
            rng.normal(0.0, 0.9, size=(shared_rank, shared_rank)), dtype=torch.float32
        )
        specific = torch.tensor(
            rng.normal(0.0, 0.12, size=(num_classes, input_dim)), dtype=torch.float32
        )
        delta = shared_left @ coeff @ shared_right + specific
        # Make the frozen model useful but incomplete, so adaptation is measurable.
        teacher = base + 0.85 * delta

        shift = torch.tensor(rng.normal(0.0, 0.35, size=(input_dim,)), dtype=torch.float32)
        x_train = torch.tensor(rng.normal(0.0, 1.0, size=(train_per_task, input_dim)), dtype=torch.float32) + shift
        x_test = torch.tensor(rng.normal(0.0, 1.0, size=(test_per_task, input_dim)), dtype=torch.float32) + shift

        train_logits = x_train @ teacher.T + 0.15 * torch.randn(train_per_task, num_classes)
        test_logits = x_test @ teacher.T + 0.15 * torch.randn(test_per_task, num_classes)
        tasks.append(
            TaskData(
                name=f"task_{task_id}",
                x_train=x_train,
                y_train=train_logits.argmax(dim=1),
                x_test=x_test,
                y_test=test_logits.argmax(dim=1),
            )
        )

    meta = {
        "seed": seed,
        "num_tasks": num_tasks,
        "input_dim": input_dim,
        "num_classes": num_classes,
        "shared_rank": shared_rank,
        "train_per_task": train_per_task,
        "test_per_task": test_per_task,
    }
    return base, tasks, meta


def write_npz(path: str | Path, *, seed: int = 13) -> None:
    base, tasks, meta = make_tasks(seed=seed)
    out = {"base_weight": base.numpy(), **{f"meta_{k}": v for k, v in meta.items()}}
    for i, task in enumerate(tasks):
        out[f"x_train_{i}"] = task.x_train.numpy()
        out[f"y_train_{i}"] = task.y_train.numpy()
        out[f"x_test_{i}"] = task.x_test.numpy()
        out[f"y_test_{i}"] = task.y_test.numpy()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **out)


def load_npz(path: str | Path) -> tuple[torch.Tensor, list[TaskData], dict[str, int]]:
    arr = np.load(path)
    meta = {
        k.removeprefix("meta_"): int(arr[k])
        for k in arr.files
        if k.startswith("meta_") and k != "meta_seed"
    }
    meta["seed"] = int(arr["meta_seed"])
    base = torch.tensor(arr["base_weight"], dtype=torch.float32)
    tasks = []
    for i in range(meta["num_tasks"]):
        tasks.append(
            TaskData(
                name=f"task_{i}",
                x_train=torch.tensor(arr[f"x_train_{i}"], dtype=torch.float32),
                y_train=torch.tensor(arr[f"y_train_{i}"], dtype=torch.long),
                x_test=torch.tensor(arr[f"x_test_{i}"], dtype=torch.float32),
                y_test=torch.tensor(arr[f"y_test_{i}"], dtype=torch.long),
            )
        )
    return base, tasks, meta

