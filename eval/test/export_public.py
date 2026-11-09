"""Maintainer tool: write the public half of every stream to data/streams/manifest.json.

Run once (``python -m eval.test.export_public``) when the stream registry in
``eval/test/streams.py`` changes. The manifest holds public seeds, training
labels, development-stream validation labels and checksums of the public
arrays. It never contains test inputs, test labels or secret seeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from eval.test import streams as S


def _digest(array) -> str:
    return hashlib.sha256(array.tobytes()).hexdigest()[:24]


def _encode(labels) -> str:
    return "".join(chr(97 + int(v)) for v in labels)


def build_manifest() -> dict:
    manifest = {
        "format": 1,
        "num_classes": S.NUM_CLASSES,
        "input_dim": S.INPUT_DIM,
        "train_per_task": S.TRAIN_PER_TASK,
        "val_per_task": S.VAL_PER_TASK,
        "label_encoding": "one character per example: chr(97 + class_index)",
        "experiments": {
            name: {
                "num_tasks": spec["num_tasks"],
                "dev_streams": S.stream_ids("dev", name),
                "test_streams": S.stream_ids("test", name),
            }
            for name, spec in S.EXPERIMENTS.items()
        },
        "streams": {},
    }
    for sid in sorted(S.STREAMS):
        spec = S.STREAMS[sid]
        parts = S.public_and_labels(sid)
        entry = {
            "experiment": spec["experiment"],
            "role": spec["role"],
            "num_tasks": S.num_tasks(sid),
            "public_seed": spec["public_seed"],
            "y_train": [_encode(y) for y in parts["y_train"]],
            "checksums": {
                "base": _digest(parts["base"]),
                "x_train": [_digest(x) for x in parts["x_train"]],
            },
        }
        if spec["role"] == "dev":
            entry["y_val"] = [_encode(y) for y in parts["y_val"]]
            entry["checksums"]["x_val"] = [_digest(x) for x in parts["x_val"]]
        manifest["streams"][sid] = entry
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/streams/manifest.json")
    parser.add_argument("--check", action="store_true", help="only verify the existing manifest")
    args = parser.parse_args()
    manifest = build_manifest()
    out = Path(args.output)
    text = json.dumps(manifest, indent=1) + "\n"
    if args.check:
        if not out.exists() or out.read_text() != text:
            raise SystemExit(f"{out} does not match the registry in eval/test/streams.py")
        print(f"{out} matches the registry")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
