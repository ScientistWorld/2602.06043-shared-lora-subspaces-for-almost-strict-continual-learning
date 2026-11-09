"""Evaluator-owned feasibility gates and cohort-normalized additive ranking.

The visible scorer has its own independent implementation. No submitted score,
comparison model, resource denominator or success flag enters this calculation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


def finalize(scores: dict, failed_metrics: dict) -> dict:
    spec = json.loads(Path(__file__).with_name("reference_metrics.json").read_text())["experiments"]
    experiments = scores["experiments"]
    names = sorted(next(iter(experiments.values()))["results"])

    # Failure anywhere fails the attempt everywhere. A failed attempt is then
    # weakly dominated in every scored coordinate by every successful attempt.
    failures = {
        n: [e for e, b in experiments.items() if n in b["_metadata"]["failed_runs"]]
        for n in names
    }
    for name, failed in failures.items():
        if not failed:
            continue
        for experiment, block in experiments.items():
            previous = block["results"][name]
            if name not in block["_metadata"]["failed_runs"]:
                block["_metadata"]["failed_runs"][name] = {
                    "reason": f"attempt failed another required experiment: {', '.join(failed)}",
                    "measured": previous.copy(),
                }
            block["results"][name] = dict(failed_metrics, stored_parameters=previous["stored_parameters"])

    totals = dict.fromkeys(names, 0.0)
    normalizers = {}
    for experiment, rule in spec.items():
        block = experiments[experiment]
        normalizers[experiment] = {}
        for metric, settings in rule["metrics"].items():
            coefficient = abs(float(settings["coefficient"]))
            if coefficient == 0:
                continue
            ref = float(rule["reference"][metric])
            # The fixed reference is itself an attempt in the ranked cohort.
            values = [ref] + [float(block["results"][n][metric]) for n in names]
            if not all(math.isfinite(v) for v in values):
                raise ValueError(f"nonfinite evaluated metric: {experiment}/{metric}")
            mean = math.fsum(values) / len(values)
            sd = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / len(values))
            normalizers[experiment][metric] = sd
            if sd == 0:
                continue
            direction = 1.0 if settings["higher_is_better"] else -1.0
            for name in names:
                improvement = direction * (block["results"][name][metric] - ref) / sd
                totals[name] += float(rule["weight"]) * coefficient * improvement
    scores["_metadata"]["ranking"] = {
        "formula": "sum(weight * abs(coefficient) * direction * (metric - fixed_reference) / population_sd)",
        "cohort": "every run on disk plus the evaluator-owned reference anchor",
        "zero_variance": "contributes zero",
        "reference_rank": 0.0,
        "normalizers": normalizers,
        "rank_improvement": totals,
        "failed_attempts": {n: e for n, e in failures.items() if e},
    }
    scores["_metadata"]["fixed_baseline_context"] = {
        e: r["baseline_context"] for e, r in spec.items()
    }
    return scores
