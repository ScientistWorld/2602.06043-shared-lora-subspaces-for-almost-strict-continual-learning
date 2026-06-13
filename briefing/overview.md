# Overview

- **Paper ID:** 2602.06043
- **Title:** Shared LoRA Subspaces for almost Strict Continual Learning
- **Domain:** Parameter-efficient continual learning
- **TL;DR:** Share continually updates a shared low-rank adapter subspace so a pretrained model can learn task streams with far less adapter storage and limited forgetting.

## Short Summary

The paper studies replay-free parameter-efficient continual finetuning for pretrained models. It proposes Share, which derives shared LoRA factor bases with SVD, trains small task coefficients and temporary basis directions for new tasks, then merges new knowledge by recomputing principal factors and reprojecting task coefficients analytically. Reported experiments cover GLUE, image classification, 3D pose estimation, text-to-image adaptation, and large collections of LoRA adapters.

## Reproduction Scope

This workspace implements the actual Share computation on a compact deterministic low-rank continual classification benchmark. The benchmark is scaled down from the paper's large backbone experiments, but it exercises the same core claim: a replay-free shared subspace can retain task performance while using a much smaller representation than independent LoRA adapters.
