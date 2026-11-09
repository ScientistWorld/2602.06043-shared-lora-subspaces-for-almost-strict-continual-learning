"""Variant methods and shortcut constructions for the hardening audit.

Every function writes a run directory in the benchmark's artifact format
(``<run>/<stream_id>/after_task_XX.npz``) so it is scored by the unmodified
evaluators. Share variants reuse the reference implementation's building
blocks from ``method/share_linear.py``.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from data.streams import save_snapshot, snapshot_path
from method.share_linear import (
    LoRAAdapter,
    ShareTaskAdapter,
    principal_factors,
    project_coefficients,
    reconstruct_adapters,
    share_state,
    stream_seed,
    train_module,
)


# --------------------------------------------------------------------------- Share variants
def share_variant_stream(
    stream,
    out_root: Path,
    *,
    seed: int,
    lora_rank: int = 12,
    k: int = 8,
    p: int = 4,
    phi: int = 2,
    lora_steps: int = 700,
    share_steps: int = 1500,
    lr: float = 0.03,
    refit_steps: int = 0,
    center_merges: bool = True,
) -> None:
    """The reference Share loop with the paper's optional switches.

    refit_steps > 0 enables Algorithm 1's optional step (lines 40-41): after the
    coefficients are recalculated, the *current* task's coefficients are
    optimised on the current task's data (no replay). center_merges=False uses
    the main-text merge (Eq. 2, uncentered SVD) instead of the appendix's
    centered SVD; initialisation stays centered.
    """

    torch.manual_seed(stream_seed(seed, stream.stream_id))
    base = torch.tensor(stream.base)
    xs = [torch.tensor(t.x_train) for t in stream.tasks]
    ys = [torch.tensor(t.y_train) for t in stream.tasks]

    def refit(t: int, alpha, beta, coeffs):
        if refit_steps <= 0:
            return coeffs
        module = ShareTaskAdapter(base, alpha, beta, p, train_basis=False)
        with torch.no_grad():
            module.eps_alpha.copy_(coeffs[t][0])
            module.eps_beta.copy_(coeffs[t][1])
        train_module(module, xs[t], ys[t], steps=refit_steps, lr=lr / 3)
        coeffs = list(coeffs)
        coeffs[t] = (module.eps_alpha.detach().clone(), module.eps_beta.detach().clone())
        return coeffs

    first = LoRAAdapter(base, lora_rank)
    train_module(first, xs[0], ys[0], steps=lora_steps, lr=lr)
    alpha, beta = principal_factors([first.factors()], k)
    initial = ShareTaskAdapter(base, alpha, beta, p, train_basis=False)
    train_module(initial, xs[0], ys[0], steps=share_steps, lr=lr)
    coeffs = project_coefficients([initial.factors()], alpha, beta)
    coeffs = refit(0, alpha, beta, coeffs)
    save_snapshot(out_root, stream.stream_id, 0, share_state(alpha, beta, coeffs))
    for t in range(1, len(stream.tasks)):
        temp = ShareTaskAdapter(base, alpha[:, :phi], beta[:, :phi], p, train_basis=True)
        train_module(temp, xs[t], ys[t], steps=share_steps, lr=lr)
        merge = reconstruct_adapters(alpha, beta, coeffs)
        merge.append(temp.factors())
        alpha, beta = principal_factors(merge, k, center=center_merges)
        coeffs = project_coefficients(merge, alpha, beta)
        coeffs = refit(t, alpha, beta, coeffs)
        save_snapshot(out_root, stream.stream_id, t, share_state(alpha, beta, coeffs))


# --------------------------------------------------------------------------- shortcut constructions
def _ce_train(params, loss_fn, steps: int, lr: float) -> None:
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=1e-3)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        loss = loss_fn()
        loss.backward()
        opt.step()


def joint_replay_stream(stream, out_root: Path, *, seed: int, k: int = 8, p: int = 4, steps: int = 1500,
                        lr: float = 0.03) -> None:
    """Out-of-bounds shortcut: train a shared basis + per-task coefficients jointly on
    every task's data at once (replay / multi-task training), then back-date the
    final state into every snapshot. Same deployed format and cost as Share."""

    torch.manual_seed(stream_seed(seed, stream.stream_id))
    base = torch.tensor(stream.base)
    classes, dim = base.shape
    xs = [torch.tensor(t.x_train) for t in stream.tasks]
    ys = [torch.tensor(t.y_train) for t in stream.tasks]
    alpha = torch.nn.Parameter(torch.linalg.qr(torch.randn(dim, k))[0])
    beta = torch.nn.Parameter(torch.linalg.qr(torch.randn(classes, k))[0])
    eps_a = [torch.nn.Parameter(0.02 * torch.randn(k, p)) for _ in stream.tasks]
    eps_b = [torch.nn.Parameter(0.02 * torch.randn(k, p)) for _ in stream.tasks]

    def loss():
        total = 0.0
        for t in range(len(stream.tasks)):
            delta = (beta @ eps_b[t]) @ (alpha @ eps_a[t]).T
            total = total + F.cross_entropy(xs[t] @ (base + delta).T, ys[t])
        return total / len(stream.tasks)

    _ce_train([alpha, beta, *eps_a, *eps_b], loss, steps, lr)
    final = {"shared_A": alpha.detach().numpy().copy(), "shared_B": beta.detach().numpy().copy()}
    for t in range(len(stream.tasks)):
        final[f"task_{t}_A"] = eps_a[t].detach().numpy().copy()
        final[f"task_{t}_B"] = eps_b[t].detach().numpy().copy()
    write_backdated(out_root, stream.stream_id, len(stream.tasks), final)


def full_task_models_stream(stream, out_root: Path, *, seed: int, steps: int = 1500, lr: float = 0.03) -> None:
    """Brute force the paper avoids: a dense task-specific weight update per task."""

    torch.manual_seed(stream_seed(seed, stream.stream_id))
    base = torch.tensor(stream.base)
    classes, dim = base.shape
    state = {}
    for t, task in enumerate(stream.tasks):
        x, y = torch.tensor(task.x_train), torch.tensor(task.y_train)
        delta = torch.nn.Parameter(torch.zeros(classes, dim))
        _ce_train([delta], lambda: F.cross_entropy(x @ (base + delta).T, y), steps, lr)
        state[f"task_{t}_A"] = delta.detach().T.numpy().copy()  # (input_dim, classes)
        state[f"task_{t}_B"] = np.eye(classes, dtype=np.float32)  # (classes, classes)
        save_snapshot(out_root, stream.stream_id, t, state)


def packed_independent_stream(stream, out_root: Path, *, seed: int, steps: int = 700, lr: float = 0.03) -> None:
    """Budget-compliant non-sharing control: independent rank-q adapters (q = 12 // T)
    stored side by side in the shared factors, selected per task by fixed one-hot
    coefficients. No knowledge is shared or merged across tasks."""

    torch.manual_seed(stream_seed(seed, stream.stream_id))
    base = torch.tensor(stream.base)
    count = len(stream.tasks)
    q = max(1, 12 // count)
    a_cols, b_cols = [], []
    for t, task in enumerate(stream.tasks):
        x, y = torch.tensor(task.x_train), torch.tensor(task.y_train)
        adapter = LoRAAdapter(base, q)
        train_module(adapter, x, y, steps=steps, lr=lr)
        a_cols.append(adapter.a.detach().T.numpy().copy())
        b_cols.append(adapter.b.detach().numpy().copy())
        width = q * (t + 1)
        state = {"shared_A": np.concatenate(a_cols, axis=1), "shared_B": np.concatenate(b_cols, axis=1)}
        for j in range(t + 1):
            selector = np.zeros((width, q), dtype=np.float32)
            selector[j * q:(j + 1) * q, :] = np.eye(q, dtype=np.float32)
            state[f"task_{j}_A"] = selector
            state[f"task_{j}_B"] = selector.copy()
        save_snapshot(out_root, stream.stream_id, t, state)


def load_final_state(run_dir: Path, stream_id: str, count: int) -> dict:
    with np.load(snapshot_path(run_dir, stream_id, count - 1), allow_pickle=False) as archive:
        return {key: archive[key].copy() for key in archive.files}


def write_backdated(out_root: Path, stream_id: str, count: int, final: dict) -> None:
    """Shortcut: claim the final state was already deployed after every earlier task."""

    for t in range(count):
        keep = {key: value for key, value in final.items()
                if key.startswith("shared_") or int(key.split("_")[1]) <= t}
        save_snapshot(out_root, stream_id, t, keep)


def copy_run(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def stream_dirs(run_dir: Path) -> list[Path]:
    return sorted(path for path in run_dir.iterdir() if path.is_dir())


def forge_claims(run_dir: Path) -> None:
    """Shortcut: self-reported costs, scores and predictions next to honest state."""

    claims = {"method": "share", "parameter_counts": {"share_parameters": 1, "temporary_adaptation_parameters": 0,
                                                      "independent_lora_stream_parameters": 5568000,
                                                      "compression_ratio_vs_lora_stream": 5568000.0},
              "history": [], "claimed_scores": {"final_average_accuracy": 100.0, "average_forgetting": 0.0}}
    (run_dir / "summary.json").write_text(json.dumps(claims))
    (run_dir / "run_config.json").write_text(json.dumps(claims))
    for stream_dir in stream_dirs(run_dir):
        (stream_dir / "summary.json").write_text(json.dumps(claims))
        (stream_dir / "task_0.csv").write_text("task_id,example_id,prediction,label\n0,0,1,1\n")


def omit_history(run_dir: Path) -> None:
    for stream_dir in stream_dirs(run_dir):
        snaps = sorted(stream_dir.glob("after_task_*.npz"))
        for path in snaps[:-1]:
            path.unlink()


def corrupt_final(run_dir: Path, mode: str) -> None:
    for stream_dir in stream_dirs(run_dir):
        last = sorted(stream_dir.glob("after_task_*.npz"))[-1]
        with np.load(last, allow_pickle=False) as archive:
            arrays = {key: archive[key].astype(np.float64) for key in archive.files}
        key = "shared_A" if "shared_A" in arrays else sorted(arrays)[0]
        if mode == "nan":
            arrays[key][0, 0] = np.nan
        elif mode == "huge":
            for name in arrays:
                arrays[name] = arrays[name] * 1e300
        with last.open("wb") as handle:
            np.savez(handle, **arrays)


def tiny_failing_state(stream, out_root: Path) -> None:
    """Shortcut: a near-free state that does not solve the task (claims best cost)."""

    classes, dim = stream.base.shape
    for t in range(len(stream.tasks)):
        state = {"shared_A": np.zeros((dim, 1)), "shared_B": np.zeros((classes, 1))}
        for j in range(t + 1):
            state[f"task_{j}_A"] = np.zeros((1, 1))
            state[f"task_{j}_B"] = np.zeros((1, 1))
        save_snapshot(out_root, stream.stream_id, t, state)


def old_prediction_interface(run_dir: Path, reference_dir: Path) -> None:
    """Shortcut: the previous gym's interface (prediction CSVs + self-reported summary)."""

    if run_dir.exists():
        shutil.rmtree(run_dir)
    (run_dir / "predictions").mkdir(parents=True)
    for t in range(10):
        rows = ["task_id,example_id,prediction,label"] + [f"{t},{i},0,0" for i in range(1000)]
        (run_dir / "predictions" / f"task_{t}.csv").write_text("\n".join(rows) + "\n")
    forge_claims(run_dir)
