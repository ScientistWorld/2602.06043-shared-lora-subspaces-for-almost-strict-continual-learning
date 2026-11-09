# Overview

- **Paper ID:** 2602.06043
- **Title:** Shared LoRA Subspaces for almost Strict Continual Learning
- **Domain:** Parameter-efficient continual learning
- **TL;DR:** Share continually updates a shared low-rank adapter subspace so a pretrained model can learn task streams with far less adapter storage and limited forgetting.

## Short Summary

The paper studies replay-free parameter-efficient continual finetuning for pretrained models. It proposes Share, which derives shared LoRA factor bases with SVD, trains small task coefficients and temporary basis directions for new tasks, then merges new knowledge by recomputing principal factors and reprojecting task coefficients analytically. Reported experiments cover GLUE, image classification, 3D pose estimation, text-to-image adaptation, and large collections of LoRA adapters.

## Reproduction Scope

This workspace implements the actual Share computation (LoRA initialisation, centered-SVD principal factors, temporary top-phi basis adaptation, SVD merge with analytical coefficient reprojection) for a frozen linear classifier on a synthetic continual low-rank benchmark. Streams of 6 tasks (the paper's GLUE stream length) and 10 tasks (its image-classification stream length) share a hidden low-rank structure. The benchmark is scaled down from the paper's pretrained backbones but keeps its claim and its constraints: replay-free sequential learning, one compact shared state plus small per-task coefficients, measured accuracy, forgetting and storage. Methods submit their deployed state after every task. The evaluator rebuilds each task's weights, scores held-out examples of hidden streams, and counts the stored parameters itself.
