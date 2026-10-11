"""Reproduce retained Phase 2 scoring and task coverage without GPU dependencies."""
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify():
    manifest = json.loads((ROOT/'public_file_manifest.json').read_text(encoding='utf-8'))
    expected = {r['path']:r['sha256'] for r in manifest['files']}
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'public_file_manifest.json'}
    assert set(expected) == actual, 'File-set mismatch'
    for path,digest in expected.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'Hash mismatch: '+path
    results = []
    for cohort, conditions, count in [('phase2_2x2',['C0_anchor','C1_grammar','C2_oneshot','C3_dual_governed'],76),('phase2_c4',['W0_full','W1_head_2k','W2_keyword_2k'],21)]:
        registry = json.loads((ROOT/f'data/{cohort}/task_registry.json').read_text(encoding='utf-8'))
        assert len(registry) == count
        tasks = {t['task_id']:t for t in registry}
        assert len(tasks) == count
        assert all(any(s['id']=='step_final' for s in t['full_gold_steps']) for t in registry)
        scorer = load(cohort+'_scorer',ROOT/f'cpu/{cohort}_scoring.py')
        ledger = ROOT/f'data/{cohort}/benchmark_ledger.jsonl'
        rows = [json.loads(s) for s in ledger.read_text(encoding='utf-8').splitlines() if s.strip()]
        models = {r['model'] for r in rows}
        assert len(models) == 3
        keys = [(r['model'],r['mode'],r['task_id']) for r in rows]
        assert len(keys) == len(set(keys))
        assert set(keys) == set(itertools.product(models,conditions,tasks))
        for row in rows:
            task = tasks[row['task_id']]
            assert row['expected_answer'] == task['expected_answer']
            assert row['suite'] == task['suite']
            success, reason = scorer.score_answer(row['final_answer'],task['expected_answer'],suite=task['suite'])
            assert (success,reason) == (row['success'],row['score_reason']), 'Rescore mismatch'
        historical = json.loads((ledger.parent/'run_manifest.json').read_text(encoding='utf-8'))
        assert hashlib.sha256(ledger.read_bytes()).hexdigest() == historical['ledger_cas_sha256']
        results.append({'cohort':cohort,'rows':len(rows),'task_coverage':'COMPLETE','rescoring':'MATCHES_EMBEDDED_SCORER','terminal_step_present':True,'declared_engine_invocations':historical['engine_invocations']})
    return {'status':'CPU_EXPORT_AND_SCORE_CONSISTENCY_VERIFIED','independent_scoring_validity':'NOT_ESTABLISHED','cohorts':results}


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
