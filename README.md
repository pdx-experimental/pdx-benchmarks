# PDX Benchmarks

The accompanying reports are technical drafts. They have not been submitted to or published by arXiv, a conference or a journal.

Formal A12 results for small language model task governance: **1,444 evaluations across 28 jobs**, using the public PyPI `pdx-artifact-engine==0.3.0a12` during governed runs.

See [the benchmark](slm-task-governance/README.md), [main paper](slm-task-governance/docs/reports/MAIN_PAPER.md), and [release scope](docs/RELEASE_SCOPE.md).

The release contains recorded outcomes, including failures and rejected tool calls. It does not establish that governance improves every model. Earlier exploratory materials are available separately in the historical archive; they are not included in the A12 evaluation count.

## Research archive

| Material | Scope and verification boundary |
| --- | --- |
| [A12 benchmark](slm-task-governance/README.md) | 1,444 recorded evaluations; export integrity, rescoring and exploratory statistical checks. Protocol limitations remain disclosed below. |
| [Historical Phase 0–3 archive](slm-task-governance/archive/legacy-phase0-3/README.md) | Available earlier data, source, tests, notebooks and historical report transcripts, with sanitization records. No separately identified Phase 1 dataset was found in the retained export. Historical defects and missing material are disclosed. |
| [Phase 2 CPU reproduction](slm-task-governance/archive/phase2-exploratory/README.md) | 912 factorial and 189 context-window evaluations; task coverage and all 1,101 stored scores reproduced using the embedded scorers. This is scoring consistency, not independent scoring validity. |

Historical condition names do not prove public Engine execution. In Phase 2, the retained code directly calls tools and declares zero Engine invocations. See [the Phase 2 audit](docs/PHASE2_STATUS.md). Historical reports are source transcripts, not current endorsed conclusions; old results must not be combined with A12 as independent evaluations.

Verify the historical export with Python's standard library, without installation, credentials, GPU access or network:

```sh
python -B slm-task-governance/archive/legacy-phase0-3/verify_archive.py
python -B slm-task-governance/archive/phase2-exploratory/verify_phase2.py
```

The archive verifier reports known malformed historical JSONL lines while checking exported bytes. An integrity pass does not certify research validity, complete execution provenance or current GPU reproducibility.

## Verify recorded results

```sh
cd slm-task-governance
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -r requirements.txt
python scripts/verify_public_candidate_formal.py
```

Verification needs no GPU, cloud credentials, model downloads or Engine execution. It checks exported file integrity, rescoring and paired statistics; it does not reproduce inference or independently prove remote submission identity.

Code is licensed under [Apache-2.0](LICENSE); see [NOTICE](NOTICE).

## Protocol evidence and correction

See the [retrospective protocol disclosure](slm-task-governance/evidence/frozen-protocol/README.md). v2–v4 TSA checks pass; v5 retained receipts fail their declared target. Prior claims of complete timestamp verification and advance specification of the statistical tests are withdrawn.

## Independent validation proposal

A separate [external parallel-validation plan](docs/INDEPENDENT_VALIDATION_PLAN.md) prioritizes scoring robustness, matched-length placebo controls and framework-independent replication. It is a draft for external execution, not a completed validation or preregistered study.
