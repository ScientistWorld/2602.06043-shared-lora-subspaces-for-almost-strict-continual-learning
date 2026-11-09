# Problem Definition

## Research Question

How can a pretrained model be adapted to a sequence of new tasks while retaining earlier task performance, without replaying earlier task data, and while keeping the stored adaptation state small enough that it does not grow by a full adapter per task?

The benchmark problem is parameter-efficient continual finetuning. A solution receives the tasks of a stream one at a time. While learning task *t* it may use task *t*'s training data and whatever state it carried forward from tasks *0..t-1*; it may not revisit earlier tasks' data or look at later tasks. After every task the solution has a deployed state that must serve every task seen so far, and after the last task it is evaluated on all tasks of the stream.

## The Benchmark

Each *stream* consists of a frozen pretrained linear classifier `W0` (20 classes x 96 input features) and an ordered sequence of related classification tasks (6 or 10 tasks per stream). Each task has 900 labelled training examples and its own input distribution. Tasks of a stream are related, but each needs its own update of the frozen weights to be solved well; the frozen classifier alone is close to chance.

A solution adapts `W0` by a low-rank weight update per task, `W_t = W0 + L_t R_t^T`, where the factors may be built from state shared by all tasks of the stream and state specific to each task. Deployed state is limited the way an almost-strict continual learner must be: the shared part may be at most the size of one rank-12 adapter (12 x (20 + 96) = 1392 parameters) and each task may add at most 139 parameters (10% of one adapter). Storing a separate full-size adapter or a dense weight update for every task does not fit.

Development streams come with a labelled validation split for each task. The scored streams provide only training data; their held-out examples are never visible.

## Why It Matters

Real deployments need to keep adapting large pretrained models as new domains and users arrive. Storing and serving a separate adaptation per task grows without bound and shares no knowledge across tasks; fine-tuning one shared adaptation sequentially forgets earlier tasks. A good solution lets one compact deployed state keep improving over a long task stream.

## Success Criteria

A good solution reaches high final accuracy on every task of every stream after the whole stream has been learned, forgets little of what it once knew, and stays well inside the storage budget. Accuracy alone is not enough: storage cost and forgetting are measured from the deployed state itself.
