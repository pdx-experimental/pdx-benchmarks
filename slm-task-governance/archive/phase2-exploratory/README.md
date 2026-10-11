# Phase 2 CPU reproduction package

This package exposes the retained 912 factorial and 189 context-window evaluations. It is a historical exploration, separate from A12, and is **not** evidence of public Engine orchestration. See [the corrected status](../../../docs/PHASE2_STATUS.md) and [the full historical archive](../legacy-phase0-3/).

```bash
python -B verify_phase2.py
```

Python 3.10+ and its standard library suffice. No installation, model, GPU, network or credentials are needed. The verifier checks public file hashes, unique complete model/condition/task coverage, expected answers against the embedded task definitions, terminal-step presence, original ledger hashes and all stored success flags/score reasons against each notebook's embedded scorer. It does not independently validate the scorer, task answers or scientific conclusions.

`cpu/` contains exact notebook code-cell extractions of scorers and loaders. `task_registry.json` is derived from those loaders, including `get_full_gold_steps()` output. `source_provenance.json` records original hashes and transformations. Notebook metadata, outputs and execution counts were removed; executable source was retained. Historical notebooks are disclosure artifacts, not validated current GPU instructions. Public manifests bind exported files and are not timestamps.

The old task loader supplies a final-answer step. An earlier suggestion that these tasks lacked a terminal stage was incorrect. Free-generation exceptions are silently converted into empty strings in the historical notebooks, limiting infrastructure/model-failure attribution. Model decisions and per-step raw responses are not present in these result ledgers. No inference rerun has been performed.
