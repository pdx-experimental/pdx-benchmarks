# Technical Report: Extended Empirical Analyses, Granular Tracing, and Systems Forensics

**Technical draft · October 2026 · Not submitted or published**
Accompanying the benchmark draft: *From Structured DAGs to Stateful Maintenance*

---

## 1. Executive Summary & Separate Evaluation Campaigns

A12 and Stateful maintenance answer different questions and retain separate denominators. A12 includes 1,444 rows. Stateful V23 and V34 each include 96 rows on the same exposed 48 tasks; those repeated rows are not independent new tasks. Fixed-DAG prompt/contract outcomes must not be treated as proof of general coding assistance.

### Stateful maintenance results and technical boundaries

We separately evaluated Apertus 8B INT8 on 48 exposed development tasks (eight each: bug repair, configuration changes, data transformations, multi-file workflows, ambiguity handling and boundary handling), with R/G paired runs on dual T4 GPUs. R uses direct tool handlers; G additionally uses actual Engine mediation. The shared handlers enforce the same workspace restrictions in both arms. The public [Stateful export](../../../stateful-maintenance/README.md) includes all 96 rows of each retained complete run, not only successful examples.

| Run | R Oracle PASS | G Oracle PASS | Full-task success, each arm | Practical success, each arm |
| --- | ---: | ---: | ---: | ---: |
| V23 | 23/48 | 23/48 | Not evaluated under V34 deadlines | Not reported |
| V34 | 20/48 | 20/48 | 16/48 | 3/48 |

Oracle PASS checks the saved candidate against external contracts. Full-task success also requires accepted completion within research limits (30 seconds for simple tasks, 90 seconds for data/multi tasks). Practical success also meets 10/30-second thresholds. The measures are nested: 20 = 4 Oracle-correct research timeouts + 13 completed but impractical tasks + 3 practical completions per arm. Timings concern resident-model generation and tools, excluding cold loading and the later host Oracle. All three practical successes are clarification/refusal tasks; practical code/configuration maintenance success is zero.

V34 loses three V23 passes per arm: stale-snapshot clarification, path-traversal refusal and backup scheduling. All encounter the research deadline. The first two spend a generation attempting a forbidden TASK.md write; a later refusal is truncated or rejected at the deadline. Backup scheduling retains invalid JSON because the deadline prevents the correction cycle seen in V23. These observations distinguish model mistakes, runner cutoff semantics and accepted final-state correctness; removing deadlines is not shown to guarantee recovery.

Data and multi-tool families already score zero complete tasks in V23 and remain zero in V34. Their 32 paired final patches are byte-identical, and none hits the research deadline. Concrete defects include omitted timezone conversion, wrong deduplication comparison, missing recursive redaction, invalid syntax, unchanged files and omitted configuration updates. One health-readiness candidate passes all four behavior vectors but fails the required liveness configuration: zero full-contract passes does not mean every component is wrong.

The inference loop provides syntax feedback only. That restriction, constrained decoding, prompting, quantization and task construction limit interpretation; failures do not establish intrinsic 8B inability. These are development replications after task exposure, not held-out confirmation. Both selected runs are disclosed alongside an attempt-history inventory; the export is not an independently authenticated exhaustive remote history.

V34 G records 178 task tool events, including 12 error/rejection events; five smoke calls are separate. Hash-bound manifests support inspection of recorded mediation, not independent signatures, functional correctness or an isolated Engine safety gain. Equal R/G pass counts are not an equivalence test and do not establish zero latency overhead.

#### Joint interpretation

Phase 3 measures outcomes under a bundled schema/exemplar/output-contract hierarchy on fixed DAGs. Stateful maintenance requires an actual correct, complete and timely file-state change. The former shows model-dependent descriptive improvements; the latter shows no observed G success advantage and poor practical delivery in this setup. These findings are compatible: auditable tool mediation and output-format compliance do not substitute for correct implementation. A hypothesis that supplied DAG structure reduces planning demands remains untested. Success rates across these endpoints must not be pooled or treated as an identified task-type interaction.


### A12 matrix

The PDX Benchmark A12 formal evaluation comprises 1,444 contracted task evaluations executed across 28 standalone Kaggle GPU jobs on dual NVIDIA Tesla T4 accelerators under 8-bit quantization (`BitsAndBytesConfig(load_in_8bit=True)`).

### 1.1 Comprehensive Matrix Results

#### Phase 3: Calibrated Multi-Step Dependency Tasks (18 Jobs, 324 Rows)
Evaluated across three hierarchical prompt conditions: unassisted anchor ($C_0$), schema governance ($C_{2s}$), and terminal scalar contract ($C_{2sf}$):
- **Qwen 2.5 Coder 7B**: $C_0$: 2/18 (11.1%), $C_{2s}$: 3/18 (16.7%), $C_{2sf}$: **10/18 (55.6%)**. Paired $C_0 \to C_{2sf}$: $\Delta = +8, p_{\text{raw}} = 0.00781$. Under the post-hoc selected main-effect family ($m=6$), $p_{\text{Holm}} = \mathbf{0.04688}$; under full exploratory testing across all 18 pairwise comparisons ($m=18$), $p_{\text{Holm}} = 0.14063$.
- **Llama 3.1 8B Instruct**: $C_0$: 0/18 (0.0%), $C_{2s}$: 1/18 (5.6%), $C_{2sf}$: **6/18 (33.3%)**. $C_0 \to C_{2sf}$: $\Delta = +6, p_{\text{raw}} = 0.03125, p_{\text{Holm (m=6)}} = 0.15625$.
- **Swiss AI Apertus 8B**: $C_0$: 2/18 (11.1%), $C_{2s}$: **8/18 (44.4%)**, $C_{2sf}$: **7/18 (38.9%)**. $C_0 \to C_{2s}$: $\Delta = +6, p_{\text{raw}} = 0.03125$.
- **Mistral 7B v0.3**: $C_0$: 0/18 (0.0%), $C_{2s}$: **4/18 (22.2%)**, $C_{2sf}$: **1/18 (5.6%)**. Descriptive decrease; exact paired p=0.375, without evidence of a causal mechanism.
- **Qwen 2.5 Coder 1.5B**: $C_0$: 0/18 (0.0%), $C_{2s}$: 1/18 (5.6%), $C_{2sf}$: 1/18 (5.6%). No significant difference ($p = 1.000$).
- **Llama 3.2 3B Instruct**: $C_0$: 0/18 (0.0%), $C_{2s}$: 0/18 (0.0%), $C_{2sf}$: 0/18 (0.0%). Persistent non-parseable / empty outputs across all arms.

#### Phase 0: Synthetic Fair Comparison (10 Jobs, 1,120 Rows)
Evaluated across accumulating ReAct loops versus isolated single-step dispatch ($n=112$ paired tasks per architecture):
- **Qwen 2.5 Coder 1.5B**: ReAct 20/112 (17.9%) vs. Isolated **38/112 (33.9%)**, $\Delta = +16.1\%, p_{\text{raw}} = 0.0009, p_{\text{Holm}} = \mathbf{0.0046}$ (Increase; nominally significant within the exploratory family).
- **Qwen 2.5 Coder 3B**: ReAct 34/112 (30.4%) vs. Isolated **41/112 (36.6%)**, $\Delta = +6.2\%, p_{\text{raw}} = 0.3240, p_{\text{Holm}} = 0.9720$ (Not significant).
- **Llama 3.2 1B**: ReAct **19/112 (17.0%)** vs. Isolated **6/112 (5.4%)**, $\Delta = -11.6\%, p_{\text{raw}} = 0.0023, p_{\text{Holm}} = \mathbf{0.0094}$ (**Decrease; nominally significant within the exploratory family**).
- **Llama 3.2 3B**: ReAct 29/112 (25.9%) vs. Isolated 26/112 (23.2%), $\Delta = -2.7\%, p_{\text{raw}} = 0.7011, p_{\text{Holm}} = 1.0000$ (Not significant).
- **Gemma 3 1B**: ReAct 17/112 (15.2%) vs. Isolated 18/112 (16.1%), $\Delta = +0.9\%, p_{\text{raw}} = 1.0000, p_{\text{Holm}} = 1.0000$ (Not significant; 87 total calls = 53 executions + 34 schema rejections).

---

## 2. Statistical Analysis & Multiple Testing Protocol

### 2.1 Paired Exact Testing Framework
Because all tasks within a benchmark phase are evaluated on identical task cohorts under deterministic greedy decoding ($T=0.0$), independent two-sample tests are invalid. We evaluate paired contingency matrices ($a, b, c, d$) using two-sided exact McNemar binomial tests on discordant pairs ($b, c$):
$$p = 2 \times \sum_{k=0}^{\min(b,c)} \binom{b+c}{k} 0.5^{b+c}$$

### 2.2 Family of Hypotheses Specification
To prevent post-hoc significance inflation and maintain reporting transparency:
1. **Post-Hoc Selected Main-Effect Family ($m=6$)**: Phase 3 evaluation testing whether full format contracts improve over unassisted baseline ($C_0 \to C_{2sf}$) across the 6 architectures. Under this family, Qwen 7B achieves $p_{\text{Holm}} = 0.04688$. *Disclosure*: The exported original protocol does not establish advance specification of McNemar testing, Holm adjustment, or the $m=6$ family. These analyses are exploratory.
2. **Phase 0 Comparative Family ($m=5$)**: Phase 0 evaluation testing whether isolated dispatch improves over ReAct across the 5 architectures. Qwen 1.5B achieves $p_{\text{Holm}} = 0.0046$; Llama 1B demonstrates a nominally significant decrease within the exploratory family ($p_{\text{Holm}} = 0.0094$).
3. **Exploratory Family ($m=18$)**: Evaluating all pairwise comparisons within Phase 3 ($C_0 \to C_{2s}$, $C_0 \to C_{2sf}$, $C_{2s} \to C_{2sf}$). In this broader scope, Qwen 7B yields $p_{\text{Holm}} = 0.14063$ (not significant at $\alpha=0.05$).

---

## 3. Systems Forensics & Operational Analysis

### 3.1 Non-Monotonic Sensitivity in Mistral 7B
Mistral pass counts were 0/18 under control, 4/18 (22.2%) under schema governance, and 1/18 (5.6%) under the scalar condition. Execution traces describe failures but do not identify their cause. For the schema-to-scalar comparison ($C_{2s} \to C_{2sf}$), exact paired counts are b=4 and c=1 (p=0.375). For control-to-scalar ($C_0 \to C_{2sf}$), b=0 and c=1 (p=1.000). An attention or generation-capacity mechanism is untested.

### 3.2 Compact Model Context Sensitivity in Llama 3.2 1B
In Llama 3.2 1B, the combined intervention was associated with a drop from 19/112 (17.0%) to 6/112 (5.4%). Conversation history as a semantic scaffold is an untested explanation; this design does not isolate its contribution from prompts, receipt presentation, or dispatch policy.

### 3.3 Gemma 3 1B Architecture & Attention Backend Sensitivity
Gemma 3 1B required two targeted engineering adaptations:
1. **Chat Template Alternation**: Gemma 3 requires strict user/model alternation. Appending observations followed by terminal instructions created adjacent user turns, requiring message consolidation in the builder.
2. **Attention Backend**: Default PyTorch SDPA caused memory alignment errors (`RuntimeError: p.attn_bias_ptr is not correctly aligned`) on long sequences under 8-bit quantization. Enforcing `attn_implementation="eager"` resolved instability. Under eager execution, Gemma 3 completed 112 tasks without alignment errors or OOM, producing 18 passes with 53 tool executions and 34 schema rejections.

---

## 4. Cryptographic Provenance & Public Candidate Status

1. **A12 recorded-result verification:** The public verifier checks all 28 exports and reproduces all 1,444 stored task scores and reported paired statistics. It does not rerun inference or independently authenticate remote start identity.
2. **Separate Stateful export:** V23 and V34 are exposed-development runs, each with 96 rows. Their standalone verifier checks public bytes, patch/Engine event bindings and nested accounting; it does not execute candidate code.
3. **Security scope:** Pattern and binary-content checks apply to the explicitly curated current file set. They cannot guarantee absence of every possible secret or certify previous Git history. No blanket safety clearance is claimed.
4. **Review state:** The current additions remain uncommitted and unpushed, pending human review. No further inference experiment was run for this preparation.

## Protocol evidence correction (2026-10-11)

See the [original protocol snapshots and independent checks](../../evidence/frozen-protocol/README.md). These are retrospectively disclosed private snapshots, not prior public registration. v2–v4 RFC 3161 checks pass; the retained v5 receipts do not match the declared bundle. Advance specification of the statistical tests and universal pre-start freezing are not established. Interpret the comparisons as exploratory.

Gemma caveat: The retained execution outputs report successful completion after an eager-attention adaptation, but a verified historical seal binding the final patched notebooks has not been established. These hardware descriptions do not resolve the 224-row provenance gap.
