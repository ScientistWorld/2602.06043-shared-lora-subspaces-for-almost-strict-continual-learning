# Paper's Method

## Key Contribution

Share proposes a replay-free, parameter-efficient continual finetuning method that maintains one evolving shared low-rank subspace instead of storing an independent LoRA adapter for every task. The method targets almost strict continual learning: no past task data replay, no growing set of deployed adapters, and minimal parameter growth.

## Approach

Share starts from one or more LoRA adapters, or from an adapter trained on the first task, and forms shared principal factors for the LoRA A and B matrices. For each layer, task adapters are stacked, centered, and decomposed with SVD. The top shared directions become frozen basis factors, while lightweight task coefficients are trained.

When new task data arrives, Share temporarily expands with a small number of basis directions initialized from the existing subspace and trains those temporary factors and coefficients on the current task. When a new adapter arrives directly, it can be merged without data. The merge step reconstructs previously represented adapters, stacks them with the new information, recomputes the shared basis with truncated SVD, and analytically updates coefficients using projection or pseudoinverse operations. An optional Share-full setting further finetunes coefficients after merging when the experimental setting allows it.

## Main Claims

The primary claim is that a single continually updated shared low-rank representation can retain task performance close to separate-adapter or joint-training references while using orders of magnitude fewer trainable and stored parameters.

Secondary claims are that the same mechanism works across language, image classification, 3D pose estimation, and generative-model settings; that the shared subspace can support forward and sometimes backward transfer; and that storage savings grow as the number of tasks increases because the deployed representation does not require one full adapter per task.
