"""Independent LoRA and frozen-backbone baselines for the synthetic benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn.functional as F

from data.synthetic_tasks import load_npz, write_npz


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


def write_predictions(output_dir: Path, task_id: int, pred: torch.Tensor, label: torch.Tensor) -> None:
    rows = ["task_id,example_id,prediction,label"]
    for i, (p, y) in enumerate(zip(pred.cpu().numpy(), label.cpu().numpy(), strict=True)):
        rows.append(f"{task_id},{i},{int(p)},{int(y)}")
    (output_dir / f"task_{task_id}.csv").write_text("\n".join(rows) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["lora", "frozen"], default="lora")
    parser.add_argument("--data", default="data/synthetic_share_tasks.npz")
    parser.add_argument("--output-dir", default="checkpoints/lora/predictions")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--rank", type=int, default=6)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--lr", type=float, default=0.03)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        write_npz(data_path, seed=args.seed)
    base_weight, tasks, meta = load_npz(data_path)
    torch.manual_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for task_id, task in enumerate(tasks):
        if args.kind == "frozen":
            pred = (task.x_test @ base_weight.T).argmax(dim=1)
        else:
            adapter = LoRAAdapter(base_weight, args.rank)
            train(adapter, task.x_train, task.y_train, args.steps, args.lr)
            pred = adapter(task.x_test).argmax(dim=1)
        write_predictions(output_dir, task_id, pred, task.y_test)

    params = 0 if args.kind == "frozen" else len(tasks) * args.rank * sum(base_weight.shape)
    summary = {"method": args.kind, "meta": meta, "parameter_counts": {"trainable_parameters": int(params)}}
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

