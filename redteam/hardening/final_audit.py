"""One batched final check. Rescores saved variants; never retrains in the test.

Run after scripts/reproduce.sh. Outputs here are audit evidence, not the gym's
reference score files. The standard no-argument test command scores all cases.
"""
from __future__ import annotations

import copy
import json
import importlib.metadata
import shutil
import subprocess
from pathlib import Path

from redteam.hardening import ranks, variants as V
from data.streams import load_manifest, load_stream, stream_ids

ROOT = Path('redteam/hardening')
RUNS = ROOT / 'runs'
EVIDENCE = ROOT / 'final'


def evaluate_all() -> dict:
    # Invoke exactly the public no-argument entry point, exposing the entire
    # audit cohort as checkpoints/. Restore the real reference runs on exit.
    saved = Path('tmp/hardening_reference_checkpoints')
    assert not saved.exists()
    Path('checkpoints').rename(saved)
    Path('checkpoints').symlink_to(RUNS.resolve(), target_is_directory=True)
    try:
        Path('scoring/scores_test.json').write_text('{"experiments":{"forged":{"results":{}}}}')
        subprocess.run(['bash', 'scripts/evaluate_test.sh'], check=True)
        subprocess.run(['bash', 'scripts/evaluate_train.sh'], check=True)
        scores = {}
        for split in ['test', 'train']:
            scores[split] = json.loads(Path(f'scoring/scores_{split}.json').read_text())
            assert 'forged' not in scores[split]['experiments']
        return scores
    finally:
        Path('checkpoints').unlink()
        saved.rename('checkpoints')


def rebuild_copies() -> None:
    RUNS.mkdir(exist_ok=True, parents=True)
    V.copy_run(Path('checkpoints/share'), RUNS/'reference_seed0')
    for name in ['independent_lora', 'independent_rank1', 'sequential_lora', 'frozen_backbone']:
        V.copy_run(Path('checkpoints')/name, RUNS/f'baseline_{name}')
    copies = {
        'shortcut_forged_claims': V.forge_claims,
        'shortcut_omit_history': V.omit_history,
        'shortcut_nan_state': lambda d: V.corrupt_final(d, 'nan'),
        'shortcut_impossible_values': lambda d: V.corrupt_final(d, 'huge'),
        'shortcut_noncanonical_snapshot': lambda d: next(d.glob('t06_00/after_task_00.npz')).rename(d/'t06_00/after_task_000.npz'),
    }
    for name, mutate in copies.items():
        V.copy_run(Path('checkpoints/share'), RUNS/name)
        mutate(RUNS/name)
    V.copy_run(Path('checkpoints/independent_lora'), RUNS/'shortcut_store_independent_adapters')
    V.copy_run(Path('checkpoints/independent_lora'), RUNS/'shortcut_poison_comparison_baseline')
    V.corrupt_final(RUNS/'shortcut_poison_comparison_baseline', 'nan')
    # A solution to one experiment that fails the other must fail the attempt.
    mixed = RUNS/'shortcut_partial_failure'
    V.copy_run(Path('checkpoints/share'), mixed)
    manifest = load_manifest()
    for sid in stream_ids(manifest=manifest):
        if manifest['streams'][sid]['experiment'] == 'continual_10task_stream':
            V.tiny_failing_state(load_stream(sid), mixed)
    for name in ['shortcut_read_visible_labels', 'shortcut_rebuild_seed_answers',
                 'shortcut_csv_label_forgery', 'shortcut_old_prediction_interface']:
        V.old_prediction_interface(RUNS/name, Path('checkpoints/share'))
    # These are the already-executed training variants; changed only the scorer.
    required = ['reference_seed1', 'reference_seed2', 'better_phi4_seed0',
                'better_phi4_seed1', 'better_phi4_seed2', 'weaker_no_finetune_seed0',
                'weaker_no_finetune_seed1', 'weaker_no_finetune_seed2',
                'shortcut_full_task_models', 'shortcut_packed_independent_adapters',
                'shortcut_backdated_snapshots', 'shortcut_joint_replay_backdated']
    for name in required:
        assert list((RUNS/name).glob('*/after_task_*.npz')), f'missing saved raw artifacts: {name}'


def verify_math(scores: dict) -> None:
    from eval.test.ranking import finalize
    from eval.test.evaluate import FAILED_METRICS
    # Independent hand calculation from spec and measured values.
    actual = scores['_metadata']['ranking']
    spec = json.loads(Path('eval/test/reference_metrics.json').read_text())['experiments']
    for name, value in actual['rank_improvement'].items():
        want = 0.0
        for e, rule in spec.items():
            for m, setting in rule['metrics'].items():
                c = abs(setting['coefficient'])
                if not c: continue
                sd = actual['normalizers'][e][m]
                if not sd: continue
                delta = scores['experiments'][e]['results'][name][m] - rule['reference'][m]
                want += rule['weight'] * c * (1 if setting['higher_is_better'] else -1) * delta / sd
        assert abs(value-want) < 1e-10
    # A unit change to a reported metric leaves the normalized contribution
    # unchanged; signs of coefficients are never used as metric direction.
    for e in spec:
        assert actual['normalizers'][e]['final_average_accuracy'] > 0
    failed = actual['failed_attempts']
    good = [v for n,v in actual['rank_improvement'].items() if n not in failed]
    bad = [v for n,v in actual['rank_improvement'].items() if n in failed]
    assert max(bad) < min(good), (max(bad), min(good))
    assert 'shortcut_partial_failure' in failed
    for e,b in scores['experiments'].items():
        assert b['results']['shortcut_partial_failure']['final_average_accuracy'] == 0
        assert b['results']['shortcut_forged_claims'] == b['results']['reference_seed0']
        assert 'shortcut_omit_history' in b['_metadata']['failed_runs']
        assert 'shortcut_store_independent_adapters' in b['_metadata']['failed_runs']
        assert 'shortcut_full_task_models' in b['_metadata']['failed_runs']
        assert b['results']['reference_seed0'] == spec[e]['reference'], 'reference changed on final rerun'
    # Reapplying the scorer's gate and rank must be idempotent.
    again = finalize(copy.deepcopy(scores), FAILED_METRICS)
    assert again['_metadata']['ranking']['rank_improvement'] == actual['rank_improvement']


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    rebuild_copies()
    before = evaluate_all()
    # Canonical answers, test size and dimensions must not come from the public
    # manifest or prediction CSVs. Change them together in this single job.
    path = Path('data/streams/manifest.json')
    original = path.read_bytes()
    try:
        forged = json.loads(original)
        forged['train_per_task'] = 2
        forged['val_per_task'] = 2
        forged['num_classes'] = 1
        for stream in forged['streams'].values():
            stream['y_train'] = ['aa'] * stream['num_tasks']
            stream['y_test'] = ['aa'] * stream['num_tasks']
        path.write_text(json.dumps(forged))
        tampered = evaluate_all()
        for split in ['train','test']:
            assert tampered[split] == before[split], f'{split} trusted agent-owned canonical data'
    finally:
        path.write_bytes(original)
    for split,scores in before.items():
        (EVIDENCE/f'scores_{split}_all.json').write_text(json.dumps(scores,indent=2,allow_nan=False)+'\n')
        summary = ranks.summarize(scores, ranks.load_spec())
        summary['evaluator_ranking'] = scores['_metadata']['ranking']
        (EVIDENCE/f'results_{split}.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
        (EVIDENCE/f'results_{split}.md').write_text(ranks.to_markdown(summary))
    verify_math(before['test'])
    verification = {'no_argument_hidden_test':True, 'direct_score_write_overwritten':True,
                    'public_answer_and_size_poisoning_ignored':True, 'visible_evaluation_data_frozen':True,
                    'reference_rerun_matches_frozen_comparison':True, 'every_failure_ranks_below_every_success':True,
                    'all_rank_terms_independently_recomputed':True,
                    'cases':len(before['test']['_metadata']['ranking']['rank_improvement']),
                    'packages':{p:importlib.metadata.version(p) for p in ['numpy','torch']}}
    (EVIDENCE/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    print(json.dumps(verification,indent=2),flush=True)
    # Leave only actual reference runs (method and official baselines) in the
    # canonical score files. Audit shortcuts never become reference results.
    subprocess.run(['bash','scripts/evaluate_test.sh'], check=True)
    subprocess.run(['bash','scripts/evaluate_train.sh'], check=True)
    shutil.copyfile('scoring/scores_train.json', 'scoring/scores.json')


if __name__ == '__main__':
    main()
