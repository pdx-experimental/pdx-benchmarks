# PDX Benchmarks: task structure, auditability and practical limits

The accompanying reports are technical drafts. They have not been submitted to or published by arXiv, a conference or a journal.

The release separates two questions: how bundled interface/output contracts affect fixed DAG task outcomes, and whether recorded tool mediation helps deliver correct, timely Python maintenance. A12 contains **1,444 evaluations across 28 jobs**, using the public PyPI `pdx-artifact-engine==0.3.0a12` during governed runs.

See [Stateful maintenance (V23/V34)](stateful-maintenance/README.md), [the A12 benchmark](slm-task-governance/README.md), [main paper](slm-task-governance/docs/reports/MAIN_PAPER.md), and [release scope](docs/RELEASE_SCOPE.md).

The release contains recorded outcomes, including failures and rejected tool calls. It does not establish that governance improves every model. Earlier exploratory materials are available separately in the historical archive; they are not included in the A12 evaluation count.

## From fixed DAG tasks to stateful maintenance

Phase 3 shows heterogeneous outcomes under combined schema, exemplar and terminal-format changes; it does not isolate the Engine or establish a universal benefit. Apertus scores 2/18, 8/18 and 7/18 across its three DAG conditions.

In the separate exposed 48-task maintenance cohort, V23 R/G each score 23/48 under the external Oracle. V34 R/G each score 20/48 under the Oracle, 16/48 for full completion within research limits, and 3/48 within practical thresholds. The three practical successes are refusals/clarifications; practical code/configuration maintenance success is zero. These are nested measures, not additive counts. The original A12 1,444 rows and the repeated Stateful runs must not be pooled.

G records actual Engine mediation, but both arms share tool safety handlers. The evidence supports auditability, not an isolated safety gain, improved coding ability, latency equivalence or production readiness. See [the complete public Stateful evidence](stateful-maintenance/README.md).

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
