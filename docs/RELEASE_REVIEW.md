# Local release review — 2026-10-11

The formal dataset contains 28 jobs and 1,444 recorded evaluations. A new Python 3.12 Windows virtual environment installed the CPU verification requirements from PyPI. `pip check` passed. The public verifier passed file-set checks, manifest/index checks, SQLite bundle digests, rescoring and paired statistical checks. Both success and score reasons were checked.

SQLite integrity checks passed for all 776 databases. A scan of the release files and structured SQLite text/BLOB contents found no matches for the credential and private Windows path patterns checked. Relative Markdown links were checked. PDF editions, historical exploratory artifacts and obsolete inference code were excluded and retained outside this repository.

These checks do not prove remote submission identity, completeness of remote retry history, absence of every possible secret, or reproducibility of model inference. Current file checks do not remove previously published Git history. No commit, push, tag or remote release was performed during this review.

## Correction review — 2026-10-11

Published selective original protocol snapshots and an offline OpenSSL verifier. Independently verified all nine retained v2–v4 RFC 3161 receipts. All three v5 receipts failed target-imprint verification; the failure is disclosed and the blanket verification claim withdrawn. Original draft plan and registry bytes remain unchanged. Statistical-test preregistration is not substantiated by the original plan. Corrected Llama 8B full-family Holm value to 0.50000 and removed unsupported causal mechanism claims. All 1,444 result rows still pass the CPU export and scoring verifier. Hygiene scanning found no unexpected secrets, account paths or broken links across 1,274 files / 776 databases; twelve documented exceptions are historical project-path/link occurrences in four immutable plan copies.

## Follow-up correction

Removed remaining preregistered-test and causal-mechanism assertions. Recomputed all 18 Phase 3 and five Phase 0 paired comparisons directly from task outcomes and published the full JSON and generation script. Corrected the two full-family Holm entries from 0.93750 to 0.87500, and corrected the Mistral schema-to-scalar contingency from (1,3,0,14) to (0,4,1,13), changing raw p from 0.25 to 0.375. Previously verified aggregate pass counts are unchanged. Retrospectively disclosed v1 archive metadata and a sanitized defect-record transcription; their assertions are not treated as independent proof. Full remote start-time coverage and final Gemma patch sealing remain unestablished.
