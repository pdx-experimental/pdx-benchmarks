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

## Follow-up questions and remaining gaps (2026-10-11)

**v1 was retained privately, not destroyed.** It was superseded after harness interface defects during the initial Qwen 1.5B job. A sanitized transcription of its archive record is now disclosed in [v1_DEFECT_REPORT.md](../release-history/v1_DEFECT_REPORT.md), together with [original authorization metadata](../release-history/v1_original_authorization_record.json). An earlier separate attempt had post-timestamp bundle mutation and incomplete verification; see [attempt1_DEFECT_AUDIT.md](../release-history/attempt1_DEFECT_AUDIT.md). These are historical internal records, not independently authenticated proof of the sequence. Omitting this history from the initial public release was a disclosure error. v1 is not included in the v2–v5 timestamp-verification claim. Historical task calibration versions remain outside this release.

**Actual start times remain unestablished for the full matrix.** Result completion timestamps and local submission metadata do not substitute for independently authenticated remote job start times. No claim is made that the 22-minute interval proves pre-start freezing.

**No alternative verified seal for the final Gemma patch has been established.** Treat both Gemma jobs (224 rows) as having unresolved final-notebook provenance. The retained outputs can be rescored, but patch provenance is not thereby proven. The original five-model Phase 0 analysis is retained with this warning. A separately labelled post-hoc four-model sensitivity excluding Gemma is available in [exploratory_pairwise_statistics.json](../exploratory_pairwise_statistics.json); it must not be presented as a preregistered family.

**Further reporting corrections:** Standard Holm recomputation gives 0.87500 for the two Phase 3 p=0.0625 comparisons. The prior 0.93750 values were reporting errors, not an alternative stated tie algorithm. Mistral schema-to-scalar pairing is (a,b,c,d)=(0,4,1,13), giving exact two-sided p=0.375; the prior appendix p=0.25 came from an incorrect contingency table. Task outcomes were not changed. All p-values are exploratory; nominal threshold crossings do not establish confirmatory evidence or intervention mechanisms.
