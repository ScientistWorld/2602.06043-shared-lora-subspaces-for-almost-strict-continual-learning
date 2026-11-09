"""Brute-force shortcut: fit/store a full linear adapter for each task."""
import csv
import json
from pathlib import Path
import torch
import torch.nn.functional as F
from data.synthetic_tasks import load_npz


def train_shortcut_full_models(data_path, out, seed):
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    base, tasks, meta = load_npz(data_path)
    out.mkdir(parents=True, exist_ok=True)
    for task_id, task in enumerate(tasks):
        delta = torch.nn.Parameter(torch.zeros_like(base))
        optimizer = torch.optim.AdamW([delta], lr=0.03, weight_decay=0.001)
        for step in range(1500):
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(task.x_train @ (base + delta).T, task.y_train)
            loss.backward()
            optimizer.step()
        prediction = (task.x_test @ (base + delta).T).argmax(dim=1)
        with (out / f'task_{task_id}.csv').open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['task_id', 'example_id', 'prediction', 'label'])
            for i, (p, y) in enumerate(zip(prediction.tolist(), task.y_test.tolist())):
                writer.writerow([task_id, i, p, y])
    params = len(tasks) * base.numel()
    (out / 'summary.json').write_text(json.dumps({
        'method': 'full_independent', 'meta': meta,
        'parameter_counts': {'trainable_parameters': params,
            'temporary_adaptation_parameters': base.numel(),
            'independent_lora_stream_parameters': 5568,
            'compression_ratio_vs_lora_stream': 5568 / params}}, indent=2))
