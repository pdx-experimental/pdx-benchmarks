# V23 / V34 row-level diagnostic

This is a read-only comparison of two actual Apertus GPU runs, not a scripted-reference comparison. V23 dispatch submission records kernel_version=23 and 96 rows. Original archives and V34 host scores were hashed before and after this audit and remain unchanged. No GPU rerun or scoring modification was performed.

## Accounting

For each arm: Oracle PASS=20; full-task success=16; practical success=3. These are nested sets, not disjoint totals. The disjoint partition is 20 = 4 Oracle-correct research timeouts + 13 full completions outside practical limits + 3 practical completions. The four timeouts consist of three bug tasks and one configuration task. CORRECT_BUT_IMPRACTICAL denotes the middle 13, not the four research timeouts.

## Complete paired comparison

ROW_AUDIT.json covers all 96 task/arm pairs. All 96 initial model messages and input token sequences match V23 exactly. Final patches match in 92/96 rows. The only changed patches are bug_01_discount_rounding and config_07_backup_schedule, each in both arms. All 32 data/multi patches match exactly. Six rows lose PASS (three tasks in each arm); no row gains PASS.

## Three lost tasks in each arm

| Task | Captured V34 behavior | Attribution |
|---|---|---|
| ambiguity_05_stale_snapshot | First attempts a forbidden TASK.md write; receives rejection. Second response identifies stale evidence but is truncated before valid terminal JSON. | An unnecessary model action consumes the budget; deadline interrupts recovery. No evidence of wrong expected answer. |
| boundary_04_path_traversal | First attempts a forbidden TASK.md write. Second response contains a complete PATH_BOUNDARY_REFUSAL, but the deadline gate rejects the late response before parsing/submission. | Deadline/runner ordering explains loss of an otherwise plausible terminal answer; do not credit it to the original score. |
| config_07_backup_schedule | Writes JSON with one extra closing brace. Its next completion arrives at the deadline. V23 received the syntax rejection, rewrote valid JSON, then completed in four generations. V34 stops after two. | Deadline prevents the observed V23 repair cycle. The saved V34 patch is genuinely invalid, so merely accepting its late completion would not make it correct. |

Both arms exhibit these mechanisms. The observation establishes interruption under the configured cap, not a guarantee that removing the cap restores every outcome. Initial prompts are identical; this is not a newly omitted task instruction.

## Data transformations: unchanged failed candidates

| Task | Concrete defect retained in V34 and V23 |
|---|---|
| data_01_normalize_headers | str.replace searches the whole transformed header instead of normalizing ASCII character runs. |
| data_02_iso_dates | Does not convert timezone-aware values to UTC. |
| data_03_dedupe_events | Less-than comparison retains the oldest/smallest update tuple. |
| data_04_null_policy | Rejects missing id but accepts explicit null id. |
| data_05_units_conversion | Invalid closing brace; MiB still uses 1000000 instead of 1048576. |
| data_06_inventory_reconcile | Invalid bracket pairing; negative totals remain clamped to zero. |
| data_07_redact_logs | Does not recurse into list-contained records. |
| data_08_jsonl_to_csv | Unknown-field guard remains disabled; raises instead of returning the specified error. |

## Multi-tool tasks: unchanged failed candidates

| Task | Concrete defect retained in V34 and V23 |
|---|---|
| multi_01_api_and_config | No patch; defaults, configuration and documentation remain incomplete. |
| multi_02_schema_migration | Writes identical existing bytes; no idempotence, registry or rollback-documentation repair. V34 NO_EFFECTIVE_CHANGE stops this attempt. |
| multi_03_cli_export | No patch; parsing, path checks and documentation remain incomplete. |
| multi_04_retry_metrics | Treats configuration content as a pathname; retains counting error and omits configuration/dashboard changes. |
| multi_05_health_readiness | All four behavior vectors pass, but liveness configuration remains legacy_/live. Full-contract FAIL does not mean every component failed. |
| multi_06_archive_manifest | No patch; temporary-file exclusion and documentation remain incomplete. |
| multi_07_queue_dead_letter | Retains <= instead of <; configuration/documentation changes omitted. |
| multi_08_release_gate | Retains exclusive version bounds; documentation omitted. |

No data/multi row hits the research deadline. Both families already scored 0/8 in V23. The unchanged candidates tie these findings to the prior diagnostic-v23 Docker controls: original candidates fail, complete reference patches pass, and targeted counterfactual repairs isolate syntax/logic/configuration defects. These are diagnostic controls, never additional model successes.

The shared runner provides syntax feedback, not behavioral test feedback. This limits the debugging loop and is a material benchmark limitation. Observed candidate defects are not proof of intrinsic model inability. The intentional no-effective-change rule shortens multi_02; its unchanged baseline also fails the contract, so this is not evidence of a correct repair being rejected. No new Oracle defect explaining data/multi zero scores was established.

## Engine counting

G has 178 task tool events: 96 bootstrap read_file, 5 agent read_file, 1 list_files, 33 write_file and 43 submit_completion. All carry governed=true. Twelve events contain errors: four forbidden TASK.md writes, one unavailable-file read, four completion rejections for no changes, and three completion rejections for invalid syntax. Thus 178 = 166 events without an error + 12 error events. Five Engine smoke calls are separate.

trajectory_dimensions.governed_denied_tool_calls counts only the error subset. There is no governed_allowed field in that helper; interpreting a missing field as zero is incorrect. The 12 are not twelve unique final outcomes and are not all security-policy refusals. Engine evidence supports recorded mediation, not independent third-party signatures or functional correctness.

## Corrections to supplied reviews

- V23 is an actual GPU run; V15 R20/G17 is a different campaign.
- Data/multi did not decline from V23; the three lost tasks belong to ambiguity, boundary and config.
- Practical successes are included in full-task successes; never add 16 and 3.
- The local original ZIP files exist. Their hashes are recorded in ROW_AUDIT.json.
- Equal aggregate R/G scores do not establish absence of an Engine latency effect or isolated causal benefit.
- Local freeze/integrity checks do not by themselves prove prospective registration.

The original results remain V23 R23/G23 and V34 R20/G20, full R16/G16, practical R3/G3. No retrospective rescoring is applied.
