# Development attempt disclosure

V23 and V34 are complete model-output comparisons, not the only executions. Earlier CPU binding jobs, GPU admission attempts, interrupted runs, latency diagnostics and alternative protocols occurred. The local records include installation/runtime failures, externally stopped runs and a SIGSEGV-interrupted full run with 38 recovered rows. These are excluded from the two complete-run denominators, not asserted to be nonexistent.

The machine-readable attempt_inventory.json lists retained submission/recovery metadata containing explicit version fields, with original-record hashes and locally asserted scope/status. Missing statuses are unknown. This discovery rule is partial: candidate submissions, scripted fixtures and per-row records are excluded, and some remote attempts have no retained submission metadata. It is not an exhaustive or independently authenticated cloud attempt ledger.

V23 uses the earlier full compatibility flow. Later development fixed protocol metric accounting, byte-identical write feedback and a tokenizer-mask escape edge. Intervening speed/diagnostic variants are not presented as comparable confirmation. V34 restores the V23 task-visible baseline with repaired feedback/decoding and explicit time/no-effective-change stopping rules. Exposed tasks and post-result engineering changes prevent a held-out confirmatory interpretation.

V23 and V34 include every recovered row of those selected complete runs. No original score is overwritten, and diagnostic repairs are never counted as additional model successes. Raw platform logs and account-bearing deployment metadata are excluded for privacy. Their absence limits independent assessment of remote start identity and exhaustive retry history.
