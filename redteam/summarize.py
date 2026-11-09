"""Audit-only rank analysis: no method or shortcut imports this module."""
import json
import math
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path('/home/user')
AUDIT = ROOT / 'redteam'
reference_contract = json.loads((ROOT / 'scoring/reference.json').read_text())['experiments']
names = json.loads((AUDIT / 'cases.json').read_text())
rows = {}
for name in names:
    path = AUDIT / name / 'scores_test.json'
    status_path = AUDIT / name / 'status.json'
    if not path.exists():
        rows[name] = {'evaluation': 'rejected_or_not_run', 'metrics': None}
        continue
    data = json.loads(path.read_text())['experiments']
    metrics = {experiment: data[experiment]['results']['share'] for experiment in reference_contract}
    finite = all(math.isfinite(v) for exp in metrics.values() for v in exp.values())
    rows[name] = {'evaluation': 'accepted' if finite else 'accepted_nonfinite', 'metrics': metrics}

reference = rows['reference_existing']['metrics']
finite_names = [name for name in names if rows[name]['evaluation'] == 'accepted']
quality_names = [name for name in finite_names if not name.startswith('shortcut_')
                 or name == 'shortcut_bruteforce_full_task_models']

def scales(cohort):
    return {exp: {metric: pstdev([rows[name]['metrics'][exp][metric] for name in cohort])
                  for metric in definition['metrics']}
            for exp, definition in reference_contract.items()}


def rank_delta(metrics, scale):
    terms = {}
    for exp, definition in reference_contract.items():
        terms[exp] = {}
        for metric, rule in definition['metrics'].items():
            sigma = scale[exp][metric]
            coefficient = abs(rule.get('coefficient', 1.0))
            if coefficient == 0 or sigma == 0:
                terms[exp][metric] = 0.0
                continue
            direction = 1 if rule['higher_is_better'] else -1
            terms[exp][metric] = (definition['weight'] * coefficient * direction
                                  * (metrics[exp][metric] - reference[exp][metric]) / sigma)
    return sum(sum(exp.values()) for exp in terms.values()), terms

normalizers = {'all_audit_attempts': scales(finite_names), 'quality_checks': scales(quality_names)}
for name in finite_names:
    row = rows[name]
    row['mean_test_accuracy'] = mean([metrics['final_average_accuracy'] for metrics in row['metrics'].values()])
    row['ranks'] = {}
    for cohort_name, scale in normalizers.items():
        # A cohort's rank applies only to its members. In particular, do not
        # extrapolate quality-only standard deviations to extreme shortcuts.
        if cohort_name == 'quality_checks' and name not in quality_names:
            continue
        delta, terms = rank_delta(row['metrics'], scale)
        row['ranks'][cohort_name] = {'delta_vs_reference': delta, 'terms': terms}
    pair_scale = {exp: {metric: abs(row['metrics'][exp][metric] - reference[exp][metric]) / 2
                        for metric in definition['metrics']}
                  for exp, definition in reference_contract.items()}
    row['pairwise_rank_delta'] = rank_delta(row['metrics'], pair_scale)[0]
    gains = []
    for exp, definition in reference_contract.items():
        for metric, rule in definition['metrics'].items():
            if abs(rule.get('coefficient', 1)) == 0:
                continue
            gains.append((1 if rule['higher_is_better'] else -1) *
                         (row['metrics'][exp][metric] - reference[exp][metric]))
    row['dominates_reference'] = min(gains) >= -1e-9 and max(gains) > 1e-9

seed_names = ['reference_seed0', 'reference_seed1', 'reference_seed2']
seed_spread = {'initialization_seeds': {'stream13': [13,14,15], 'stream21': [21,22,23]},
               'metrics': {}, 'aggregate_accuracy': {}}
if all(name in finite_names for name in seed_names):
    for exp, definition in reference_contract.items():
        seed_spread['metrics'][exp] = {}
        for metric in definition['metrics']:
            values = [rows[name]['metrics'][exp][metric] for name in seed_names]
            seed_spread['metrics'][exp][metric] = {'values': values, 'min': min(values),
                                                   'max': max(values), 'range': max(values)-min(values)}
    values = [rows[name]['mean_test_accuracy'] for name in seed_names]
    seed_spread['aggregate_accuracy'] = {'values': values, 'range': max(values)-min(values)}
    for cohort_name in normalizers:
        values = [rows[name]['ranks'][cohort_name]['delta_vs_reference'] for name in seed_names]
        seed_spread[cohort_name] = {'rank_deltas': values, 'rank_range': max(values)-min(values)}

output = {'reference_source': 'reference_existing/scores_test.json',
          'formula': 'sum_experiments weight * sum_metrics abs(coefficient) * signed_improvement / population_stddev',
          'zero_variance_handling': 'zero contribution, since all cohort attempts have identical values',
          'cohorts': {'all_audit_attempts': finite_names, 'quality_checks': quality_names},
          'normalizers': normalizers, 'seed_spread': seed_spread, 'cases': rows}
(AUDIT / 'audit_summary.json').write_text(json.dumps(output, indent=2, allow_nan=True)+'\n')
lines = ['| Case | Accuracy stream 13 / 21 (%) | Rank delta, all | Rank delta, quality | Pairwise delta | Status |',
         '|---|---:|---:|---:|---:|---|']
for name, row in rows.items():
    if row['evaluation'] != 'accepted':
        lines.append(f'| {name} | — | — | — | — | {row["evaluation"]} |')
        continue
    acc = ' / '.join(f'{v["final_average_accuracy"]:.3f}' for v in row['metrics'].values())
    rank_all = row['ranks']['all_audit_attempts']['delta_vs_reference']
    rank_quality = (f'{row["ranks"]["quality_checks"]["delta_vs_reference"]:+.4f}'
                    if name in quality_names else '—')
    lines.append(f'| {name} | {acc} | {rank_all:+.5g} | {rank_quality} | {row["pairwise_rank_delta"]:+.4f} | accepted |')
(AUDIT / 'RESULTS.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines), flush=True)
