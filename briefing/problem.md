# Problem Definition

## Research Question

How can a pretrained model be adapted to a sequence of new tasks while retaining earlier task performance, avoiding replay of previous task data, and keeping the incremental parameter and storage cost small enough for long task streams?

The benchmark problem is parameter-efficient continual finetuning. A solution receives tasks sequentially. At each step it may train on the current task data, but it should not rely on revisiting earlier task datasets. After the stream finishes, the resulting system is evaluated on all tasks seen so far.

## Why It Matters

Real deployments often need to update large pretrained models as new domains, datasets, or user needs arrive. Training and serving a full model or a separate adapter for every task becomes expensive, hard to maintain, and weak at sharing knowledge across tasks. A good solution would let one deployed model keep improving over time without unbounded growth.

## Success Criteria

A successful scaled reproduction should show that sequential adaptation remains competitive with strong non-continual or jointly trained references while using far fewer trainable and stored parameters. It should also measure the continual-learning constraints directly: final accuracy or task score alone is insufficient unless parameter cost, memory cost, and forgetting are also reported.
