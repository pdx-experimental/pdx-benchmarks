# Local release review — 2026-10-11

The formal dataset contains 28 jobs and 1,444 recorded evaluations. A new Python 3.12 Windows virtual environment installed the CPU verification requirements from PyPI. `pip check` passed. The public verifier passed file-set checks, manifest/index checks, SQLite bundle digests, rescoring and paired statistical checks. Both success and score reasons were checked.

SQLite integrity checks passed for all 776 databases. A scan of the release files and structured SQLite text/BLOB contents found no matches for the credential and private Windows path patterns checked. Relative Markdown links were checked. PDF editions, historical exploratory artifacts and obsolete inference code were excluded and retained outside this repository.

These checks do not prove remote submission identity, completeness of remote retry history, absence of every possible secret, or reproducibility of model inference. Current file checks do not remove previously published Git history. No commit, push, tag or remote release was performed during this review.

## Correction review — 2026-10-11

Published selective original protocol snapshots and an offline OpenSSL verifier. Independently verified all nine retained v2–v4 RFC 3161 receipts. All three v5 receipts failed target-imprint verification; the failure is disclosed and the blanket verification claim withdrawn. Original draft plan and registry bytes remain unchanged. Statistical-test preregistration is not substantiated by the original plan. Corrected Llama 8B full-family Holm value to 0.50000 and removed unsupported causal mechanism claims. All 1,444 result rows still pass the CPU export and scoring verifier. Hygiene scanning found no unexpected secrets, account paths or broken links across 1,274 files / 776 databases; twelve documented exceptions are historical project-path/link occurrences in four immutable plan copies.
