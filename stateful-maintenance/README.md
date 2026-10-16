# Stateful Python maintenance: development evidence

This release examines whether an Apertus 8B assistant can deliver small Python and configuration changes under restricted tools. These are exposed development tasks, not an independent held-out study. Reports are drafts, not submitted or published papers.

## Results and denominators

Each version contains the same 48 tasks, evaluated in R and G (96 rows). The two versions are repeated measurements of an exposed cohort; their 192 rows are not 192 independent tasks and are not added to the A12 denominator.

| Run | R Oracle PASS | G Oracle PASS | R/G full-task success | R/G practical success |
| --- | ---: | ---: | ---: | ---: |
| V23 | 23/48 | 23/48 | Not scored under the V34 deadline policy | Not reported |
| V34 | 20/48 | 20/48 | 16/48 each | 3/48 each |

Oracle PASS means the final saved candidate meets the recorded acceptance contract. Full-task success additionally requires an accepted terminal submission inside the research deadline. Practical success additionally meets the shorter latency threshold. These are nested sets: **20 = 4 Oracle-correct research timeouts + 13 complete but slow tasks + 3 practical completions** per arm. Never add 16 and 3.

Simple tasks have a 30-second research cap and 10-second practical threshold; data/multi tasks have a 90-second cap and 30-second practical threshold. Latency covers resident-model generation, tool use and terminal submission; cold loading and offline host Oracle time are separate. This is not end-to-end user-device latency.

All three practical successes are clarification/refusal tasks. Practical code/configuration maintenance success is zero. V34 finishes with 96 rows, including 11 research timeouts per arm. V23 and V34 both score 0/8 in each of the data and multi-tool families; their 32 paired final patches are byte-identical. See [the diagnostic report](comparison/FINDINGS.md) and [96-row comparison](comparison/V23_V34_COMPARISON.csv).

## Design and enforcement

Both arms use the same model revision, INT8 deployment on dual T4 GPUs, task inputs and narrow tools. R directly calls the shared tool handlers. G additionally mediates calls through the public Engine. Both arms retain the same underlying path and file restrictions. Equal refusal behavior therefore cannot establish an isolated Engine safety improvement.

V34 records 178 G task tool events (96 bootstrap reads and 82 agent calls), including 12 error/rejection events. Five separate smoke calls are excluded from 178. The 12 are a subset, not an alternative total. Exported manifests and hashes bind the recorded events; they are not independently signed third-party attestations, proof of functional correctness, or proof of exhaustive attempt history.

The model receives syntax feedback, not behavioral test feedback. Candidate modules are not executed on the inference host. Functional verification was performed separately using a constrained Docker worker and host-held expected results. The tasks cover bounded Python API and workspace maintenance, not general repository repair, deployment or unrestricted systems administration.

## What this adds to Phase 3

[A12 Phase 3](../slm-task-governance/README.md) observes model-dependent outcomes under bundled schema, exemplar and output-contract changes on fixed DAG tasks. It does not isolate an Engine effect. Here, real code/state acceptance and latency expose a different boundary: recorded mediation does not make incorrect or incomplete edits correct. No task-success advantage for G is observed in these two runs; equal counts are not a statistical equivalence or no-overhead result. The suggested explanation that supplied DAG structure reduces planning demands is a hypothesis, not an identified mechanism.

## Public material

- `cohort/`: all 48 model-visible workspaces and task specifications, registry, external Oracle vectors and reference file contents.
- `runs/v23/`, `runs/v34/`: all prompts/token sequences, tool observations, candidate patches, completion claims, Engine evidence and recorded host evaluations, including every failure.
- `runtime-source/`: retained inference scripts from the frozen input archives, for inspection. These are historical source artifacts, not a turnkey remote submission bundle.
- `comparison/`: complete paired accounting and failure diagnosis.
- `EXPORT_LINEAGE.json`: per-file origin and explicit export transformations. Host temporary-user paths are replaced in derived host evaluations; original result archives remain private and unchanged.
- `PUBLIC_SHA256.json`: current public-byte inventory. Self-generated hashes are not signatures or independent timestamps.

Synthetic `config/secrets.json` fixtures contain test markers, not credentials. Third-party model/package organization identifiers are bibliographic dependencies, not operator accounts.

## Offline verification

From the repository root, with Python 3.10 or later:

```sh
python -B stateful-maintenance/tools/verify_export.py
```

This uses only the standard library and does not execute candidates, inference, Docker or network requests. It verifies exported bytes, complete paired coverage, patch and Engine-event bindings, and recorded accounting. It does not independently validate the scientific design or rerun the Oracle.

For a separate, optional replay of a recorded task, install Git and a working Linux Docker backend, obtain the Python 3.12 slim image in advance, then run:

```sh
python -B stateful-maintenance/tools/replay.py --version v34 --task data_01_normalize_headers
```

The portable adapter retains the recorded Oracle function bodies while relocating imports/default paths. It defaults to `python:3.12-slim`; `PDX_REPLAY_IMAGE` can select a local image. The original local image digest is not established by this export, so a replay is not a byte-identical environment claim. Expected results stay on the host. Candidate replies remain untrusted; finite hidden vectors can be gamed and are not a formal security proof. No Docker replay or new model experiment was run for this release preparation.

## Development history and exclusions

V23 and V34 were selected for complete-result comparison, not as the only attempts. Earlier development, interrupted jobs and unsuccessful admission attempts occurred. [The attempt-history disclosure](ATTEMPT_HISTORY.md) records the retained inventory and its limitations. Complete independently authenticated remote attempt histories and prospective registration are not established.

Excluded: cloud/operator account metadata, credentials, deployment notebooks, downloaded wheels, private Git objects, cache files, raw platform logs and duplicate archive containers. This does not justify removing failed rows from the two released runs. Public sources should not be assumed safe to execute outside the documented Docker boundaries.
