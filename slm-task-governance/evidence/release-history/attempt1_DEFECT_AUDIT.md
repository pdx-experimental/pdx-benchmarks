# Attempt 1 Defect Record (2026-10-09)
Reason for Retraction:
1. Bundle Mutation Post-Timestamp: environment_contract.json was modified after TSA submission to record timestamps, causing SHA256SUMS and FORMAL_RELEASE_SHA256SUMS digests to drift from the timestamped message imprint.
2. Incomplete Verification: Script only verified ASN.1 fields and messageImprint equality, but omitted CMS signature validation and certificate trust chain verification.
3. OpenTimestamps Misrepresentation: Marked calendar submission as fully verified rather than calendar-submitted.

Status: SUPERSEDED & RETRACTED. Formal matrix execution remained blocked.
