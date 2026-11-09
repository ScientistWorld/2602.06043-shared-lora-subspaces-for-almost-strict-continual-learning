"""Frozen development evaluation streams, independent of method-owned data.

A *stream* is a frozen base linear classifier ``W0`` (classes x input_dim) plus
an ordered sequence of classification tasks. Every task comes with labelled
training examples and a labelled validation split, scored by ``eval/train``.
This loader contains only the development streams and has no test dependency.

Inputs are regenerated deterministically from public seeds; labels are stored
in ``eval/train/manifest.json``. Every regenerated array is checked against a
stored checksum, so a numerical drift fails loudly instead of silently pairing
inputs with the wrong labels.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"

# Public derivation (must stay identical to the stream generator that wrote the manifest).
_PUB_BASE, _PUB_SHIFT, _PUB_X_TRAIN, _PUB_X_VAL = 0, 1, 2, 3
_BASE_STD = 0.35
_SHIFT_STD = 0.35


@dataclass(frozen=True)
class Task:
    index: int
    x_train: np.ndarray
    y_train: np.ndarray
    x_val: np.ndarray | None = None
    y_val: np.ndarray | None = None


@dataclass(frozen=True)
class Stream:
    stream_id: str
    experiment: str
    role: str
    base: np.ndarray
    tasks: list[Task]

    @property
    def num_classes(self) -> int:
        return int(self.base.shape[0])

    @property
    def input_dim(self) -> int:
        return int(self.base.shape[1])


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing stream manifest: {path}")
    return json.loads(path.read_text())


def stream_ids(role: str | None = None, experiment: str | None = None, manifest: dict | None = None) -> list[str]:
    manifest = manifest or load_manifest()
    return sorted(
        sid
        for sid, entry in manifest["streams"].items()
        if (role is None or entry["role"] == role) and (experiment is None or entry["experiment"] == experiment)
    )


def _rng(seed: int, component: int, task: int = 0) -> np.random.Generator:
    digest = hashlib.sha256(f"{int(seed)}:{int(component)}:{int(task)}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest, "little"))


def _inputs(seed: int, task: int, component: int, count: int, dim: int) -> np.ndarray:
    shift = _rng(seed, _PUB_SHIFT, task).normal(0.0, _SHIFT_STD, size=(dim,))
    noise = _rng(seed, component, task).standard_normal((count, dim))
    return (noise + shift).astype(np.float32)


def _check(array: np.ndarray, expected: str, what: str) -> None:
    got = hashlib.sha256(array.tobytes()).hexdigest()[: len(expected)]
    if got != expected:
        raise RuntimeError(f"Checksum mismatch for {what}: regenerated inputs do not match the stored labels")


def _decode(text: str) -> np.ndarray:
    return np.frombuffer(text.encode("ascii"), dtype=np.uint8).astype(np.int64) - 97


def load_stream(stream_id: str, *, manifest: dict | None = None) -> Stream:
    manifest = manifest or load_manifest()
    entry = manifest["streams"][stream_id]
    classes, dim = int(manifest["num_classes"]), int(manifest["input_dim"])
    seed = int(entry["public_seed"])
    base = _rng(seed, _PUB_BASE).normal(0.0, _BASE_STD, size=(classes, dim)).astype(np.float32)
    _check(base, entry["checksums"]["base"], f"{stream_id} base weight")

    tasks = []
    for t in range(int(entry["num_tasks"])):
        x_train = _inputs(seed, t, _PUB_X_TRAIN, int(manifest["train_per_task"]), dim)
        _check(x_train, entry["checksums"]["x_train"][t], f"{stream_id} task {t} training inputs")
        y_train = _decode(entry["y_train"][t])
        x_val = y_val = None
        if "y_val" in entry:
            x_val = _inputs(seed, t, _PUB_X_VAL, int(manifest["val_per_task"]), dim)
            _check(x_val, entry["checksums"]["x_val"][t], f"{stream_id} task {t} validation inputs")
            y_val = _decode(entry["y_val"][t])
        tasks.append(Task(index=t, x_train=x_train, y_train=y_train, x_val=x_val, y_val=y_val))
    return Stream(stream_id=stream_id, experiment=entry["experiment"], role=entry["role"], base=base, tasks=tasks)
