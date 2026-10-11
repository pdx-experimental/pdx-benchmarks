# When Contracts Help and When They Hurt: An Empirical Benchmark of Interface and Format Governance on Small Language Models

**Technical draft · October 2026 · Not submitted or published**

---

## Abstract

Multi-step tool invocation in Small Language Models (SLMs, 1B–8B parameters) commonly exhibits near-zero completion rates on compound autonomous agent benchmarks. A prevailing assumption is that this reflects an intrinsic deficit in multi-step reasoning capacity. In this work, we deconstruct multi-step task execution into interface impedance (parameter schema mismatches), context referral impedance (unstructured intermediate receipt citation), and format impedance (conversational verbosity triggering automated parsing failure). We evaluate a prompt-level governance hierarchy comprising OpenAPI parameter schemas ($C_{2s}$) and terminal scalar output contracts ($C_{2sf}$) across an evaluation matrix with retrospectively disclosed, privately timestamped protocol snapshots spanning 1,444 contracted task executions across 28 standalone jobs on dual NVIDIA Tesla T4 GPUs.

In **Phase 3 (Calibrated Multi-Step Dependency Tasks, $N=324$ rows across 6 architectures)**, we evaluate an unassisted anchor ($C_0$), schema governance ($C_{2s}$), and full format contracts ($C_{2sf}$) on calibrated DAG tasks ($n=18$ per model, `dag_chain_v3`):
1. **Qwen 2.5 Coder 7B**: Advances from 2/18 (11.1%) under $C_0$ to 3/18 (16.7%) under $C_{2s}$, and to **10/18 (55.6%)** under $C_{2sf}$ (paired $\Delta = +8, p_{\text{raw}} = 0.00781$). Under the post-hoc selected main-effect family of 6 primary model comparisons ($m=6$), this gain is nominally significant within the exploratory family ($p_{\text{Holm}} = \mathbf{0.04688}$). However, under the full exploratory family across all 18 pairwise comparisons ($m=18$), the adjusted value is $p_{\text{Holm}} = 0.14063$, which does not meet conventional significance ($\alpha=0.05$). The $m=6$ family was selected post-hoc; the exported original plan does not establish advance specification of McNemar testing or Holm correction.
2. **Llama 3.1 8B Instruct**: Advances from 0/18 (0.0%) under $C_0$ to 1/18 (5.6%) under $C_{2s}$, and to **6/18 (33.3%)** under $C_{2sf}$ ($\Delta = +6, p_{\text{raw}} = 0.03125$; $p_{\text{Holm}} = 0.15625$ across $m=6$).
3. **Swiss AI Apertus 8B**: Advances from 2/18 (11.1%) under $C_0$ to **8/18 (44.4%)** under $C_{2s}$ ($\Delta = +6, p_{\text{raw}} = 0.03125$), and to **7/18 (38.9%)** under $C_{2sf}$ ($\Delta = +5, p_{\text{raw}} = 0.0625$).
4. **Mistral 7B v0.3**: Shows a descriptive, non-significant decrease from schema to scalar conditions (0/18 under $C_0$, **4/18 (22.2%)** under $C_{2s}$, dropping to **1/18 (5.6%)** under $C_{2sf}$), with a paired raw p-value of 0.375 for the decrease; this does not establish harm or a mechanism.
5. **Qwen 2.5 Coder 1.5B**: Scores 0/18 under $C_0$, 1/18 under $C_{2s}$, and 1/18 under $C_{2sf}$, showing no significant change ($p = 1.000$).
6. **Llama 3.2 3B**: Scores 0/18 across all conditions ($C_0$, $C_{2s}$, $C_{2sf}$) due to persistent non-parseable and empty output generation.

In **Phase 0 (Cross-Architecture Synthetic Fair Benchmark, $N=1,120$ rows across 5 architectures)**, we contrast accumulating ReAct loops with isolated per-step dispatch ($n=112$ paired tasks per model):
- **Qwen 2.5 Coder 1.5B**: ReAct 20/112 (17.9%) vs. Isolated **38/112 (33.9%)** ($\Delta = +16.1\%, p_{\text{raw}} = 0.0009, p_{\text{Holm}} = \mathbf{0.0046}$; increase; nominally significant within the exploratory family).
- **Qwen 2.5 Coder 3B**: ReAct 34/112 (30.4%) vs. Isolated **41/112 (36.6%)** ($\Delta = +6.2\%, p_{\text{raw}} = 0.3240, p_{\text{Holm}} = 0.9720$; not significant).
- **Llama 3.2 1B**: ReAct 19/112 (17.0%) vs. Isolated **6/112 (5.4%)** ($\Delta = -11.6\%, p_{\text{raw}} = 0.0023, p_{\text{Holm}} = \mathbf{0.0094}$; **decrease; nominally significant within the exploratory family**).
- **Llama 3.2 3B**: ReAct 29/112 (25.9%) vs. Isolated 26/112 (23.2%) ($\Delta = -2.7\%, p_{\text{raw}} = 0.7011$; not significant).
- **Gemma 3 1B**: ReAct 17/112 (15.2%) vs. Isolated 18/112 (16.1%) ($\Delta = +0.9\%, p_{\text{raw}} = 1.000$; negligible difference with 34 schema rejections).

**Observed outcome**: Effects differed across models and conditions. These bundled interventions do not establish a universal benefit or isolate an Engine-specific causal effect. Architecture and attention explanations remain hypotheses.

---

## 1. Introduction

Deploying Small Language Models (SLMs, 1B–8B parameters) on commodity edge accelerators (e.g., dual NVIDIA Tesla T4 GPUs) is essential for cost-effective enterprise AI systems. However, evaluations of compact models on multi-step tool invocation tasks routinely report pass rates near zero. Standard literature often interprets these outcomes as evidence of an intrinsic cognitive ceiling: models below 10B parameters are assumed to lack working memory and attention capacity for multi-step execution.

In this work, we investigate the operational boundaries of this assumption. Execution traces and multi-arm comparisons identify three observed categories of failure:
1. **Interface Impedance**: Tool definitions lacking explicit schemas trigger argument hallucination (e.g., emitting raw strings for structured key-value stores).
2. **Context Referral Impedance**: Unstructured intermediate execution receipts lead to template placeholder emissions in downstream steps.
3. **Format Impedance (Verbal Wrapping)**: Correct intermediate computations fail exact-match scoring due to unconstrained conversational text.

To measure these factors, we designed the **PDX Benchmark A12**, evaluating 1,444 contracted task executions across 28 standalone jobs on dual NVIDIA Tesla T4 GPUs with Engine receipt recording (distinct from protocol timestamp verification).

---

## 2. Experimental Design & Governance Hierarchy

We evaluate three structured prompt governance conditions across deterministic dependency workflows:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        GOVERNANCE TREATMENTS                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┴─────────────────────────────┐
       ▼                                                           ▼
┌───────────────────────────────┐               ┌────────────────────────────────┐
│         CONTROL ARMS          │               │         TREATMENT ARMS         │
├───────────────────────────────┤               ├────────────────────────────────┤
│ Condition C0 (Unassisted)     │               │ Arm C2s (Interface Governance) │
│ - Zero-shot tool prompt       │               │ - Formal OpenAPI 3.0 schemas   │
│ - Names & descriptions only   │               │ - 3-turn multi-tool exemplars  │
│                               │               │                                │
│ Phase 0 Control: ReAct        │               │ Arm C2sf (Scalar Contract)     │
│ - Accumulating conversation   │               │ - Full OpenAPI parameter schema│
│ - Observations appended       │               │ - Strict scalar Rule 3         │
│ - Full gold plan in prompt    │               │ - Dedicated terminal exemplar  │
└───────────────────────────────┘               └────────────────────────────────┘
```

1. **Unassisted Control ($C_0$ / ReAct)**:
   - In Phase 3: Zero-shot prompt skeleton; tools described by name and short text only.
   - In Phase 0: Standard accumulating multi-turn conversation with observation appending.
2. **Interface Governance ($C_{2s}$)**:
   - Formal OpenAPI 3.0 `parameters` JSON schemas for all available tools, coupled with 3 few-shot exemplars demonstrating structured parameter dispatch.
3. **Scalar Format Contract ($C_{2sf}$)**:
   - Retains full OpenAPI schemas and enforces a strict terminal scalar constraint (Rule 3: answer must be raw scalar only with no conversational filler), demonstrated via a 4th few-shot exemplar.

---

## 3. Phase 3: Multi-Arm Interface and Contract Evaluation Across 6 Architectures ($N=324$)

Table 1 summarizes task completion across all 6 evaluated models ($n=18$ tasks each, `dag_chain_v3`).

**Table 1: Phase 3 task completion across 6 model architectures ($N=18$ tasks per model).**
$\Delta$ denotes pass count difference. $p_{\text{raw}}$ denotes exact two-sided McNemar binomial test on discordant pairs. $p_{\text{Holm (m=6)}}$ represents step-down Holm correction across the post-hoc selected main-effect family ($C_0 \to C_{2sf}$). $p_{\text{Holm (m=18)}}$ represents correction across the full exploratory family (all 18 pairwise comparisons). Note: Advance specification of McNemar testing, Holm correction and the testing family is not established; all comparisons are exploratory.

| Model Architecture | Parameters | $C_0$ Pass | $C_{2s}$ Pass | $C_{2sf}$ Pass | $C_0 \to C_{2sf}$ ($\Delta, p_{\text{raw}}$) | $p_{\text{Holm (m=6)}}$ | $p_{\text{Holm (m=18)}}$ | Observed Pattern |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Qwen 2.5 Coder 7B** | 7.61B | 2 / 18 (11.1%) | 3 / 18 (16.7%) | **10 / 18 (55.6%)** | **+8 ($p=0.00781$)** | **0.04688** | 0.14063 | Observed Format Recovery |
| **Llama 3.1 8B Instruct** | 8.03B | 0 / 18 (0.0%) | 1 / 18 (5.6%) | **6 / 18 (33.3%)** | +6 ($p=0.03125$) | 0.15625 | 0.50000 | Observed increase; not significant after correction |
| **Swiss AI Apertus 8B** | 8.00B | 2 / 18 (11.1%) | **8 / 18 (44.4%)** | 7 / 18 (38.9%) | +5 ($p=0.06250$) | 0.25000 | 0.87500 | Observed difference ($C_0 \to C_{2s}: p=0.031$) |
| **Mistral 7B v0.3** | 7.25B | 0 / 18 (0.0%) | **4 / 18 (22.2%)** | 1 / 18 (5.6%) | +1 ($p=1.00000$) | 1.00000 | 1.00000 | Descriptive arm difference |
| **Qwen 2.5 Coder 1.5B** | 1.54B | 0 / 18 (0.0%) | 1 / 18 (5.6%) | 1 / 18 (5.6%) | +1 ($p=1.00000$) | 1.00000 | 1.00000 | Sub-2B Inactive |
| **Llama 3.2 3B Instruct** | 3.21B | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 0 ($p=1.00000$) | 1.00000 | 1.00000 | Persistent Non-Parseable Output |

### Key Observations:
1. **Testing Family Scope ($m=6$ vs. $m=18$)**: Under the post-hoc selected main-effect family ($m=6$ comparisons of $C_0 \to C_{2sf}$), Qwen 2.5 Coder 7B shows a nominally significant difference within the exploratory family ($p_{\text{Holm}} = 0.04688$). However, under the full exploratory scope spanning all 18 pairwise comparisons ($m=18$), the adjusted value is $p_{\text{Holm}} = 0.14063$, which is not significant at $\alpha=0.05$. Because the original plan did not explicitly isolate $m=6$ in advance, both adjusted values are reported side-by-side.
2. **Descriptive Difference (Mistral 7B)**: Mistral 7B scored 4/18 under schema governance ($C_{2s}$) but dropped to 1/18 when the rigid terminal scalar contract ($C_{2sf}$) was added. The paired raw p-value is 0.375; this decrease is not nominally significant within the exploratory family. Competition for attention is an untested hypothesis, not an established mechanism.
3. **Interface-Driven Recovery (Apertus 8B)**: Apertus 8B benefited strongly from schema governance alone ($C_0 \to C_{2s}: \Delta = +6, p = 0.03125$), while adding scalar constraints yielded no further improvement (7/18).

---

## 4. Phase 0: Synthetic Fair Comparison ($N=1,120$)

Phase 0 compares an accumulating ReAct loop against isolated per-step dispatch across 5 models ($n=112$ paired tasks per model).

**Table 2: Phase 0 paired comparison (112 tasks per model, ReAct vs. Isolated).**
Contingency counts ($a$: both pass, $b$: ReAct only, $c$: Isolated only, $d$: both fail). $p_{\text{raw}}$ denotes exact two-sided McNemar test. $p_{\text{Holm}}$ and $p_{\text{FDR}}$ represent multiple testing corrections across the 5 models.

| Model Architecture | Scale | ReAct Pass (95% Wilson CI) | Isolated Pass (95% Wilson CI) | Contingency ($a / b / c / d$) | Net $\Delta$ | $p_{\text{raw}}$ | $p_{\text{Holm}}$ | $p_{\text{FDR}}$ | Empirical Verdict |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Qwen 2.5 Coder 1.5B** | 1.54B | 20 / 112 (17.9% [11.9, 26.0]) | **38 / 112 (33.9% [25.8, 43.1])** | 15 / 5 / 23 / 69 | **+16.1%** | 0.0009 | **0.0046** | **0.0046** | **Nominal exploratory increase** |
| **Qwen 2.5 Coder 3B** | 3.09B | 34 / 112 (30.4% [22.6, 39.4]) | 41 / 112 (36.6% [28.3, 45.8]) | 19 / 15 / 22 / 56 | +6.2% | 0.3240 | 0.9720 | 0.5400 | No nominal difference |
| **Llama 3.2 1B** | 1.24B | **19 / 112 (17.0% [11.1, 25.0])** | 6 / 112 (5.4% [2.5, 11.2]) | 4 / 15 / 2 / 91 | **-11.6%** | 0.0023 | **0.0094** | **0.0059** | **Nominal exploratory decrease** |
| **Llama 3.2 3B** | 3.21B | 29 / 112 (25.9% [18.7, 34.7]) | 26 / 112 (23.2% [16.4, 31.8]) | 14 / 15 / 12 / 71 | -2.7% | 0.7011 | 1.0000 | 0.8764 | No nominal difference |
| **Gemma 3 1B** | 1.00B | 17 / 112 (15.2% [9.7, 23.0]) | 18 / 112 (16.1% [10.4, 24.0]) | 7 / 10 / 11 / 84 | +0.9% | 1.0000 | 1.0000 | 1.0000 | No nominal difference |

### Analysis:
- **Heterogeneous observed outcomes**: Across 5 models, only **1 model** (Qwen 1.5B) showed an increase nominally significant within the exploratory family under isolation ($p_{\text{adj}} = 0.0046$).
- **Observed decrease under the combined intervention**: Llama 3.2 1B showed a decrease nominally significant within the exploratory family under isolation (17.0% $\to$ 5.4%, $p_{\text{adj}} = 0.0094$). The design does not isolate the contribution of dialogue history; a continuity mechanism remains untested.
- **Gemma 3 1B Invariance & Rejections**: Gemma 3 1B showed a difference of only 1 task (17 $\to$ 18, $p = 1.000$). In the isolated arm, 87 total invocations yielded **53 successful tool executions** and **34 schema rejections**.

---

## 5. Limitations & Boundary Conditions

1. **Intervention Bundle Nature**: Phase 0 evaluates the combined effect of isolated single-step dispatch, structured prompts, and engine receipt verification. Differences cannot be attributed solely to the engine governance component.
2. **Compact Model Sensitivity**: Llama 3.2 1B had lower observed accuracy under the combined intervention. Dialogue-history effects and other components were not separately tested.
3. **Formatting Trade-offs**: Mistral had lower observed accuracy under the scalar condition than the schema condition (paired raw p=0.375). This difference does not establish competition for generation bandwidth or harm caused by a contract.
4. **Hardware & Backend Dependencies**: Attention backend choices (e.g. PyTorch SDPA alignment issues in Gemma 3) can introduce numerical and memory instability in 8-bit quantized models, requiring fallback to eager execution.
5. **Timestamp Disclosure**: The retained v2–v4 RFC 3161 receipts verify; all three retained v5 receipts fail comparison with the declared target. Prior blanket verification claims are withdrawn. OpenTimestamps confirmation is not established.

---

## 6. Conclusion

Across this task matrix, the bundled interventions showed heterogeneous outcomes. The experiment does not identify an isolated Engine effect or establish the proposed cognitive mechanisms. Independent replication is needed.

## Protocol evidence correction (2026-10-11)

See the [original protocol snapshots and independent checks](../../evidence/frozen-protocol/README.md). These are retrospectively disclosed private snapshots, not prior public registration. v2–v4 RFC 3161 checks pass; the retained v5 receipts do not match the declared bundle. Advance specification of the statistical tests and universal pre-start freezing are not established. Interpret the comparisons as exploratory.
