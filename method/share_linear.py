"""Share for frozen linear layers with low-rank adapters.

This implements the paper's algorithmic steps: LoRA initialization, SVD-derived
principal A/B factor subspaces, temporary basis adaptation, SVD merging, and
analytical coefficient reprojection.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn.functional as F

from data.synthetic_tasks import load_npz, write_npz


def _accuracy(logits: torch.Tensor, y: torch.Tensor) -> float:
    return float((logits.argmax(dim=1) == y).float().mean().item())


class LoRAAdapter(torch.nn.Module):
    def __init__(self, base_weight: torch.Tensor, rank: int):
        super().__init__()
        classes, dim = base_weight.shape
        self.register_buffer("base_weight", base_weight.clone())
        self.a = torch.nn.Parameter(0.02 * torch.randn(rank, dim))
        self.b = torch.nn.Parameter(0.02 * torch.randn(classes, rank))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x @ (self.base_weight + self.b @ self.a).T

    def factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        return self.a.detach().clone(), self.b.detach().clone()


class ShareTaskAdapter(torch.nn.Module):
    def __init__(
        self,
        base_weight: torch.Tensor,
        alpha: torch.Tensor,
        beta: torch.Tensor,
        pseudo_rank: int,
        train_basis: bool,
    ):
        super().__init__()
        self.register_buffer("base_weight", base_weight.clone())
        self.alpha = torch.nn.Parameter(alpha.clone(), requires_grad=train_basis)
        self.beta = torch.nn.Parameter(beta.clone(), requires_grad=train_basis)
        k = alpha.shape[1]
        self.eps_alpha = torch.nn.Parameter(0.02 * torch.randn(k, pseudo_rank))
        self.eps_beta = torch.nn.Parameter(0.02 * torch.randn(k, pseudo_rank))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        a_hat = (self.alpha @ self.eps_alpha).T
        b_hat = self.beta @ self.eps_beta
        return x @ (self.base_weight + b_hat @ a_hat).T

    def factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        return (self.alpha @ self.eps_alpha).T.detach(), (self.beta @ self.eps_beta).detach()


def train_module(module: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, *, steps: int, lr: float) -> None:
    opt = torch.optim.AdamW([p for p in module.parameters() if p.requires_grad], lr=lr, weight_decay=1e-3)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        loss = F.cross_entropy(module(x), y)
        loss.backward()
        opt.step()


def principal_factors(adapters: list[tuple[torch.Tensor, torch.Tensor]], k: int) -> tuple[torch.Tensor, torch.Tensor]:
    a_rows = torch.cat([a for a, _ in adapters], dim=0)
    b_cols = torch.cat([b.T for _, b in adapters], dim=0)
    a_centered = a_rows - a_rows.mean(dim=0, keepdim=True)
    b_centered = b_cols - b_cols.mean(dim=0, keepdim=True)
    _, _, va = torch.linalg.svd(a_centered, full_matrices=False)
    _, _, vb = torch.linalg.svd(b_centered, full_matrices=False)
    return va[:k].T.contiguous(), vb[:k].T.contiguous()


def project_coefficients(
    adapters: list[tuple[torch.Tensor, torch.Tensor]], alpha: torch.Tensor, beta: torch.Tensor
) -> list[tuple[torch.Tensor, torch.Tensor]]:
    coeffs = []
    alpha_pinv = torch.linalg.pinv(alpha)
    beta_pinv = torch.linalg.pinv(beta)
    for a_hat, b_hat in adapters:
        coeffs.append((alpha_pinv @ a_hat.T, beta_pinv @ b_hat))
    return coeffs


def reconstruct_adapters(
    alpha: torch.Tensor, beta: torch.Tensor, coeffs: list[tuple[torch.Tensor, torch.Tensor]]
) -> list[tuple[torch.Tensor, torch.Tensor]]:
    """Reconstruct task adapters from the retained Share state before merging."""

    adapters = []
    for eps_alpha, eps_beta in coeffs:
        adapters.append(((alpha @ eps_alpha).T.detach(), (beta @ eps_beta).detach()))
    return adapters


def logits_from_coeffs(
    base_weight: torch.Tensor,
    alpha: torch.Tensor,
    beta: torch.Tensor,
    coeff: tuple[torch.Tensor, torch.Tensor],
    x: torch.Tensor,
) -> torch.Tensor:
    eps_alpha, eps_beta = coeff
    a_hat = (alpha @ eps_alpha).T
    b_hat = beta @ eps_beta
    return x @ (base_weight + b_hat @ a_hat).T


def train_share(args: argparse.Namespace) -> dict:
    data_path = Path(args.data)
    if not data_path.exists():
        write_npz(data_path, seed=args.seed)
    base_weight, tasks, meta = load_npz(data_path)

    torch.manual_seed(args.seed)
    first = LoRAAdapter(base_weight, args.lora_rank)
    train_module(first, tasks[0].x_train, tasks[0].y_train, steps=args.lora_steps, lr=args.lr)
    seed_adapters = [first.factors()]
    alpha, beta = principal_factors(seed_adapters, args.k)

    initial = ShareTaskAdapter(base_weight, alpha, beta, args.pseudo_rank, train_basis=False)
    train_module(initial, tasks[0].x_train, tasks[0].y_train, steps=args.share_steps, lr=args.lr)
    coeffs = project_coefficients([initial.factors()], alpha, beta)

    history = []
    for task_index, task in enumerate(tasks):
        if task_index > 0:
            tmp_alpha = alpha[:, : args.phi].clone()
            tmp_beta = beta[:, : args.phi].clone()
            temp = ShareTaskAdapter(base_weight, tmp_alpha, tmp_beta, args.pseudo_rank, train_basis=True)
            train_module(temp, task.x_train, task.y_train, steps=args.share_steps, lr=args.lr)
            merge_adapters = reconstruct_adapters(alpha, beta, coeffs)
            merge_adapters.append(temp.factors())
            alpha, beta = principal_factors(merge_adapters, args.k)
            coeffs = project_coefficients(merge_adapters, alpha, beta)

        seen_scores = {}
        for j in range(task_index + 1):
            logits = logits_from_coeffs(base_weight, alpha, beta, coeffs[j], tasks[j].x_test)
            seen_scores[tasks[j].name] = _accuracy(logits, tasks[j].y_test)
        history.append({"after_task": task.name, "seen_task_accuracy": seen_scores})

    predictions_dir = Path(args.output_dir)
    predictions_dir.mkdir(parents=True, exist_ok=True)
    for j, task in enumerate(tasks):
        logits = logits_from_coeffs(base_weight, alpha, beta, coeffs[j], task.x_test)
        pred = logits.argmax(dim=1).cpu().numpy()
        rows = ["task_id,example_id,prediction,label"]
        for i, (p, y) in enumerate(zip(pred, task.y_test.cpu().numpy(), strict=True)):
            rows.append(f"{j},{i},{int(p)},{int(y)}")
        (predictions_dir / f"{task.name}.csv").write_text("\n".join(rows) + "\n")

    deployed_share = int(alpha.numel() + beta.numel() + len(tasks) * args.k * args.pseudo_rank * 2)
    temporary_adaptation = int(args.phi * (sum(base_weight.shape) + 2 * args.pseudo_rank))
    trainable_lora_stream = int(len(tasks) * args.lora_rank * sum(base_weight.shape))
    summary = {
        "method": "share",
        "meta": meta,
        "hyperparameters": vars(args),
        "history": history,
        "parameter_counts": {
            "share_parameters": deployed_share,
            "temporary_adaptation_parameters": temporary_adaptation,
            "independent_lora_stream_parameters": trainable_lora_stream,
            "compression_ratio_vs_lora_stream": trainable_lora_stream / deployed_share,
        },
    }
    (predictions_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/synthetic_share_tasks.npz")
    parser.add_argument("--output-dir", default="checkpoints/share/predictions")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--lora-rank", type=int, default=12)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--pseudo-rank", type=int, default=4)
    parser.add_argument("--phi", type=int, default=2)
    parser.add_argument("--lora-steps", type=int, default=700)
    parser.add_argument("--share-steps", type=int, default=1500)
    parser.add_argument("--lr", type=float, default=0.03)
    args = parser.parse_args()
    train_share(args)


if __name__ == "__main__":
    main()
