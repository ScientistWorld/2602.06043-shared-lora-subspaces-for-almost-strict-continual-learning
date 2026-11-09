"""Rank accounting for the hardening audit (pure Python; no numpy needed).

rank_delta(case) = sum_e weight_e * sum_m |coef_em| * dir_em * (case_em - ref_em) / sd_em

dir is +1 for higher-is-better metrics and -1 otherwise; sd is the population
standard deviation of the metric across the ranked cohort (zero-variance
metrics contribute nothing). Coefficient signs are ignored, as in the gym.

Usage: python3 redteam/hardening/ranks.py [scores_test_all.json] [out.json]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFERENCE_JSON = ROOT.parents[1] / "scoring" / "reference.json"
REF_CASE = "reference_seed0"


def load_spec(path: Path = REFERENCE_JSON) -> dict:
    ref = json.loads(path.read_text())["experiments"]
    return {
        exp: {
            "weight": float(block["weight"]),
            "metrics": {
                name: (abs(float(m["coefficient"])), 1.0 if m["higher_is_better"] else -1.0)
                for name, m in block["metrics"].items()
                if abs(float(m["coefficient"])) > 0
            },
        }
        for exp, block in ref.items()
    }


def _sd(values: list[float]) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def rank_delta(scores: dict, spec: dict, case: str, cohort: list[str], ref: str = REF_CASE) -> float:
    members = sorted(set(cohort) | {case, ref})
    total = 0.0
    for exp, exp_spec in spec.items():
        results = scores["experiments"][exp]["results"]
        for metric, (coef, direction) in exp_spec["metrics"].items():
            sd = _sd([results[m][metric] for m in members])
            if sd == 0:
                continue
            total += exp_spec["weight"] * coef * direction * (results[case][metric] - results[ref][metric]) / sd
    return total


def summarize(scores: dict, spec: dict) -> dict:
    names = sorted(next(iter(scores["experiments"].values()))["results"])
    honest = [n for n in names if not n.startswith("shortcut_")]
    out = {"reference": REF_CASE, "honest_cohort": honest, "cases": {}}
    for case in names:
        cohort = honest if case in honest else honest + [case]
        row = {
            "rank_delta": rank_delta(scores, spec, case, cohort),
            "rank_delta_pairwise": rank_delta(scores, spec, case, [case, REF_CASE]),
            "metrics": {},
            "failed": {},
            "paired_streams": {},
        }
        for exp, block in scores["experiments"].items():
            row["metrics"][exp] = block["results"][case]
            failure = block["_metadata"]["failed_runs"].get(case)
            if failure:
                row["failed"][exp] = failure
            mine = block["_metadata"]["final_accuracy_by_stream"].get(case, {})
            ref = block["_metadata"]["final_accuracy_by_stream"].get(REF_CASE, {})
            diffs = [mine[s] - ref[s] for s in sorted(ref) if s in mine]
            if diffs:
                mean = sum(diffs) / len(diffs)
                se = _sd(diffs) / math.sqrt(max(1, len(diffs) - 1)) if len(diffs) > 1 else float("nan")
                row["paired_streams"][exp] = {
                    "mean_accuracy_gain": mean,
                    "standard_error": se,
                    "streams_won": sum(d > 0 for d in diffs),
                    "streams": len(diffs),
                }
        out["cases"][case] = row
    refs = [n for n in honest if n.startswith("reference_seed")]
    deltas = [out["cases"][n]["rank_delta"] for n in refs]
    out["reference_seed_rank_spread"] = (max(deltas) - min(deltas)) if deltas else None
    for exp in scores["experiments"]:
        accs = [scores["experiments"][exp]["results"][n]["final_average_accuracy"] for n in refs]
        out.setdefault("reference_seed_accuracy_spread", {})[exp] = (max(accs) - min(accs)) if accs else None
    return out


def to_markdown(summary: dict) -> str:
    exps = list(next(iter(summary["cases"].values()))["metrics"])
    head = ["Case"] + [f"{e} acc / forg / frac" for e in exps] + ["Δrank (honest cohort)", "Δrank pairwise", "Status"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for case, row in summary["cases"].items():
        cells = [case]
        for e in exps:
            m = row["metrics"][e]
            cells.append(f"{m['final_average_accuracy']:.2f} / {m['average_forgetting']:.2f} / "
                         f"{m['parameter_fraction_vs_lora_stream']:.3f}")
        cells.append(f"{row['rank_delta']:+.3f}")
        cells.append(f"{row['rank_delta_pairwise']:+.3f}")
        cells.append("; ".join(f"{e}: {f['reason']}" for e, f in row["failed"].items()) or "ok")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(f"Reference-seed Δrank spread: {summary['reference_seed_rank_spread']:.3f}")
    for e, v in summary["reference_seed_accuracy_spread"].items():
        lines.append(f"Reference-seed final-accuracy spread ({e}): {v:.3f} pp")
    lines.append("")
    lines.append("Paired per-stream accuracy gains vs reference_seed0 (mean ± s.e., streams won):")
    for case, row in summary["cases"].items():
        parts = [f"{e}: {p['mean_accuracy_gain']:+.2f} ± {p['standard_error']:.2f} ({p['streams_won']}/{p['streams']})"
                 for e, p in row["paired_streams"].items()]
        if parts:
            lines.append(f"- {case}: " + "; ".join(parts))
    return "\n".join(lines) + "\n"


def main() -> None:
    scores_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scores_test_all.json"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results_test.json"
    summary = summarize(json.loads(scores_path.read_text()), load_spec())
    out_path.write_text(json.dumps(summary, indent=2) + "\n")
    out_path.with_suffix(".md").write_text(to_markdown(summary))
    print(to_markdown(summary))


if __name__ == "__main__":
    main()
