"""Share for a frozen linear layer adapted continually with low-rank updates.

Implements the paper's algorithmic steps (Sec. 3.2, Algorithm 1):

1. Initialization: train a LoRA adapter on the first task, stack its rank
   vectors, center them and take the top-k right singular vectors as the
   principal factors (alpha for A, beta for B); learn task coefficients
   eps_alpha, eps_beta (k x p) in that frozen basis.
2. Continual adaptation: for every new task, initialise phi temporary basis
   vectors from the top-phi principal factors plus fresh coefficients, and
   optimise both on the current task's data only (no replay).
3. Merging & finetuning: reconstruct every previous task adapter from the
   retained shared state (alpha, beta, coefficients), stack them with the new
   temporary adapter, recompute the principal factors by (centered) SVD and
   analytically recompute all task coefficients with the pseudoinverse
   projection; then finetune the *current* task's coefficients on the current
   task's data (Algorithm 1, lines 40-41). Earlier tasks' coefficients are only
   ever recalculated analytically -- their data is never revisited (finetuning
   them with old data would be the relaxed Share-full setting).

After each task the deployed Share state -- shared factors plus per-task
coefficients for the tasks seen so far -- is saved as a snapshot; the
evaluator reconstructs every task's weight update from it.
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
    params = [p for p in module.parameters() if p.requires_grad]
    if steps <= 0 or not params:
        return
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=1e-3)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        loss = F.cross_entropy(module(x), y)
        loss.backward()
        opt.step()


def principal_factors(
    adapters: list[tuple[torch.Tensor, torch.Tensor]], k: int, center: bool = True
) -> tuple[torch.Tensor, torch.Tensor]:
    a_rows = torch.cat([a for a, _ in adapters], dim=0)
    b_cols = torch.cat([b.T for _, b in adapters], dim=0)
    if center:
        a_rows = a_rows - a_rows.mean(dim=0, keepdim=True)
        b_cols = b_cols - b_cols.mean(dim=0, keepdim=True)
    _, _, va = torch.linalg.svd(a_rows, full_matrices=False)
    _, _, vb = torch.linalg.svd(b_cols, full_matrices=False)
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


def share_state(alpha: torch.Tensor, beta: torch.Tensor, coeffs: list[tuple[torch.Tensor, torch.Tensor]]) -> dict:
    """Deployed state: shared factors plus each seen task's coefficients."""

    state = {"shared_A": alpha.detach().numpy(), "shared_B": beta.detach().numpy()}
    for j, (eps_alpha, eps_beta) in enumerate(coeffs):
        state[f"task_{j}_A"] = eps_alpha.detach().numpy()
        state[f"task_{j}_B"] = eps_beta.detach().numpy()
    return state


def finetune_current(base_weight, alpha, beta, coeffs, t, x, y, args) -> list:
    """Step 3 finetuning: optimise task t's coefficients in the merged basis on task t's data."""

    if args.finetune_steps <= 0:
        return coeffs
    module = ShareTaskAdapter(base_weight, alpha, beta, args.pseudo_rank, train_basis=False)
    with torch.no_grad():
        module.eps_alpha.copy_(coeffs[t][0])
        module.eps_beta.copy_(coeffs[t][1])
    train_module(module, x, y, steps=args.finetune_steps, lr=args.lr / args.finetune_lr_divisor)
    coeffs = list(coeffs)
    coeffs[t] = (module.eps_alpha.detach().clone(), module.eps_beta.detach().clone())
    return coeffs


def stream_seed(seed: int, stream_id: str) -> int:
    return int(hashlib.sha256(f"{seed}:{stream_id}".encode()).hexdigest()[:8], 16)


def train_share_stream(stream, args: argparse.Namespace, output_root: Path) -> None:
    torch.manual_seed(stream_seed(args.seed, stream.stream_id))
    base_weight = torch.tensor(stream.base)
    xs = [torch.tensor(task.x_train) for task in stream.tasks]
    ys = [torch.tensor(task.y_train) for task in stream.tasks]

    # Step 1: initialise the principal subspace from a LoRA trained on the first task.
    first = LoRAAdapter(base_weight, args.lora_rank)
    train_module(first, xs[0], ys[0], steps=args.lora_steps, lr=args.lr)
    alpha, beta = principal_factors([first.factors()], args.k)
    initial = ShareTaskAdapter(base_weight, alpha, beta, args.pseudo_rank, train_basis=False)
    train_module(initial, xs[0], ys[0], steps=args.share_steps, lr=args.lr)
    coeffs = project_coefficients([initial.factors()], alpha, beta)
    coeffs = finetune_current(base_weight, alpha, beta, coeffs, 0, xs[0], ys[0], args)
    save_snapshot(output_root, stream.stream_id, 0, share_state(alpha, beta, coeffs))

    for t in range(1, len(stream.tasks)):
        # Step 2: temporary expansion from the top-phi factors, trained on task t only.
        temp = ShareTaskAdapter(base_weight, alpha[:, : args.phi], beta[:, : args.phi], args.pseudo_rank, train_basis=True)
        train_module(temp, xs[t], ys[t], steps=args.share_steps, lr=args.lr)
        # Step 3: merge previous (reconstructed) adapters with the new one; reproject coefficients;
        # finetune the current task's coefficients on its own data (no replay).
        merge_adapters = reconstruct_adapters(alpha, beta, coeffs)
        merge_adapters.append(temp.factors())
        alpha, beta = principal_factors(merge_adapters, args.k)
        coeffs = project_coefficients(merge_adapters, alpha, beta)
        coeffs = finetune_current(base_weight, alpha, beta, coeffs, t, xs[t], ys[t], args)
        save_snapshot(output_root, stream.stream_id, t, share_state(alpha, beta, coeffs))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", default="checkpoints/share")
    parser.add_argument("--roles", nargs="+", default=["dev", "test"], help="which manifest streams to train on")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--lora-rank", type=int, default=12)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--pseudo-rank", type=int, default=4)
    parser.add_argument("--phi", type=int, default=2)
    parser.add_argument("--lora-steps", type=int, default=700)
    parser.add_argument("--share-steps", type=int, default=1500)
    parser.add_argument("--lr", type=float, default=0.03)
    parser.add_argument("--finetune-steps", type=int, default=700, help="Step 3 current-task coefficient finetuning")
    parser.add_argument("--finetune-lr-divisor", type=float, default=3.0)
    args = parser.parse_args()

    torch.set_num_threads(1)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "run_config.json").write_text(json.dumps({"method": "share", **vars(args)}, indent=2) + "\n")
    manifest = load_manifest()
    for role in args.roles:
        for sid in stream_ids(role=role, manifest=manifest):
            train_share_stream(load_stream(sid, manifest=manifest), args, output_root)
            print(f"share: finished {sid}", flush=True)


if __name__ == "__main__":
    main()
