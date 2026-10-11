# PDX Benchmarks

The accompanying reports are technical drafts. They have not been submitted to or published by arXiv, a conference or a journal.

Formal A12 results for small language model task governance: **1,444 evaluations across 28 jobs**, using the public PyPI `pdx-artifact-engine==0.3.0a12` during governed runs.

See [the benchmark](slm-task-governance/README.md), [main paper](slm-task-governance/docs/reports/MAIN_PAPER.md), and [release scope](docs/RELEASE_SCOPE.md).

The release contains recorded outcomes, including failures and rejected tool calls. It does not establish that governance improves every model. Historical exploratory experiments are excluded from this release.

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
