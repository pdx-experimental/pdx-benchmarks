# External validator handoff

Independently evaluate the SLM experiments in this repository. Seek counterexamples that could overturn the reported interpretations; reproducing a PASS label is not the objective. Read the [independent validation plan](INDEPENDENT_VALIDATION_PLAN.md) and [protocol evidence and limitations](../slm-task-governance/evidence/frozen-protocol/README.md). The new plan is a draft, not a preregistered study or authorization to launch GPU jobs.

Use two separate workstreams: A audits evidence, scoring reproduction and statistics; B implements an independent parser and scorer without importing the original scorer. A third reviewer reconciles disagreements without overwriting either result. Disclose any limitations on executor independence.

## First stage: existing outputs only

1. Fix the input commit and file hashes; account for all 1,444 rows.
2. Freeze the new scoring rules before unblinding condition labels. The original scorer already includes numerical tolerance, rounded equality and conditional number extraction; it is not pure exact matching.
3. Evaluate original scoring, independent typed normalization and final-state correctness separately. Missing state is not evaluable; an answer hit or a receipt does not establish a correct environment state.
4. Extract candidate answers without access to expected answers. Do not arbitrarily choose the last number. Recovery from raw terminal responses must be a separately reported extraction-pipeline sensitivity analysis, never a silent ledger rewrite.
5. Recompute every paired comparison. Independently check Llama 8B full-family Holm=0.50000, the two p=0.0625 comparisons with Holm=0.87500, and Mistral schema-to-scalar contingency (0,4,1,13), exact two-sided p=0.375. Do not accept these stated values without checking the task-level outcomes.
6. Retained v2–v4 TSA receipts verify; retained v5 receipts fail. Complete independently authenticated remote start/attempt histories and a valid seal for the final Gemma patch remain unestablished. Preserve Gemma's 224 rows with this provenance flag. Any exclusion sensitivity is post hoc.
7. Deliver all per-row scores, disagreements, unavailable evidence, statistics and reproducible commands. Describe these new analyses as retrospective.

## Second stage: proposed new inference

Submit an executable placebo and framework-control design, dependency lock, real-hardware admission evidence, power calculation and compute budget before requesting execution authorization. Keep the inference backend fixed when comparing orchestration. Do not simultaneously change quantization, templates, model serving and orchestration and attribute the difference solely to the Engine.

PDX-governed arms must actually invoke the pinned public PyPI Engine. A non-PDX executor is an explicitly labelled research control, not a substitute PDX implementation. Never fabricate receipts or repair invalid arguments asymmetrically. Preserve valid model failures and every infrastructure attempt. Do not change prompts, scoring or exclusion rules after inspecting scores.

First return the independent retrospective validation report and the unmet execution requirements for the proposed new study. State directly which claims should be withdrawn if the evidence contradicts them.
