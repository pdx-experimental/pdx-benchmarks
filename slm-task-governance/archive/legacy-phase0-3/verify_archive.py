"""CPU-only byte-integrity and historical ledger diagnostics; standard library only."""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(root):
    manifest = json.loads((root/'public_file_manifest.json').read_text(encoding='utf-8'))
    expected = {item['path']: item['sha256'] for item in manifest['files']}
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'public_file_manifest.json'}
    if actual != set(expected):
        raise ValueError('Archive file set differs from manifest')
    for rel, digest in expected.items():
        if hashlib.sha256((root/rel).read_bytes()).hexdigest() != digest:
            raise ValueError('Archive byte mismatch: '+rel)
    provenance = json.loads((root/'sanitization_provenance.json').read_text(encoding='utf-8'))
    for record in provenance['files']:
        if expected[record['path']] != record['public_sha256']:
            raise ValueError('Provenance mismatch: '+record['path'])
    ledgers = []
    for path in sorted((root/'data').rglob('*.jsonl')):
        rows, errors = [], []
        for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
            if not line.strip(): continue
            try:
                row = json.loads(line)
                if not isinstance(row,dict): raise ValueError('Row is not an object')
                rows.append(row)
            except (ValueError, TypeError) as exc:
                errors.append({'line':number,'error_type':type(exc).__name__})
        keys = [(r.get('model'),r.get('mode'),r.get('task_id')) for r in rows]
        item = {'path':path.relative_to(root).as_posix(),'parsed_rows':len(rows),'parse_errors':errors,'duplicate_keys':len(keys)-len(set(keys)), 'stored_successes':sum(r.get('success') is True for r in rows)}
        parent = path.parent/'run_manifest.json'
        if parent.exists():
            historical = json.loads(parent.read_text(encoding='utf-8'))
            old_hash = historical.get('ledger_cas_sha256',historical.get('ledger_sha256'))
            item['historical_ledger_hash_matches_public_bytes'] = None if old_hash is None else old_hash == expected[path.relative_to(root).as_posix()]
            item['declared_engine_invocations'] = historical.get('engine_invocations')
        ledgers.append(item)
    return {'archive_byte_integrity':'VERIFIED','research_validity':'NOT_ESTABLISHED_BY_THIS_CHECK','phase1':'No separately identified Phase 1 dataset in retained export','ledgers':ledgers,'warning':'Parsed-row counts exclude explicitly listed malformed lines; do not use them as complete cohort denominators. Duplicate ledger variants are not independent evaluations.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(inspect(args.root),indent=2))
