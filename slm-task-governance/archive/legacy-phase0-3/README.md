# Historical Phase 0–3 exploratory archive

This is a sanitized disclosure of the retained September exploratory archive. It is separate from the October A12 1,444-row dataset. Historical labels, scores and assertions are retained for scrutiny, not endorsed as verified research conclusions. No separately identified Phase 1 dataset was found in this retained export; this is not a claim that no such experiment ever existed.

## Contents and privacy treatment

- `data/results/`: retained Phase 0 ledgers and alternate scoring variants, Phase 2 factorial/window campaigns, and seven Phase 3 result bundles. The root ledger and Phase 0 strict ledger may duplicate evaluations; do not sum every file's rows.
- `src/`, `tests/`: available archived source and tests. The source set is incomplete: archived builders refer to a scorer source file not present here. The two Phase 2 notebooks retain their embedded scorers; a separate CPU disclosure package is available in [the Phase 2 directory](../phase2-exploratory/). Exact Phase 3 execution-source identity is not established by this export.
- `notebooks/`: retained Phase 0 and Phase 2 source notebooks. Outputs, execution counts and metadata are removed. These are historical source disclosures, not currently validated GPU launch instructions.
- `docs/`: historical English prose as `.md.txt` transcripts. Unsupported claims, obsolete instructions and links may remain in the quoted historical body; the wrapper marks them as superseded. They are not publication-ready papers.
- `sanitization_provenance.json`: original relative paths and source hashes, public hashes, transformations and excluded files. It contains no private absolute paths or personal account names.

Personal identifiers and detected credentials/local paths are removed. Non-English historical manifest annotations are replaced with an explicit omission marker. Binary PDFs, caches, compiled files and unrelated execution artifacts are excluded and retained privately. Historical manifest hashes are not rewritten to make sanitized files appear original; the new public manifest binds this export. Original source hashes establish a comparison target, not an independent timestamp or proof of execution.

## Verification and limits

Run from this directory with Python 3.10 or later; no packages, credentials, GPU or network are required:

```bash
python -B verify_archive.py
```

The verifier checks the complete public file set, hashes and provenance bindings, then reports malformed JSONL line numbers, duplicate row keys and retained hash comparisons. A byte-integrity pass does **not** turn malformed ledgers into valid data, validate historical claims, prove Engine execution or certify preregistration. Known parse errors are retained rather than repaired or dropped. The diagnostic output is reproducible; do not mistake parsed-row totals for complete evaluation counts.

For Phase 2, both original ledger hashes match and embedded scoring reproduces 1,101 stored results. Its builders install/import the Engine but directly execute tools; zero Engine invocations are declared. Its task loader adds `step_final`, correcting an earlier concern that final synthesis was absent. Free-generation exceptions are converted to empty strings, so model non-response and infrastructure errors cannot be fully distinguished. See [Phase 2 status](../../../docs/PHASE2_STATUS.md).

No model inference rerun was performed. Historical dependency ranges and unpinned model revisions do not support a claim of bit-for-bit GPU reproducibility today. Runtime installation, tests of inference adapters, raw-response completeness and independent scoring validity remain separate work.
