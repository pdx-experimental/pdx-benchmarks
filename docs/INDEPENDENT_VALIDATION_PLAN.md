# Independent parallel validation plan

Status: **DRAFT FOR EXTERNAL REVIEW / NOT PREREGISTERED / NO GPU RUN AUTHORIZED**.
Prepared 2026-10-11. This is a new validation study, not an amendment that retroactively preregisters the A12 results. Its purpose is to test and potentially overturn the current interpretations. Existing result rows and original protocol evidence must remain unchanged.

## Independence and responsibilities

The external executor should not be the author of the original runner, scorer or report. The user selects and contacts the executor. This document does not authorize sending messages, purchasing compute or launching jobs.

Two tracks proceed independently, with a third reviewer reconciling them:

| Track | Responsibility | Independence requirement |
| --- | --- | --- |
| A: provenance and result integrity | Recompute original scores, paired statistics, file commitments and TSA verification; audit job/attempt coverage | Read original code for audit; report failures rather than accepting prior PASS labels |
| B: scoring robustness | Implement an independent parser and scorer; assess how conclusions change with scoring policy | Do not import the original scoring implementation; freeze parser rules before arm labels and aggregate scores are revealed |
| C: adjudication | Compare per-row differences and review disputed task semantics and evidence coverage | May not silently overwrite either track; retain both outputs and explain resolutions |

A second agent using the same source, parser and assumptions is not independent replication. Process separation and a separate implementation are necessary; a different model name alone is insufficient. External verification of existing outputs is distinct from independent inference replication.

## Stage 1 — existing outputs, no new inference

Scope: all 1,444 released rows across 28 jobs. Do not select only Qwen successes or format failures. Fix the input commit and hash every input file. Preserve Gemma's 224 rows with an unresolved-final-notebook-provenance flag; retain the full cohort and separately report the already-labelled post-hoc sensitivity excluding Gemma.

### Track A checks

1. Verify the released result manifests and rescore every row, including `success` and `score_reason`.
2. Recompute all 18 Phase 3 paired comparisons and five Phase 0 comparisons from task IDs, with standard Holm correction. Independently cross-check tied p-values.
3. Verify original protocol snapshot hashes and reconstruct each RFC 3161 target; check message imprint, CMS signature and certificate chain. Do not accept authorization JSON as proof.
4. Establish the limits: v2–v4 retained receipts pass; v5 retained receipts fail; independently authenticated full job start/attempt history and a valid final Gemma patch seal remain unestablished.
5. Distinguish answer correctness, successful tool execution, business success, Engine rejection, infrastructure failure and final-state evidence. An answer hit after rejection remains an answer hit, not a successful tool audit.

### Track B scoring policies

The current scorer is **not pure exact matching**. It already normalizes text, extracts a first number in eligible cases, uses numerical tolerances, permits one-decimal rounded equality, and treats some suites differently. Audit its actual behavior, including false positives and false negatives.

Freeze three separately named analyses:

| Policy | Input and rule | Restrictions |
| --- | --- | --- |
| S0: original policy | Existing `final_answer` and original scoring behavior, reproduced independently where feasible | A reproduction baseline, not a gold standard of validity |
| S1: independent typed answer normalization | Only the declared terminal answer; task-type-specific numeric, percentage, currency, token, identifier or text comparison | No search for an expected answer anywhere in the response; no substring hit as a generic pass |
| S2: final-state verification | Independently replay/check deterministic tool state against task-specific assertions | Mark `not_evaluable` when state or replay inputs are missing; do not manufacture a state from an answer or receipt label |

For S1, a separate extraction stage must be blind to the expected answer and arm. Its output is a candidate value plus a trace of the extraction rule. Define numerical tolerance, percentage scale, units, scientific notation, rounding, multiple-number ambiguity and supported task types before unblinding. Include adversarial examples: wrong numeric answer followed by a correct distractor, multiple values, percent versus fraction, currency scale, contradictory answer sentences, IP addresses, filenames and hash tokens.

Do not automatically take the last number. Do not use an LLM judge as the sole correctness authority. Independent human review of ambiguity must be arm-blind and retain disagreement records.

The effect of parsing raw terminal JSON from `step_receipts.raw_response` is a **separate extraction-pipeline sensitivity analysis**. It must not silently replace an empty `final_answer`, use intermediate tool observations as terminal predictions, or cherry-pick a favourable response. Freeze terminal-message identification and JSON parsing rules first; record missing terminal evidence explicitly.

Report per-arm accuracy under each policy, all paired flip counts, the number of evaluable final states, and how estimated arm differences change. Do not claim format recovery is a model mechanism when it depends on a particular parser.

### Deliverables and exit gate

- `input_manifest.json`: commit, paths, SHA-256 and complete row keys.
- `validation_protocol.json`: parser, scoring and statistical rules with freeze time.
- `independent_scores.jsonl`: every row, policy, prediction, correctness, reason and evidence availability.
- `paired_statistics.json`: contingency counts, unrounded p-values and corrections.
- `disagreements.csv`: every mismatch with the original scorer, without deletion.
- `provenance_findings.md`: supported, unsupported and failed checks.
- `validation_report.md`: conclusions that survive and conclusions that fail.

A completed check can legitimately report FAILED or NOT EVALUABLE. The gate is complete accounting and reproducibility, not improvement in scores. Stage 1 is retrospective even if its new parser is frozen before use; do not describe the historical outcomes as confirmatory.

## Stage 2 — new inference: placebo and framework controls

Freeze a new cohort and executable protocol before running. Admission tests use disjoint tasks and cannot enter the analysis. Do not choose models or tasks after seeing validation scores.

### Prompt-length placebo study

Within one fixed execution backend, compare three arms:

- P0: minimal baseline prompt.
- P1: neutral placebo text, matched to P2's tokenizer-measured input length within a prespecified tolerance (proposed maximum 5%). It must contain no task solution, schema instruction, worked tool example or answer-format rule.
- P2: the full schema / exemplar / scalar prompt bundle under examination.

Keep tool inventory and semantics, authorization policy, context availability, model revision, actual quantization, tokenizer, inference backend, decoding and generation/tool budgets identical across these arms. Use immutable static padding construction and validate matching per model and task; record actual lengths. Do not inject task-relevant demonstrations into the placebo. Prevent truncation from deleting different task content.

Primary contrasts: P2−P1 (bundle effect beyond matched length) and P1−P0 (placebo/length condition difference). Even this does not isolate schema, few-shot examples or scalar rules. A neutral prompt can itself distract; interpret the placebo contrast with that limitation.

### Framework-independent comparison

Use the same model, inference backend and frozen prompts while changing only orchestration. A generic executor may serve as an explicitly labelled **research control**, not as a replacement PDX implementation or a PDX-governed arm. All PDX-governed arms must still invoke the pinned public PyPI Engine; no local clone, monkeypatch or fabricated receipt.

First replay identical, pre-recorded model decisions into both backends to test tool/validation/state semantics independently of generation. Then, if admission passes, conduct free-running paired inference with the same task inputs, budgets and observation presentation. Equivalent deterministic tool functions, fixtures, I/O schemas, error behavior and terminal rules are mandatory.

A new reference harness must not repair invalid model arguments when PDX would reject them. If semantics cannot be matched, report a framework-bundle comparison, not an isolated Engine effect. Freeze the comparator choice and executable package lock after admission; simply switching to llama.cpp, vLLM, Ollama or native function calling also changes inference or templates and is not a clean orchestration-only control.

### Budget and analysis freeze

Proposed initial model set: Qwen 2.5 Coder 7B, Qwen 2.5 Coder 1.5B and Llama 3.2 1B, covering previously observed improvement and regression. Reuse accessible pinned model revisions; independently admit each exact configuration before scheduling formal jobs.

Use at least 100 independently selected tasks per model only if the power analysis supports that number. Freeze a minimum detectable paired effect, expected discordance, multiplicity family and power target first; use simulation/exact calculations to fix N before inference. Do not promise that N=100 is sufficient. Cluster near-duplicate tasks and document the sampling population. Existing `dag_chain_v3` tasks are not unseen held-out tasks.

Proposed primary family for the three-arm placebo study: six comparisons (two named contrasts × three models), standard Holm at 0.05, paired task-level analysis under one deterministic greedy run. This is a **proposal**, not frozen preregistration. The framework study needs its own explicit family; never pool or split families after scores are seen.

Repeated greedy runs with different seeds do not provide independent observations. Optional sampled-decoding robustness runs must freeze temperature, seed list and aggregation and be analysed as repeated measurements within tasks, not extra independent tasks. Mixed-effects logistic regression may be a secondary analysis with task effects and model interactions; specify convergence/separation handling and task-sampling assumptions in advance. It does not automatically replace a valid paired test.

Admission gate: genuine target-GPU run with exact official dependencies, model revision, quantization evidence, representative multi-turn and longest-input tasks, tool rejection, terminal answer and complete artifact export. No mock-only approval. Retain infrastructure attempts with immutable identities. The executor must provide a compute estimate and bounded schedule before the user authorizes new GPU work.

## Stage 3 — further decomposition and external validity

After Stage 1 and Stage 2, design a separate study for schema × few-shot count × scalar rule × isolation × validation. The naive full design has 2×3×2×2×2=48 cells; many combinations may be semantically dependent. Define each cell and what interactions are estimable. A fractional design needs a declared alias structure; do not call a hierarchical design factorial or claim isolated components from it.

Constrained decoding versus prompt constraints versus postprocessing requires separate compatibility admission and the same task definitions, tool semantics and inference budgets. It is not a drop-in replacement unless the exact model/backend supports the intended grammar.

Use externally selected held-out tasks and, where compatible, a fixed version of an external tool-use benchmark. Audit overlap and licences. Add a larger-model comparator only after access, capacity and matched protocol admission; it is a scale comparator, not automatically a negative control.

## Pre-execution evidence and publication gate

For each new study, freeze task registry, model revisions, prompts, parser, scorer, tool fixtures, budgets, retry/exclusion rules, primary contrasts, sample size and analysis code. Independently verify the timestamp against the exact snapshot. Capture authenticated remote submission/start identities as well as completion; establish the freeze precedes submission. Preserve failed and cancelled attempts.

New source must be reviewed for secrets before public release. Publish the protocol before formal inference when allowed, then disclose all deviations and outcomes. Never rewrite old tags or acquire a new timestamp as a substitute for failed historical proof. Existing papers remain technical drafts and exploratory until a separately reported independent study justifies stronger language.
