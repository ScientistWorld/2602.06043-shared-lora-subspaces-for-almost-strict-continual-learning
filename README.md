# Shared LoRA Subspaces for almost Strict Continual Learning

<!-- scope-note -->
> [!NOTE]
> **Not a full reproduction of the paper.** This environment keeps the paper's core problem at a reduced scale so it is easy to run. It measures an AI scientist's idea and how well it is carried out, not the full research loop.

<!-- hardening-note -->
> [!NOTE]
> **Red-teamed and hardened.** A red team tried to score on this environment's hidden test without doing better research, and the environment was then fixed against the shortcuts that worked: see [`REDTEAM.md`](REDTEAM.md) and [`HARDENING.md`](HARDENING.md). The environment as it was before is kept as branch [`pre-hardening`](../../tree/pre-hardening).

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2602.06043"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2602.06043-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| **Paper ID** | [2602.06043](https://arxiv.org/abs/2602.06043) |
|:---|:---|
| **Domain** | Parameter-efficient continual learning |
| **TL;DR** | Share continually updates a shared low-rank adapter subspace so a pretrained model can learn task streams with far less adapter storage and limited forgetting. |

## Summary

The paper studies replay-free parameter-efficient continual finetuning for pretrained models. It proposes Share, which derives shared LoRA factor bases with SVD, trains small task coefficients and temporary basis directions for new tasks, then merges new knowledge by recomputing principal factors and reprojecting task coefficients analytically. Reported experiments cover GLUE, image classification, 3D pose estimation, text-to-image adaptation, and large collections of LoRA adapters.

## Problem

How can a pretrained model be adapted to a sequence of new tasks while retaining earlier task performance, avoiding replay of previous task data, and keeping the incremental parameter and storage cost small enough for long task streams?

The benchmark problem is parameter-efficient continual finetuning. A solution receives tasks sequentially. At each step it may train on the current task data, but it should not rely on revisiting earlier task datasets. After the stream finishes, the resulting system is evaluated on all tasks seen so far.

## The paper's method

Share proposes a replay-free, parameter-efficient continual finetuning method that maintains one evolving shared low-rank subspace instead of storing an independent LoRA adapter for every task. The method targets almost strict continual learning: no past task data replay, no growing set of deployed adapters, and minimal parameter growth.

## Run it

```bash
pip install sciworld
sw research 2602.06043 --mode innovate --agent claude-code
sw evaluate 2602.06043
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

