# Phase 2: historical exploratory study and audit status

Phase 2 was excluded when the public release was narrowed to the A12 result exports. That scope decision was not evidence that Phase 2 was invalid. Exclusion without an adequate explanation obscured the research history. An earlier explanation that old dependencies prevented publication was not substantiated and is withdrawn.

## What was checked

The retained ledgers contain 912 factorial evaluations (three models, four conditions, 76 tasks) and 189 context-window evaluations (three models, three conditions, 21 tasks). Model/condition/task keys are unique in each ledger. Both ledger SHA-256 values match their retained manifests. Reapplying each retained notebook's embedded scorer reproduces all 1,101 stored success flags and score reasons. This checks scoring consistency, not independent validity of the scoring rules or ground truth.

| Cohort | Rows | Retained ledger SHA-256 |
| --- | ---: | --- |
| Phase 2 factorial | 912 | `734546e2df14a738a20ffe34bfb30aaa04abbb8f330e2861d8f179ccb02ffc5b` |
| Phase 2 context windows | 189 | `202502041c1d2fb9aa945469ecb474210cd974129856ed80e9b58571d7718e14` |

## Execution boundary

The retained builders install and import `pdx-artifact-engine==0.3.0a9`, but connect their runners directly to `execute_benchmark_tool`. The runners manage steps and create shortened hashes themselves. Constrained generation uses Outlines. Both manifests explicitly declare zero Engine invocations. These artifacts support a study of prompting, constrained decoding and context windows; they do **not** establish public PDX Engine orchestration or authoritative Engine receipts. The historical condition name `C3_dual_governed` must not be interpreted as proof of Engine execution.

Correction after following the task loader: `get_full_gold_steps()` appends `step_final` when absent. The exported task registry confirms a terminal step for all 76 factorial and 21 window tasks. The earlier concern that no terminal opportunity was provided is withdrawn. The notebooks catch free-generation exceptions and return an empty string, obscuring infrastructure failure versus model non-response. The result ledgers do not retain per-step raw model responses, limiting retrospective diagnosis.

## Publication decision

Original artifacts are preserved privately without alteration. Sanitized historical files are now available in the [Phase 0–3 archive](../slm-task-governance/archive/legacy-phase0-3/), with [CPU Phase 2 reproduction](../slm-task-governance/archive/phase2-exploratory/). Do not add these rows to the A12 1,444-row denominator, describe them as Engine-governed results, or retroactively assert preregistration. Retained hashes are integrity checks, not independent timestamps. Current GPU inference reproducibility and independent scoring validity remain unestablished.

A future Engine study would require a new cohort and verified public API execution. It cannot repair the historical execution path by relabeling or rewriting old outputs. No GPU rerun is authorized or implied by this disclosure.
