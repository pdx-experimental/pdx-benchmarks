# Version23 failure diagnosis

## Scope and preservation

Twenty task pairs (40 rows) cover all eight data transformations, all eight multi-tool tasks, and the four other tasks in the14 false-success cases per arm. R/G candidate patches and final claims match for every investigated pair. Original scores remain R23/48 and G23/48. No GPU rerun occurred.

All98 actual token sequences exactly decode to the saved rendered prompts. All49 R/G turn pairs have identical prompts and input tokens; all58 subsequent tool-feedback transitions match. Required task text and file contents were present without bootstrap clipping.

## Per-task findings

Behavior columns refer to the original Oracle vectors, including config variants. Each listed row represents identical R/G final results. False success means a final claimed_success=true with a failed acceptance contract; it does not establish intentional deception.

| Task | Original behavior cases passed | Final false success | Evidence-based cause |
|---|---:|---|---|
| [bug_01_discount_rounding](../runs/v23/bug_01_discount_rounding_R/candidate.patch) | 0/6 | True | Invalid quantize rounding argument, non-JSON Decimal return, and truthiness instead of fixed-key presence. |
| [bug_06_queue_drain_rate](../runs/v23/bug_06_queue_drain_rate_R/candidate.patch) | 3/4 | True | Nonzero test retains negative-rate division; contract requires null for every rate<=0. |
| [bug_07_env_boolean](../runs/v23/bug_07_env_boolean_R/candidate.patch) | 3/4 | True | Unknown values still return true instead of raising ValueError. |
| [config_04_health_timeout](../runs/v23/config_04_health_timeout_R/candidate.patch) | configuration-only | True | Reformatted JSON retains timeout_seconds=10 instead of3. |
| [data_01_normalize_headers](../runs/v23/data_01_normalize_headers_R/candidate.patch) | 0/5 | True | str.replace uses the whole transformed header as the search string; required ASCII-run normalization is not performed. |
| [data_02_iso_dates](../runs/v23/data_02_iso_dates_R/candidate.patch) | 1/3 | True | Offset-aware datetime is never converted with astimezone(UTC). |
| [data_03_dedupe_events](../runs/v23/data_03_dedupe_events_R/candidate.patch) | 1/3 | True | The original less-than comparison still selects the smallest timestamp/priority tuple. |
| [data_04_null_policy](../runs/v23/data_04_null_policy_R/candidate.patch) | 2/3 | True | Checks absent id but not explicit null id. |
| [data_05_units_conversion](../runs/v23/data_05_units_conversion_R/candidate.patch) | 0/4 | False | Extra closing brace makes invalid Python; MiB remains1000000 instead of1048576. |
| [data_06_inventory_reconcile](../runs/v23/data_06_inventory_reconcile_R/candidate.patch) | 0/2 | False | Mismatched closing brace makes invalid Python; negative quantities are still clamped. |
| [data_07_redact_logs](../runs/v23/data_07_redact_logs_R/candidate.patch) | 1/2 | True | List values are returned unchanged, so nested dictionaries in lists leak sensitive fields. |
| [data_08_jsonl_to_csv](../runs/v23/data_08_jsonl_to_csv_R/candidate.patch) | 2/3 | True | Unknown-field guard remains if False; csv writer raises ValueError instead of the specified error object. |
| [multi_01_api_and_config](../runs/v23/multi_01_api_and_config_R/candidate.patch) | 1/3 | False | No writes; premature success rejected, followed by honest incomplete submission. Defaults/config/docs remain unchanged. |
| [multi_02_schema_migration](../runs/v23/multi_02_schema_migration_R/candidate.patch) | 0/3 | False | Writes exactly the existing non-idempotent migration; registry and rollback documentation are not updated. |
| [multi_03_cli_export](../runs/v23/multi_03_cli_export_R/candidate.patch) | 2/5 | False | No writes; output parsing/path safety/docs remain incomplete, followed by honest incomplete submission. |
| [multi_04_retry_metrics](../runs/v23/multi_04_retry_metrics_R/candidate.patch) | 0/3 | True | Treats config file content as a pathname, keeps retry_count=n, and omits config/dashboard updates. |
| [multi_05_health_readiness](../runs/v23/multi_05_health_readiness_R/candidate.patch) | 4/4 | True | Corrects route wiring, passes all four behavior vectors, but leaves liveness=legacy_/live in config. |
| [multi_06_archive_manifest](../runs/v23/multi_06_archive_manifest_R/candidate.patch) | 2/3 | False | No writes; temporary-file exclusion and documentation remain incomplete. |
| [multi_07_queue_dead_letter](../runs/v23/multi_07_queue_dead_letter_R/candidate.patch) | 2/4 | True | Keeps <= instead of strict < and omits queue configuration and documentation updates. |
| [multi_08_release_gate](../runs/v23/multi_08_release_gate_R/candidate.patch) | 2/4 | True | Keeps exclusive bounds and omits documentation updates. |

## What explains the zero family scores

Data: six semantic/edge-case failures and two syntax failures. The syntax failures also retain incorrect underlying logic; the model receives the correct syntax rejection and ends honestly. Multi-tool: four tasks have no effective changes, and four have partial changes or wrong logic/configuration. multi_05 passes all four behavior probes but fails the required liveness configuration. Zero complete tasks does not mean every component is wrong.

Nine of14 false-success cases per arm contain only Python AST-equivalent or JSON-equivalent changes. The five others are bug_01, data_01, data_04, multi_04 and multi_05. In all14, functional acceptance fails; none is rejected solely for documentation wording or transport formatting.

## Confirmed engineering issues

1. The frozen trajectory_dimensions helper understands the old final boolean, not the V5 action=final wire format. It reports118 invalid actions. Re-validating the original202 generations with the actual schema and terminal mapping yields0 invalid actions. This is a reporting defect; the helper does not determine task PASS/FAIL or false_success_claim, so primary scores and14-case counts remain unchanged. See protocol_metric_diagnostic.json.

2. write_file reports changed_paths even when it writes identical bytes. Real R/G CPU counterexamples reproduce this, then submit_completion correctly rejects a success claim because Git has no changes. The original multi_02 exhibits this contradiction. That candidate still fails its explicit idempotence, registry and documentation requirements. The feedback defect may confuse a model; its causal contribution is not measured here.

3. The actual pinned tokenizer/mask accepts33 of36 preferred reference action tokenizations. Three configuration strings in multi_04/multi_05 are rejected at token106891 (escaped quote followed by a backslash), despite character-level JSON validity. Splitting that token preserves the exact original bytes and is accepted in all three cases; compact equivalent JSON also passes. All reference actions are at most137 tokens, and reference workflows fit the12-turn budget. This establishes an unnecessarily restrictive token-mask path, not an impossible task or a proven explanation of the observed model choices. See mask_edge_checks.json.

The previously disclosed five R exception events without separate arguments remain untouched; their same-turn raw actions are preserved. They do not explain the investigated40 rows.

## Oracle and counterfactual controls

All20 original R candidates were independently replayed in Docker and reproduced FAIL; each G candidate is byte-identical. All20 complete reference patches pass the same Oracle. Sixty-eight behavior vectors were independently calculated from the written specifications; the configuration-only timeout contract was separately checked. No wrong expected value causing the investigated failures was found. Coverage is finite and not a proof of universal Oracle correctness.

Separate CPU counterfactuals show: fixing only syntax in data_05/data_06 still leaves MiB/clamping defects; fixing the remaining logic passes. Correcting only config/probes.json makes the existing multi_05 candidate pass. Repairing Decimal rounding/JSON serialization in bug_01 exposes its fixed=0 bug; repairing that too passes. Correcting multi_04 file-content-as-path misuse removes FileNotFoundError but leaves counting/config errors; repairing those passes. These are diagnostic edits, not model outputs, and receive no credit in original scores.

## Attribution and next steps

The observed code and workflow failures are real in this fixed setup. They do not establish intrinsic Apertus inability, because prompting, quantization, constrained decoding and syntax-only feedback have not been independently varied. Functional feedback was explicitly unavailable on Kaggle. Completion acceptance checks changes and syntax, not hidden behavior; Engine evidence therefore does not certify task correctness.

Before future inference, fix and CPU-regress the protocol metric and token-mask conformance, clarify written_paths versus actual changed_paths, and label accepted submissions as pending external functional evaluation. Preserve Version23 as development evidence and document these defects. Do not rerun only failed tasks or silently replace scores. No GPU run was authorized or performed by this diagnosis.

## Evidence

Per-task folders contain original prompts, trajectory, patch, claim, Oracle and reference snapshots. Original file hashes before/after match. CPU probes, independent calculations, paired-input checks and decoder counterexamples are stored separately in this directory.

Export note: original diagnostic subfolders and CPU counterfactual logs are not included in this curated export. Their prior findings are retrospective summaries, not newly run controls; recorded candidates, external Oracle definitions and reference contents are provided for scrutiny.
