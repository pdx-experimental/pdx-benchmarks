# Supplementary Material: Technical Appendix & Cryptographic Provenance

**Technical draft · October 2026 · Not submitted or published**

**Accompanying the benchmark draft:**
*When Contracts Help and When They Hurt: An Empirical Benchmark of Interface and Format Governance on Small Language Models*

---

## Appendix A: Cryptographic Run Registry & Candidate Provenance

To support byte-level integrity checks, Table A1 records the cryptographic SHA-256 checksums, execution timestamps, and candidate export paths for all 28 primary formal evaluation jobs (1,444 contracted rows).

**Table A1: Cryptographic run registry and content-addressed storage (CAS) targets.**
All paths correspond to the public candidate structure under `slm-task-governance/data/results_formal_candidate/`. `Private Source SHA-256` represents the pre-sanitized ledger hash; `Candidate Public SHA-256` represents the sanitized ledger hash.

| Job Key | Architecture & Arm | Phase | Rows | Passed | Private Source SHA-256 (prefix) | Candidate Public SHA-256 (prefix) | Candidate DBs |
|:---|:---|:---:|:---:|:---:|:---|:---|:---:|
| `phase3_qwen15_c0` | Qwen 2.5 Coder 1.5B (C0) | P3 | 18 | 0 | `63b827361a9c8f10...` | `e2a4beadcb982f64...` | 0 |
| `phase3_qwen15_c2s` | Qwen 2.5 Coder 1.5B (C2s) | P3 | 18 | 1 | `e0db2c68c34f0d61...` | `11867c488349fa81...` | 18 |
| `phase3_qwen15_c2sf` | Qwen 2.5 Coder 1.5B (C2sf) | P3 | 18 | 1 | `73322a3ce3c25b82...` | `bcfa8ea7c558c44c...` | 18 |
| `phase3_qwen7_c0` | Qwen 2.5 Coder 7B (C0) | P3 | 18 | 2 | `cb071ee77441a6a9...` | `a3ad323497d4d420...` | 0 |
| `phase3_qwen7_c2s` | Qwen 2.5 Coder 7B (C2s) | P3 | 18 | 3 | `becd3d86cf411158...` | `482fe00508da4f4a...` | 18 |
| `phase3_qwen7_c2sf` | Qwen 2.5 Coder 7B (C2sf) | P3 | 18 | 10 | `29664acebe91364c...` | `fece9cbe498528f8...` | 18 |
| `phase3_llama3_c0` | Llama 3.2 3B (C0) | P3 | 18 | 0 | `a0d6b161635d2543...` | `5e9faeb4434ff744...` | 0 |
| `phase3_llama3_c2s` | Llama 3.2 3B (C2s) | P3 | 18 | 0 | `7feb413d4389ca46...` | `8c1c4daea5254199...` | 18 |
| `phase3_llama3_c2sf` | Llama 3.2 3B (C2sf) | P3 | 18 | 0 | `25ba0b30ef76ba99...` | `04128f615468d672...` | 18 |
| `phase3_llama8_c0` | Llama 3.1 8B (C0) | P3 | 18 | 0 | `699712796e4c3e3c...` | `37517c5d4ef57913...` | 0 |
| `phase3_llama8_c2s` | Llama 3.1 8B (C2s) | P3 | 18 | 1 | `1ddd9f16c4079dca...` | `b3d5b0370425a5e3...` | 18 |
| `phase3_llama8_c2sf` | Llama 3.1 8B (C2sf) | P3 | 18 | 6 | `0eae7cea4dcd44ef...` | `7be3395b05f278eb...` | 18 |
| `phase3_mistral_c0` | Mistral 7B (C0) | P3 | 18 | 0 | `b09fad06368538e7...` | `295a0242a0335e31...` | 0 |
| `phase3_mistral_c2s` | Mistral 7B (C2s) | P3 | 18 | 4 | `f0739489cb7fb340...` | `2854964645ae497b...` | 18 |
| `phase3_mistral_c2sf` | Mistral 7B (C2sf) | P3 | 18 | 1 | `daee0b268eac27f9...` | `9b3fe3c8052ebfdf...` | 18 |
| `phase3_apertus_c0` | Apertus 8B (C0) | P3 | 18 | 2 | `8bd43249496f93d1...` | `e971d2b8618e7787...` | 0 |
| `phase3_apertus_c2s` | Apertus 8B (C2s) | P3 | 18 | 8 | `e4db0509d0d97110...` | `8390b1fc219aa226...` | 18 |
| `phase3_apertus_c2sf` | Apertus 8B (C2sf) | P3 | 18 | 7 | `8d878309fdab0a5c...` | `c0228bb335ae71b9...` | 18 |
| `phase0_gemma3_1b_react` | Gemma 3 1B (ReAct) | P0 | 112 | 17 | `d0c0f6f437a9e3d8...` | `aa7aa29b9f074d47...` | 0 |
| `phase0_gemma3_1b_isolated` | Gemma 3 1B (Isolated) | P0 | 112 | 18 | `95700a57f399a477...` | `bbad78f685ba0563...` | 112 |
| `phase0_llama32_1b_react` | Llama 3.2 1B (ReAct) | P0 | 112 | 19 | `6f6dfaf4f00e36ba...` | `82cf212dd07b9a71...` | 0 |
| `phase0_llama32_1b_isolated` | Llama 3.2 1B (Isolated) | P0 | 112 | 6 | `b629306681da3747...` | `aa68ca0b8a2e2170...` | 112 |
| `phase0_llama32_3b_react` | Llama 3.2 3B (ReAct) | P0 | 112 | 29 | `e6e1e4b0e06f1d4b...` | `61159955fa9c90f1...` | 0 |
| `phase0_llama32_3b_isolated` | Llama 3.2 3B (Isolated) | P0 | 112 | 26 | `deb5708c71053055...` | `0142fa91f0907474...` | 112 |
| `phase0_qwen25_15b_react` | Qwen 2.5 Coder 1.5B (ReAct) | P0 | 112 | 20 | `eab4f53d996caf4c...` | `0d0bf93c3062828e...` | 0 |
| `phase0_qwen25_15b_isolated` | Qwen 2.5 Coder 1.5B (Isolated) | P0 | 112 | 38 | `b4fe101601c2da34...` | `75a7fcddc749942a...` | 112 |
| `phase0_qwen25_3b_react` | Qwen 2.5 Coder 3B (ReAct) | P0 | 112 | 34 | `0efd9e3600efb6bb...` | `b53fe4c2b97c41fe...` | 0 |
| `phase0_qwen25_3b_isolated` | Qwen 2.5 Coder 3B (Isolated) | P0 | 112 | 41 | `7ac255037a7273a1...` | `085ea34cbf7d84d6...` | 112 |

---

## Appendix B: Paired Contingency Tables ($2 \times 2$ McNemar Matrices)

To provide mathematical transparency for statistical testing, Table B1 reports the exact contingency cell counts:
- Cell $a$: Both pass ($+/+$)
- Cell $b$: Condition 1 passes, Condition 2 fails ($+/-$)
- Cell $c$: Condition 1 fails, Condition 2 passes ($-/+$)
- Cell $d$: Both fail ($-/-$)
- Exact $p$-value: Two-tailed exact binomial distribution on discordant pairs ($b, c$).

**Table B1: All paired comparisons recomputed from released task-level outcomes.**

| Phase / first → second | N | a | b | c | d | Delta | Exact raw p | Exploratory Holm | Post-hoc m=6 Holm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P3: qwen7_c0 → qwen7_c2sf | 18 | 2 | 0 | 8 | 8 | +8 | 0.00781 | 0.14062 (m=18) | 0.04688 |
| P3: qwen7_c0 → qwen7_c2s | 18 | 1 | 1 | 2 | 14 | +1 | 1.00000 | 1.00000 (m=18) | — |
| P3: qwen7_c2s → qwen7_c2sf | 18 | 3 | 0 | 7 | 8 | +7 | 0.01562 | 0.26562 (m=18) | — |
| P3: llama8_c0 → llama8_c2sf | 18 | 0 | 0 | 6 | 12 | +6 | 0.03125 | 0.50000 (m=18) | 0.15625 |
| P3: llama8_c0 → llama8_c2s | 18 | 0 | 0 | 1 | 17 | +1 | 1.00000 | 1.00000 (m=18) | — |
| P3: llama8_c2s → llama8_c2sf | 18 | 1 | 0 | 5 | 12 | +5 | 0.06250 | 0.87500 (m=18) | — |
| P3: apertus_c0 → apertus_c2sf | 18 | 2 | 0 | 5 | 11 | +5 | 0.06250 | 0.87500 (m=18) | 0.25000 |
| P3: apertus_c0 → apertus_c2s | 18 | 2 | 0 | 6 | 10 | +6 | 0.03125 | 0.50000 (m=18) | — |
| P3: apertus_c2s → apertus_c2sf | 18 | 5 | 3 | 2 | 8 | -1 | 1.00000 | 1.00000 (m=18) | — |
| P3: mistral_c0 → mistral_c2sf | 18 | 0 | 0 | 1 | 17 | +1 | 1.00000 | 1.00000 (m=18) | 1.00000 |
| P3: mistral_c0 → mistral_c2s | 18 | 0 | 0 | 4 | 14 | +4 | 0.12500 | 1.00000 (m=18) | — |
| P3: mistral_c2s → mistral_c2sf | 18 | 0 | 4 | 1 | 13 | -3 | 0.37500 | 1.00000 (m=18) | — |
| P3: qwen15_c0 → qwen15_c2sf | 18 | 0 | 0 | 1 | 17 | +1 | 1.00000 | 1.00000 (m=18) | 1.00000 |
| P3: qwen15_c0 → qwen15_c2s | 18 | 0 | 0 | 1 | 17 | +1 | 1.00000 | 1.00000 (m=18) | — |
| P3: qwen15_c2s → qwen15_c2sf | 18 | 0 | 1 | 1 | 16 | +0 | 1.00000 | 1.00000 (m=18) | — |
| P3: llama3_c0 → llama3_c2sf | 18 | 0 | 0 | 0 | 18 | +0 | 1.00000 | 1.00000 (m=18) | 1.00000 |
| P3: llama3_c0 → llama3_c2s | 18 | 0 | 0 | 0 | 18 | +0 | 1.00000 | 1.00000 (m=18) | — |
| P3: llama3_c2s → llama3_c2sf | 18 | 0 | 0 | 0 | 18 | +0 | 1.00000 | 1.00000 (m=18) | — |
| P0: qwen25_15b_react → qwen25_15b_isolated | 112 | 15 | 5 | 23 | 69 | +18 | 0.00091 | 0.00456 (m=5) | — |
| P0: qwen25_3b_react → qwen25_3b_isolated | 112 | 19 | 15 | 22 | 56 | +7 | 0.32401 | 0.97203 (m=5) | — |
| P0: llama32_1b_react → llama32_1b_isolated | 112 | 4 | 15 | 2 | 91 | -13 | 0.00235 | 0.00940 (m=5) | — |
| P0: llama32_3b_react → llama32_3b_isolated | 112 | 14 | 15 | 12 | 71 | -3 | 0.70111 | 1.00000 (m=5) | — |
| P0: gemma3_1b_react → gemma3_1b_isolated | 112 | 7 | 10 | 11 | 84 | +1 | 1.00000 | 1.00000 (m=5) | — |

Holm uses sorted p-values with factors m, m−1, …, 1 and a cumulative maximum, including tied p-values. For the two p=0.0625 comparisons, ranks 5 and 6 give 0.875 and 0.8125; both adjusted values are 0.875. The former 0.9375 entries were reporting errors, not a declared alternative method.

The corrected Mistral schema-to-scalar contingency is (a,b,c,d)=(0,4,1,13), giving exact two-sided p=0.375. Previous (1,3,0,14) and p=0.25 entries were incorrect.

See [machine-readable calculations](../../evidence/exploratory_pairwise_statistics.json) and [the recomputation script](../../scripts/compute_pairwise_statistics.py). The post-hoc sensitivity excluding Gemma is provided separately; it is not a replacement preregistered analysis.

---

## Appendix C: Execution Provenance & Authorization Windows

**Table C1: Full execution authorization history and attempt breakdown.**

| Job Key | Staged Notebook SHA-256 (prefix) | Matching Tag Digests | Manifest Completion (UTC) | Release Window & Binding | Attempt Audit (Local Stages / Remote Status) |
|:---|:---|:---:|:---:|:---|:---|
| `phase3_qwen15_c0` | `1c1e53441410...` | v3, v4, v5 | 2026-10-09 05:32:41 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_qwen15_c2s` | `c2b722fe03b3...` | v3, v4, v5 | 2026-10-09 05:26:51 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_qwen15_c2sf` | `2e5d75b5f3cb...` | v3, v4, v5 | 2026-10-09 05:51:58 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_qwen7_c0` | `cb071ee77441...` | v3, v4, v5 | 2026-10-09 08:36:12 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_qwen7_c2s` | `becd3d86cf41...` | v3, v4, v5 | 2026-10-09 08:32:12 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_qwen7_c2sf` | `29664acebe91...` | v3, v4, v5 | 2026-10-09 08:52:48 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_llama3_c0` | `a0d6b161635d...` | v3, v4, v5 | 2026-10-09 09:32:02 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_llama3_c2s` | `7feb413d4389...` | v3, v4, v5 | 2026-10-09 09:31:07 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_llama3_c2sf` | `25ba0b30ef76...` | v3, v4, v5 | 2026-10-09 09:57:56 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_mistral_c0` | `b09fad063685...` | v3, v4, v5 | 2026-10-09 12:05:00 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_mistral_c2s` | `f0739489cb7f...` | v3, v4, v5 | 2026-10-09 11:58:15 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_mistral_c2sf` | `daee0b268eac...` | v3, v4, v5 | 2026-10-09 12:34:22 | Authorized window v2 (`54fca7f`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_qwen25_15b_react` | `b2123f87f88b...` | v3, v4, v5 | 2026-10-09 14:24:44 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_qwen25_15b_isolated` | `590c53e3bcfa...` | v3, v4, v5 | 2026-10-09 14:44:31 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_apertus_c0` | `f0ed075cbb4e...` | v4, v5 | 2026-10-10 00:32:51 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_apertus_c2s` | `75535d95b782...` | v4, v5 | 2026-10-10 01:01:04 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_apertus_c2sf` | `ae2419dae818...` | v4, v5 | 2026-10-10 01:14:33 | Authorized window v4 (`f599fa9`) | 2 local stages (1 local timeout archive; remote attempt count unconfirmed) |
| `phase0_qwen25_3b_react` | `30085cfa8876...` | v3, v4, v5 | 2026-10-10 03:17:04 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_qwen25_3b_isolated` | `388f13ac69d3...` | v3, v4, v5 | 2026-10-10 03:25:37 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_llama8_c0` | `699712796e4c...` | v3, v4, v5 | 2026-10-10 03:58:27 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_llama8_c2s` | `1ddd9f16c407...` | v3, v4, v5 | 2026-10-10 04:00:37 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_llama32_1b_isolated` | `94ce1fab3846...` | v3, v4, v5 | 2026-10-10 05:21:23 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_llama32_1b_react` | `6d4275b610c7...` | v3, v4, v5 | 2026-10-10 05:28:48 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_llama32_3b_isolated` | `5268264f10b7...` | v3, v4, v5 | 2026-10-10 08:11:49 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_llama32_3b_react` | `ea6bb770f467...` | v3, v4, v5 | 2026-10-10 08:13:52 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase3_llama8_c2sf` | `0eae7cea4dcd...` | v3, v4, v5 | 2026-10-10 09:36:56 | Authorized window v4 (`f599fa9`) | 1 stage passed (remote attempt count unconfirmed) |
| `phase0_gemma3_1b_isolated` | `c3994641268c...` | v5 | 2026-10-10 14:25:59 | Authorized window v5 (`5edbd24`) | 2 local stages (1 local SDPA err archive; remote attempt count unconfirmed) |
| `phase0_gemma3_1b_react` | `1273b03209c3...` | v5 | 2026-10-10 14:29:36 | Authorized window v5 (`5edbd24`) | 2 local stages (1 local template err archive; remote attempt count unconfirmed) |

> [!NOTE]
> 1. **Timestamp definition:** Manifest Completion (UTC) is the time recorded after inference in run_manifest.json, not the inference start time.
> 2. **Attempts and scheduling:** Exported artifacts do not contain independently authenticated remote attempt counters or version identities. Stage counts describe retained local staging records only.
> 3. **Notebook hashes:** Hashes refer to locally staged submission files and associated historical tags. Remote execution bytes were not independently retained.

## Protocol evidence correction (2026-10-11)

See the [original protocol snapshots and independent checks](../../evidence/frozen-protocol/README.md). These are retrospectively disclosed private snapshots, not prior public registration. v2–v4 RFC 3161 checks pass; the retained v5 receipts do not match the declared bundle. Advance specification of the statistical tests and universal pre-start freezing are not established. Interpret the comparisons as exploratory.
