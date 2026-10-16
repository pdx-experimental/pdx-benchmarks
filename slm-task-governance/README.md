# Small Language Model (SLM) Task Governance Benchmark

The accompanying reports are technical drafts. They have not been submitted to or published by arXiv, a conference or a journal.

An empirical benchmark evaluating **Interface Governance**, **Prompt Contracts**, and **Execution Isolation** across Small Language Models (1B to 8B parameters) under dual NVIDIA Tesla T4 GPUs (1,444 contracted evaluations across 28 standalone jobs).

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](../LICENSE)
[![Engine](https://img.shields.io/badge/pdx--artifact--engine-0.3.0a12-green.svg)](https://pypi.org/project/pdx-artifact-engine/)
[![Formal Evaluations](https://img.shields.io/badge/evaluations-1444_contracted-success.svg)](data/results_formal_candidate/)
[Result export verifier](scripts/verify_public_candidate_formal.py) · [Protocol verification limitations](evidence/frozen-protocol/README.md)

[Historical Phase 2 audit status](../docs/PHASE2_STATUS.md): 1,101 earlier exploratory evaluations are outside the A12 denominator. Their retained execution path directly calls tools rather than dispatching through the public Engine; they must not be presented as Engine-governed evidence.

[Historical Phase 0–3 archive](archive/legacy-phase0-3/) restores available earlier data, source and report transcripts with sanitization records and a CPU integrity verifier. It discloses missing material and malformed historical rows rather than treating all old campaigns as validated. [Phase 2 CPU reproduction](archive/phase2-exploratory/) independently exposes its retained scoring pipeline.

---

## Relationship to stateful maintenance

A separate [Stateful development export](../stateful-maintenance/README.md) tests real candidate code/configuration against external acceptance contracts and time limits. Its results are not added to this A12 denominator. Fixed-DAG contract outcomes and maintenance delivery are different endpoints. The combined evidence shows task-dependent outcomes and observable mediation, not a universal or isolated Engine benefit.

## Executive Summary

Autonomous agent architectures typically place language models inside an open-ended conversational ReAct loop. While large frontier models (70B+) can navigate these loops with moderate stability, **Small Language Models (SLMs, 1B–8B)** routinely exhibit near-zero pass rates on compound multi-step benchmarks. A prevailing assumption in the literature is that this reflects an intrinsic deficit in multi-step reasoning capacity.

This benchmark deconstructs multi-step task failure into three distinct operational layers:
1. **Interface Impedance**: Tool parameter schema violations and argument hallucination.
2. **Context Referral Impedance**: Unstructured intermediate execution receipts leading to template placeholder emissions in downstream steps.
3. **Format Impedance (Verbal Wrapping)**: Correct intermediate computations failing automated parsing due to unconstrained conversational text.

We evaluate prompt-level governance comprising **formal OpenAPI 3.0 schemas** ($C_{2s}$) and **terminal scalar contracts** ($C_{2sf}$), powered by [pdx-artifact-engine](https://pypi.org/project/pdx-artifact-engine/) (`0.3.0a12`), across **1,444 contracted task evaluations** executed across 28 standalone GPU jobs on dual NVIDIA Tesla T4 accelerators.

**Observed outcome**: Effects differed across models and conditions. These bundled interventions do not establish a universal benefit or isolate an Engine-specific causal effect. Architecture and attention explanations remain hypotheses.

---

## Formal Evaluation Matrix ($N=1,444$)

### Phase 3: Multi-Arm Interface and Contract Evaluation ($N=324$)

Evaluated across 6 model architectures on multi-step dependency DAG tasks ($n=18$ tasks per model, `dag_chain_v3`):
- **$C_0$ (Unassisted Anchor)**: Zero-shot prompt skeleton; tools described by name and text only.
- **$C_{2s}$ (Interface Governance)**: Formal OpenAPI 3.0 parameter schemas with 3 structured few-shot exemplars.
- **$C_{2sf}$ (Scalar Format Contract)**: Retains OpenAPI schemas and enforces a strict terminal scalar constraint (Rule 3) via a 4th exemplar.

| Model Architecture | Parameters | $C_0$ Pass | $C_{2s}$ Pass | $C_{2sf}$ Pass | $C_0 \to C_{2sf}$ ($\Delta, p_{\text{raw}}$) | Main-Effect $p_{\text{Holm}} (m=6)$ | Exploratory $p_{\text{Holm}} (m=18)$ | Observed Pattern |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Qwen 2.5 Coder 7B** | 7.61B | 2 / 18 (11.1%) | 3 / 18 (16.7%) | **10 / 18 (55.6%)** | **+8 ($p=0.00781$)** | **0.04688** | 0.14063 | Observed Format Recovery |
| **Llama 3.1 8B Instruct** | 8.03B | 0 / 18 (0.0%) | 1 / 18 (5.6%) | **6 / 18 (33.3%)** | +6 ($p=0.03125$) | 0.15625 | 0.50000 | Observed increase; not significant after correction |
| **Swiss AI Apertus 8B** | 8.00B | 2 / 18 (11.1%) | **8 / 18 (44.4%)** | 7 / 18 (38.9%) | +5 ($p=0.06250$) | 0.25000 | 0.87500 | Observed difference ($C_0 \to C_{2s}: p=0.031$) |
| **Mistral 7B v0.3** | 7.25B | 0 / 18 (0.0%) | **4 / 18 (22.2%)** | 1 / 18 (5.6%) | +1 ($p=1.00000$) | 1.00000 | 1.00000 | Non-Monotonic Sensitivity |
| **Qwen 2.5 Coder 1.5B** | 1.54B | 0 / 18 (0.0%) | 1 / 18 (5.6%) | 1 / 18 (5.6%) | +1 ($p=1.00000$) | 1.00000 | 1.00000 | Sub-2B Inactive |
| **Llama 3.2 3B Instruct** | 3.21B | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 0 ($p=1.00000$) | 1.00000 | 1.00000 | Persistent Non-Parseable Output |

> **Hypothesis Family Disclosure**: Under the post-hoc selected main-effect family ($m=6$, $C_0 \to C_{2sf}$ across 6 models), Qwen 7B shows a nominally significant difference within the exploratory family ($p_{\text{Holm}} = 0.04688$). In the full exploratory family across all 18 pairwise comparisons ($m=18$), the adjusted value is $p_{\text{Holm}} = 0.14063$ (not significant at $\alpha=0.05$). Advance specification of these tests and corrections is not established. All comparisons are exploratory.

---

### Phase 0: Synthetic Fair Comparison ($N=1,120$)

Contrasts an accumulating ReAct loop against isolated per-step dispatch across 5 models ($n=112$ paired tasks per model, deterministic greedy decoding $T=0.0$):

| Model Architecture | Scale | ReAct Pass (95% Wilson CI) | Isolated Pass (95% Wilson CI) | Contingency ($a / b / c / d$) | Net $\Delta$ | $p_{\text{raw}}$ | $p_{\text{Holm}}$ | Empirical Verdict |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Qwen 2.5 Coder 1.5B** | 1.54B | 20 / 112 (17.9% [11.9, 26.0]) | **38 / 112 (33.9% [25.8, 43.1])** | 15 / 5 / 23 / 69 | **+16.1%** | 0.0009 | **0.0046** | **Nominal exploratory increase** |
| **Qwen 2.5 Coder 3B** | 3.09B | 34 / 112 (30.4% [22.6, 39.4]) | 41 / 112 (36.6% [28.3, 45.8]) | 19 / 15 / 22 / 56 | +6.2% | 0.3240 | 0.9720 | No nominal difference |
| **Llama 3.2 1B** | 1.24B | **19 / 112 (17.0% [11.1, 25.0])** | 6 / 112 (5.4% [2.5, 11.2]) | 4 / 15 / 2 / 91 | **-11.6%** | 0.0023 | **0.0094** | **Nominal exploratory decrease** |
| **Llama 3.2 3B** | 3.21B | 29 / 112 (25.9% [18.7, 34.7]) | 26 / 112 (23.2% [16.4, 31.8]) | 14 / 15 / 12 / 71 | -2.7% | 0.7011 | 1.0000 | No nominal difference |
| **Gemma 3 1B** | 1.00B | 17 / 112 (15.2% [9.7, 23.0]) | 18 / 112 (16.1% [10.4, 24.0]) | 7 / 10 / 11 / 84 | +0.9% | 1.0000 | 1.0000 | No significant difference (53 executions, 34 rejections) |

---

## Installation & Independent Verification

The public candidate release can be verified for exported integrity, scores and paired statistics using the included self-contained verification tool.

### 1. Environment Setup

```bash
# Obtain the repository checkout through the hosting interface.
cd pdx-benchmarks/slm-task-governance

# Install required dependencies
pip install -r requirements.txt
```

### 2. Run Public Formal Verifier

Execute the strict verification script directly from the repository root:

```bash
python scripts/verify_public_candidate_formal.py
```

### What the Verifier Validates:
1. **Master Manifest & Cryptographic Digests**:
   - RFC 8785 canonical self-digest on `candidate_manifest.json` and all 28 `public_manifest.json` files.
   - Exact SHA-256 and byte-size verification for every published file.
   - Canonical SQLite bundle digest (`sqlite_bundle_sha256`) against all SQLite databases.
   - Dual-hash bridge integrity (`original_manifest_sha256`, `original_ledger_sha256`).
2. **Filesystem Lockdown**:
   - Confirms candidate directories contain zero unlisted or auxiliary files.
3. **Deterministic Answer Re-scoring**:
   - Independently re-scores **all 1,444 contracted task answers** using `src.scoring.score_answer`.
   - Asserts 0 mismatches against recorded pass/fail results.
4. **Statistical Replication**:
   - Computes exact paired contingency tables and two-sided McNemar binomial tests.
   - Replicates step-down Holm-Bonferroni corrections across Phase 0 ($m=5$) and Phase 3 ($m=6, m=18$).

---

## Repository Structure

```
slm-task-governance/
├── data/
│   └── results_formal_candidate/     # Sanitized candidate release (28 jobs, 1,444 rows)
│       ├── candidate_manifest.json    # Master CAS candidate manifest with RFC 8785 digests
│       ├── phase3_qwen7_c2sf/         # Example job directory
│       │   ├── public_manifest.json   # Derived public manifest
│       │   ├── original_run_manifest.json # Verbatim original manifest bridge
│       │   ├── benchmark_ledger.jsonl # Sanitized task ledger
│       │   ├── engine_evidence.jsonl  # Engine call receipts
│       │   └── workflows/             # Workflows SQLite databases (.sqlite3)
│       └── ... (28 formal evaluation directories)
├── docs/
│   └── reports/                       # Formal October 2026 publication documents
│       ├── MAIN_PAPER.md              # Main benchmark paper
│       ├── TECHNICAL_REPORT.md        # Extended technical and forensics report
│       ├── APPENDIX.md                # Cryptographic provenance and contingency tables
├── scripts/
│   └── verify_public_candidate_formal.py # Standalone public formal verifier
├── src/
│   └── scoring.py                     # Fair scoring engine
├── requirements.txt                   # Production verification dependencies
└── pyproject.toml                     # Package configuration
```

---

## Technical Drafts & Reports


---

## License

This benchmark repository is licensed under the [Apache License 2.0](../LICENSE).
Task cohorts, execution ledgers, and cryptographic evidence chains are distributed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).


## Release boundaries

The dependency file supports CPU verification of recorded results only. The experiment used public Engine 0.3.0a12; installing the verifier does not rerun that Engine or model inference. Remote kernel version and complete attempt history are not established by the offline release. PDF editions and historical experiments are excluded. See [release scope](../docs/RELEASE_SCOPE.md).

Reports: [main paper](docs/reports/MAIN_PAPER.md), [appendix](docs/reports/APPENDIX.md), [technical report](docs/reports/TECHNICAL_REPORT.md).

## Protocol evidence and correction

See the [retrospective protocol disclosure](evidence/frozen-protocol/README.md). v2–v4 TSA checks pass; v5 retained receipts fail their declared target. Prior claims of complete timestamp verification and advance specification of the statistical tests are withdrawn.

## Independent validation proposal

A separate [external parallel-validation plan](../docs/INDEPENDENT_VALIDATION_PLAN.md) prioritizes scoring robustness, matched-length placebo controls and framework-independent replication. It is a draft for external execution, not a completed validation or preregistered study.
