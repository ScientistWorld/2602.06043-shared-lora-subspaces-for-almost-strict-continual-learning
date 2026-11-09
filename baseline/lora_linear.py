"""Baselines for the continual low-rank adaptation benchmark.

* ``independent_lora`` -- one rank-12 LoRA adapter per task, trained and stored
  separately (the paper's non-continual LoRA reference; it stores one full
  adapter per task, so it exceeds the benchmark's continual-learning budget).
* ``frozen_backbone`` -- no adaptation.
* ``sequential_lora`` -- a single rank-12 LoRA adapter fine-tuned on each task
  in turn with no per-task state (the sequential fine-tuning baseline).
* ``independent_rank1`` -- one rank-1 adapter per task: the largest
  independent per-task adapter that fits the per-task budget.

Each writes deployed-state snapshots after every task in the same format as any
method (see briefing/evaluation.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
import torch.nn.functional as F

from data.streams import load_manifest, load_stream, save_snapshot, stream_ids


class LoRAAdapter(torch.nn.Module):
    def __init__(self, base_weight: torch.Tensor, rank: int):
        super().__init__()
        classes, dim = base_weight.shape
        self.register_buffer("base_weight", base_weight.clone())
        self.a = torch.nn.Parameter(0.02 * torch.randn(rank, dim))
        self.b = torch.nn.Parameter(0.02 * torch.randn(classes, rank))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x @ (self.base_weight + self.b @ self.a).T


def train(module: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, steps: int, lr: float) -> None:
    opt = torch.optim.AdamW(module.parameters(), lr=lr, weight_decay=1e-3)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        loss = F.cross_entropy(module(x), y)
        loss.backward()
        opt.step()


def stream_seed(seed: int, stream_id: str) -> int:
    return int(hashlib.sha256(f"{seed}:{stream_id}".encode()).hexdigest()[:8], 16)


def run_stream(kind: str, stream, args: argparse.Namespace, output_root: Path) -> None:
    torch.manual_seed(stream_seed(args.seed, stream.stream_id))
    base_weight = torch.tensor(stream.base)
    state: dict = {}
    sequential = LoRAAdapter(base_weight, args.rank) if kind == "sequential_lora" else None
    for t, task in enumerate(stream.tasks):
        x, y = torch.tensor(task.x_train), torch.tensor(task.y_train)
        if kind in ("independent_lora", "independent_rank1"):
            adapter = LoRAAdapter(base_weight, args.rank if kind == "independent_lora" else 1)
            train(adapter, x, y, args.steps, args.lr)
            state[f"task_{t}_A"] = adapter.a.detach().T.numpy().copy()  # (input_dim, rank)
            state[f"task_{t}_B"] = adapter.b.detach().numpy().copy()  # (classes, rank)
        elif kind == "sequential_lora":
            train(sequential, x, y, args.steps, args.lr)
            state = {"shared_A": sequential.a.detach().T.numpy().copy(), "shared_B": sequential.b.detach().numpy().copy()}
        save_snapshot(output_root, stream.stream_id, t, state)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["independent_lora", "frozen_backbone", "sequential_lora", "independent_rank1"],
                        default="independent_lora")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--roles", nargs="+", default=["dev", "test"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--rank", type=int, default=12)
    parser.add_argument("--steps", type=int, default=700)
    parser.add_argument("--lr", type=float, default=0.03)
    args = parser.parse_args()

    torch.set_num_threads(1)
    output_root = Path(args.output_root or f"checkpoints/{args.kind}")
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "run_config.json").write_text(json.dumps(vars(args), indent=2) + "\n")
    manifest = load_manifest()
    for role in args.roles:
        for sid in stream_ids(role=role, manifest=manifest):
            run_stream(args.kind, load_stream(sid, manifest=manifest), args, output_root)
            print(f"{args.kind}: finished {sid}", flush=True)


if __name__ == "__main__":
    main()
