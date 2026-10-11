# Retrospective protocol disclosure and correction

These are original, selectively exported private protocol snapshots, publicly disclosed on 2026-10-11. This is **not evidence of pre-run public registration**. Snapshot bytes are preserved, including original draft labels; later summaries do not override them.

## Independent checks

Run from the repository root with Python and OpenSSL installed:

```sh
python slm-task-governance/scripts/verify_frozen_protocol.py
```

The verifier checks each exported file against its original bundle manifest, reconstructs the timestamp target, and verifies RFC 3161 message imprints, signatures and certificate chains. It exits nonzero when a timestamp fails. See [verification_report.json](verification_report.json). Certificates are supplied for reproducibility; reviewers may use independently sourced trust anchors.

| Snapshot | Verified TSA times (UTC) | Result |
| --- | --- | --- |
| v2 | 2026-10-09 05:04:05–06 | All three TSA receipts verified |
| v3 | 2026-10-09 13:04:26–28 | All three TSA receipts verified |
| v4 | 2026-10-09 13:21:35–36 | All three TSA receipts verified |
| v5 | Not established for the declared target | All three retained receipts fail message-imprint comparison |

**Correction:** Previous claims that the v5 timestamp bundle was independently verified are withdrawn. Current private working-tree receipts and receipts exported from its authorization tag both failed comparison with the declared v5 target. No replacement timestamp can prove the historical claim. v5 authorization JSON is an original assertion, not independent proof.

## What is covered

Each directory includes the original plan, environment contract, task and row registries, cohort files, scoring source, formal notebooks, hash manifests, authorization metadata and TSA receipts. [export_index.json](export_index.json) explicitly lists exported and omitted paths. Only selected files are disclosed; this is not a complete source-release or re-execution bundle. Hashes of omitted files are commitments, not verification of their contents.

The v2 snapshot already includes Apertus and Gemma cohorts and formal notebooks. Therefore later notebook revisions alone do not show that these models were added later. v3 and v4 change the three Apertus notebook hashes relative to the preceding export. The selected v5 snapshot hashes match v4; this export does not substantiate the claimed Gemma notebook patch. Consult the machine-readable differences rather than inferring changes from version names.

## Limits on inference

The earliest verified v2 timestamp predates the earliest currently reported job **completion** at 2026-10-09 05:26:51 UTC. Completion is not submission or start. Complete independently authenticated remote start times and attempt histories are not supplied, so this release does not establish that every execution began after its applicable freeze or that no retries were omitted. Old commit/tag names are timestamp-bound metadata; the fresh public repository does not contain their Git objects.

The original plan does not establish advance specification of McNemar testing, Holm correction or the six-comparison family. Statistical comparisons are exploratory. The six- and eighteen-comparison results are both reported. Task version names and the current registry do not disclose the complete historical calibration process; claims of immunity to task-selection bias are not warranted.

OpenTimestamps confirmation is not claimed. These checks establish retained-byte integrity and the stated RFC 3161 results, not correctness of scientific design, scoring validity, author identity or freedom from selective reporting.

## Hygiene exception for original evidence

The four byte-identical original plan snapshots retain two historical `file:` links into a private project directory. They contain no personal account name or credential and do not resolve in this release. They are preserved solely to avoid falsifying timestamp-bound evidence. Use the public scoring source and verifiers instead. No other private-path exception is authorized.
