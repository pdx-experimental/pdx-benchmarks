# === 5. Standardized 21 RULER Benchmark Tasks ===
"""Comprehensive Two-Tier Benchmark Suite for PDX Phase 0 Large-Scale Evaluation.

Contains 76 standardized tasks across two distinct difficulty tiers:
=== Tier 1: Level 1 Baseline (40 tasks) ===
1. gaia_l1 (15 tasks): Single-step tool use, document audit, numerical calculation.
2. ruler_l1 (15 tasks): Single-needle retrieval across 4k to 32k contexts.
3. swe_l1 (10 tasks): Basic Python bug fixes and schema validations.

=== Tier 2: Level 2 Advanced (36 tasks) ===
4. dag_chain (8 tasks): Multi-step DAG tool chaining with strict upstream dependencies.
5. gaia_l2 (8 tasks): GAIA Level 2 multi-tool tabular and multi-constraint reasoning.
6. swe_algo (8 tasks): Algorithmic Python code repair with unit test verification.
7. gsm8k_hard (6 tasks): Multi-step compound arithmetic requiring tool calculator execution.
8. ruler_multihop (6 tasks): Multi-hop needle-in-a-haystack context retrieval (6k-12k tokens).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkTask:
    task_id: str
    suite: str
    tier: str  # "level_1" or "level_2"
    prompt: str
    context: str
    tools: List[Dict[str, Any]]
    expected_answer: str
    pdx_steps: List[Dict[str, Any]]
    max_steps: int = 5
    difficulty: str = "medium"

    def get_full_gold_steps(self) -> List[Dict[str, Any]]:
        steps = [dict(s) for s in self.pdx_steps]
        if not any(s.get("id") == "step_final" for s in steps):
            prev_ids = [s["id"] for s in steps]
            steps.append({
                "id": "step_final",
                "kind": "final",
                "instruction": "Output the task's final answer only.",
                "depends_on": prev_ids,
            })
        return steps

    def to_pdx_plan(self) -> Dict[str, Any]:
        return {
            "schema_version": "pdx_execution_plan_v1",
            "request_id": f"phase0_{self.suite}_{self.task_id}",
            "producer": {"type": "benchmark", "name": f"pdx-phase0-{self.suite}"},
            "intent": {
                "summary": self.prompt,
                "suite": self.suite,
                "tier": self.tier,
                "task_id": self.task_id,
                "max_steps": self.max_steps,
            },
            "environment": {
                "context_length": len(self.context),
                "available_tools": [t.get("name") for t in self.tools],
            },
            "steps": self.get_full_gold_steps(),
            "verification": [
                {
                    "id": "final_answer_match",
                    "check": "exact_or_substring",
                    "expected": self.expected_answer,
                }
            ],
            "policies": {
                "timeout_seconds": 600,
                "max_retries": 1,
                "default_approval_required": False,
            },
        }


def _noise(lines: int, text: str = "System telemetry OK. Cluster health nominal. P99 latency within SLA bounds.\n") -> str:
    return text * lines


BENCHMARK_TASKS: List[BenchmarkTask] = [
    # =========================================================================
    # TIER 1: LEVEL 1 BASELINE (40 tasks)
    # =========================================================================

    # 1. GAIA Level 1 (15 tasks)
    BenchmarkTask("gaia_01_revenue_calc", "gaia_l1", "level_1", "Find total revenue in Q3 2024 and compute year-over-year growth rate compared to Q3 2023.", "Financial Report: 2023 Q3 Revenue was $120.0M. 2024 Q3 Revenue was $156.0M.", [{"name": "calc"}], "30%", [
        {"id": "step_1_calc", "kind": "tool", "tool": "calc", "instruction": "Compute ((156.0 - 120.0) / 120.0) * 100", "depends_on": []}
    ]),
    BenchmarkTask("gaia_02_file_audit", "gaia_l1", "level_1", "Examine the system manifest and output the single invalid file name if any.", "Manifest: file_a.pdf: valid; file_b.docx: INVALID; file_c.json: valid", [{"name": "json_filter"}], "file_b.docx", [
        {"id": "step_1_audit", "kind": "transform", "instruction": "Examine manifest and identify invalid file name", "depends_on": []}
    ]),
    BenchmarkTask("gaia_03_date_calc", "gaia_l1", "level_1", "Calculate the day difference between deployment on 2024-05-10 and verification on 2024-05-24.", "Project log: start=2024-05-10, verified=2024-05-24.", [{"name": "calc"}], "14", [
        {"id": "step_1_diff", "kind": "tool", "tool": "calc", "instruction": "Compute 24 - 10", "depends_on": []}
    ]),
    BenchmarkTask("gaia_04_author_lookup", "gaia_l1", "level_1", "Find the author of spec document PRODOCUX_SPEC_V2.", "Registry: PRODOCUX_SPEC_V2 authored by Ada Lovelace, approved by QA team.", [{"name": "db_lookup"}], "Ada Lovelace", [
        {"id": "step_1_author", "kind": "transform", "instruction": "Identify author of PRODOCUX_SPEC_V2 from context", "depends_on": []}
    ]),
    BenchmarkTask("gaia_05_version_filter", "gaia_l1", "level_1", "Find the latest release version among v1.2, v2.0.1, v1.9, and v2.1.0-rc1.", "Release tags: v1.2, v2.0.1, v1.9, v2.1.0-rc1.", [{"name": "json_filter"}], "v2.1.0-rc1", [
        {"id": "step_1_filter", "kind": "transform", "instruction": "Find highest semver among candidate versions", "depends_on": []}
    ]),
    BenchmarkTask("gaia_06_port_inspect", "gaia_l1", "level_1", "What is the default HTTP service port specified for ProDocuX adapter?", "Config: server.host=0.0.0.0, server.port=8080, mode=production.", [{"name": "db_lookup"}], "8080", [
        {"id": "step_1_port", "kind": "transform", "instruction": "Extract server.port value from config", "depends_on": []}
    ]),
    BenchmarkTask("gaia_07_status_count", "gaia_l1", "level_1", "Count the total number of failed jobs in the batch execution log.", "Jobs: job_1=success, job_2=failed, job_3=failed, job_4=success, job_5=failed.", [{"name": "calc"}], "3", [
        {"id": "step_1_count", "kind": "transform", "instruction": "Count failed jobs in log list", "depends_on": []}
    ]),
    BenchmarkTask("gaia_08_token_estimate", "gaia_l1", "level_1", "Estimate token cost for 500k words with a multiplier of 1.3 tokens/word.", "Formula: tokens = 500000 * 1.3.", [{"name": "calc"}], "650000", [
        {"id": "step_1_estimate", "kind": "tool", "tool": "calc", "instruction": "Compute 500000 * 1.3", "depends_on": []}
    ]),
    BenchmarkTask("gaia_09_duplicate_finder", "gaia_l1", "level_1", "Identify the duplicated asset ID present in the asset registration list.", "Assets: asset_1012, asset_4402, asset_9918, asset_3301, asset_9918.", [{"name": "db_lookup"}], "asset_9918", [
        {"id": "step_1_dup", "kind": "transform", "instruction": "Identify duplicated asset identifier", "depends_on": []}
    ]),
    BenchmarkTask("gaia_10_missing_key", "gaia_l1", "level_1", "Identify the missing required configuration key among host, port, and database_uri.", "Supplied config: {'host': 'localhost', 'port': 5432}.", [{"name": "json_filter"}], "database_uri", [
        {"id": "step_1_missing", "kind": "transform", "instruction": "Identify which required key is missing", "depends_on": []}
    ]),
    BenchmarkTask("gaia_11_max_latency", "gaia_l1", "level_1", "Identify the service with the highest latency from the telemetry table.", "Latency table: auth=45ms, db=120ms, image_embedder=890ms, cache=5ms.", [{"name": "db_lookup"}], "image_embedder", [
        {"id": "step_1_max", "kind": "transform", "instruction": "Identify service name with maximum latency", "depends_on": []}
    ]),
    BenchmarkTask("gaia_12_permission_check", "gaia_l1", "level_1", "What user role is required to access the /export endpoint?", "Security policy: /view requires user, /export requires admin, /ping is public.", [{"name": "db_lookup"}], "admin", [
        {"id": "step_1_role", "kind": "transform", "instruction": "Extract role requirement for /export endpoint", "depends_on": []}
    ]),
    BenchmarkTask("gaia_13_file_size_sum", "gaia_l1", "level_1", "Sum the total size of attachments in MB: file1=12MB, file2=45MB, file3=18MB.", "Attachments: 12MB, 45MB, 18MB.", [{"name": "calc"}], "75", [
        {"id": "step_1_sum", "kind": "tool", "tool": "calc", "instruction": "Compute 12 + 45 + 18", "depends_on": []}
    ]),
    BenchmarkTask("gaia_14_hash_verify", "gaia_l1", "level_1", "Identify the MD5 prefix recorded for artifact release package.", "Checksum table: package_zip=a8f9c1e0992..., status=verified.", [{"name": "crypto_transform"}], "a8f9c1", [
        {"id": "step_1_hash", "kind": "transform", "instruction": "Extract first 6 hex characters of package_zip checksum", "depends_on": []}
    ]),
    BenchmarkTask("gaia_15_dependency_order", "gaia_l1", "level_1", "Resolve the top-level prerequisite package for pkg_c if pkg_c depends on pkg_b, which depends on pkg_a.", "Dependency chain: pkg_c -> pkg_b -> pkg_a.", [{"name": "db_lookup"}], "pkg_a", [
        {"id": "step_1_dep", "kind": "transform", "instruction": "Resolve root prerequisite package name", "depends_on": []}
    ]),

    # 2. RULER Level 1 (15 tasks)
    BenchmarkTask("ruler_01_needle_4k", "ruler_l1", "level_1", "What is the secret deployment token assigned to server node-melbourne-4?", _noise(60) + "server node-melbourne-4 token is TRN2-SECRET-MEL-9921.\n" + _noise(60), [{"name": "grep"}], "TRN2-SECRET-MEL-9921", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for token assigned to node-melbourne-4", "depends_on": []}
    ]),
    BenchmarkTask("ruler_02_needle_4k_ip", "ruler_l1", "level_1", "What is the internal IP address assigned to node-brazil-01?", _noise(70) + "Internal IP for node-brazil-01 is 10.240.12.88.\n" + _noise(60), [{"name": "grep"}], "10.240.12.88", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for IP address of node-brazil-01", "depends_on": []}
    ]),
    BenchmarkTask("ruler_03_needle_8k_key", "ruler_l1", "level_1", "Find the active production API key for payment gateway.", _noise(120) + "The active production key is sk-live-prod-88716.\n" + _noise(120), [{"name": "grep"}], "sk-live-prod-88716", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for production API key for payment gateway", "depends_on": []}
    ]),
    BenchmarkTask("ruler_04_needle_8k_city", "ruler_l1", "level_1", "Which AWS region is designated for Capacity Block reservations?", _noise(130) + "Designated Capacity Block region is ap-southeast-4 (Melbourne).\n" + _noise(110), [{"name": "grep"}], "ap-southeast-4", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for designated Capacity Block AWS region", "depends_on": []}
    ]),
    BenchmarkTask("ruler_05_needle_16k_uuid", "ruler_l1", "level_1", "Extract the run UUID of the failed pipeline job.", _noise(180) + "Pipeline failed: run_id=b4901f4a-9912-4c22-86ee-23ad4123.\n" + _noise(180), [{"name": "grep"}], "b4901f4a-9912-4c22-86ee-23ad4123", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for run_id of failed pipeline", "depends_on": []}
    ]),
    BenchmarkTask("ruler_06_needle_16k_user", "ruler_l1", "level_1", "Which user account was flagged for multiple failed login attempts?", _noise(190) + "Security alert: suspicious activity on account user_victor_99.\n" + _noise(190), [{"name": "grep"}], "user_victor_99", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for suspicious activity flagged user account", "depends_on": []}
    ]),
    BenchmarkTask("ruler_07_needle_32k_pass", "ruler_l1", "level_1", "What is the recovery passphrase stored in the disaster backup record?", _noise(260) + "Emergency recovery passphrase: crimson-falcon-orbit-992.\n" + _noise(260), [{"name": "grep"}], "crimson-falcon-orbit-992", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for emergency recovery passphrase", "depends_on": []}
    ]),
    BenchmarkTask("ruler_08_multihop_4k", "ruler_l1", "level_1", "Track user session user_882: find login IP and final exported file ID.", _noise(60) + "user_882 login from 192.168.10.42.\n" + _noise(50) + "user_882 exported artifact_doc_7719.pdf.\n" + _noise(40), [{"name": "grep"}], "192.168.10.42", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search user_882 login IP address", "depends_on": []}
    ]),
    BenchmarkTask("ruler_09_multihop_8k", "ruler_l1", "level_1", "Find the author and commit hash that introduced the hotfix.", _noise(110) + "Commit 7a88b19 merged by Alice Zhang (hotfix: memory leak).\n" + _noise(120), [{"name": "grep"}], "Alice Zhang", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search for author of hotfix commit", "depends_on": []}
    ]),
    BenchmarkTask("ruler_10_multihop_8k_rel", "ruler_l1", "level_1", "What is the child task ID spawned by task_root_101?", _noise(120) + "Parent task_root_101 spawned subtask task_sub_404 successfully.\n" + _noise(110), [{"name": "grep"}], "task_sub_404", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search subtask spawned by task_root_101", "depends_on": []}
    ]),
    BenchmarkTask("ruler_11_multihop_16k", "ruler_l1", "level_1", "Identify the server node and rule name that triggered the OOM kill event.", _noise(180) + "Host node_us_east_2 triggered alert RULE_OOM_KILL.\n" + _noise(180), [{"name": "grep"}], "RULE_OOM_KILL", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search rule name triggering OOM kill alert", "depends_on": []}
    ]),
    BenchmarkTask("ruler_12_multihop_16k_order", "ruler_l1", "level_1", "Identify the buyer company and transaction ID for order 99201.", _noise(190) + "Order 99201: buyer=Acquired By Globex, transaction=tx_pay_88190.\n" + _noise(180), [{"name": "grep"}], "Globex", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search buyer for order 99201", "depends_on": []}
    ]),
    BenchmarkTask("ruler_13_multihop_32k", "ruler_l1", "level_1", "What was the root cause hardware failure identified in incident report #402?", _noise(260) + "Incident #402 Root Cause: disk_controller_failure on rack_c7.\n" + _noise(260), [{"name": "grep"}], "disk_controller_failure", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Search root cause of incident #402", "depends_on": []}
    ]),
    BenchmarkTask("ruler_14_aggregation_8k", "ruler_l1", "level_1", "State the total count of distinct error codes recorded in the error log.", _noise(110) + "Errors: ERR_401, ERR_404, ERR_500, ERR_502. All 4 distinct errors acknowledged.\n" + _noise(110), [{"name": "calc"}], "4", [
        {"id": "step_1_count", "kind": "transform", "instruction": "Count distinct error codes listed in log", "depends_on": []}
    ]),
    BenchmarkTask("ruler_15_aggregation_16k", "ruler_l1", "level_1", "What is the most frequent telemetry event code observed in the system stream?", _noise(180) + "Summary: EVENT_DISCONNECT: 2, EVENT_TIMEOUT: 5, HEARTBEAT_ACK: 1042.\n" + _noise(180), [{"name": "grep"}], "HEARTBEAT_ACK", [
        {"id": "step_1_grep", "kind": "tool", "tool": "grep", "instruction": "Identify most frequent telemetry event", "depends_on": []}
    ]),

    # 3. SWE Level 1 (10 tasks)
    BenchmarkTask("swe_01_division_zero", "swe_l1", "level_1", "Fix ZeroDivisionError in compute_average(items) when items list is empty, returning 0.0.", "def compute_average(items): return sum(items)/len(items) if items else 0.0", [], "0.0", [
        {"id": "step_1_fix", "kind": "transform", "instruction": "Provide safe average fallback return value", "depends_on": []}
    ]),
    BenchmarkTask("swe_02_json_schema_repair", "swe_l1", "level_1", "Identify missing required receipt digest field in schema.", "Receipt requires: run_id, status, receipt_sha256.", [{"name": "json_filter"}], "receipt_sha256", [
        {"id": "step_1_field", "kind": "transform", "instruction": "Identify required receipt digest field name", "depends_on": []}
    ]),
    BenchmarkTask("swe_03_list_index_error", "swe_l1", "level_1", "What should pop() on an empty stack return when guarded safely with default?", "def safe_pop(stack): return stack.pop() if stack else None", [], "None", [
        {"id": "step_1_pop", "kind": "transform", "instruction": "Identify safe default return value for empty pop", "depends_on": []}
    ]),
    BenchmarkTask("swe_04_sql_injection", "swe_l1", "level_1", "Which dangerous technique should be replaced by parameterized queries: string formatting or cursor binding?", "Review: query = f'SELECT * FROM users WHERE id = {user_id}'", [], "string formatting", [
        {"id": "step_1_sec", "kind": "transform", "instruction": "Identify vulnerable technique name", "depends_on": []}
    ]),
    BenchmarkTask("swe_05_regex_escape", "swe_l1", "level_1", "What character must be escaped with a backslash to match a literal period in regex?", "Regex problem: pattern = 'www.google.com'", [], "\\.", [
        {"id": "step_1_regex", "kind": "transform", "instruction": "Provide literal period regex escape sequence", "depends_on": []}
    ]),
    BenchmarkTask("swe_06_dict_get_fallback", "swe_l1", "level_1", "Which dictionary method safely retrieves a value with a fallback default?", "Method options: dict.pop, dict.keys, dict.get.", [], "dict.get", [
        {"id": "step_1_method", "kind": "transform", "instruction": "Identify safe dictionary lookup method", "depends_on": []}
    ]),
    BenchmarkTask("swe_07_type_hint_fix", "swe_l1", "level_1", "Specify the proper typing annotation for a variable that can be string or None.", "Typing options: Union[str, int], Optional[str], List[str].", [], "Optional[str]", [
        {"id": "step_1_hint", "kind": "transform", "instruction": "Select proper type hint annotation", "depends_on": []}
    ]),
    BenchmarkTask("swe_08_retry_decorator", "swe_l1", "level_1", "What parameter name sets the maximum retry attempts in the tenacity retry decorator?", "Example: @retry(stop=stop_after_attempt(3), max_retries=3)", [], "max_retries=3", [
        {"id": "step_1_retry", "kind": "transform", "instruction": "Identify parameter name setting retry limit", "depends_on": []}
    ]),
    BenchmarkTask("swe_09_datetime_iso", "swe_l1", "level_1", "What is the standard ISO8601 representation of midnight UTC on September 16, 2026?", "Format requirement: YYYY-MM-DDTHH:MM:SSZ", [], "2026-09-16T00:00:00Z", [
        {"id": "step_1_iso", "kind": "transform", "instruction": "Provide exact ISO8601 midnight timestamp", "depends_on": []}
    ]),
    BenchmarkTask("swe_10_subprocess_check", "swe_l1", "level_1", "Which parameter in subprocess.run ensures an exception is raised on non-zero exit code?", "Options: capture_output=True, check=True, shell=True.", [], "check=True", [
        {"id": "step_1_check", "kind": "transform", "instruction": "Identify subprocess argument raising on failure", "depends_on": []}
    ]),

    # =========================================================================
    # TIER 2: LEVEL 2 ADVANCED (36 tasks)
    # =========================================================================

    # 4. DAG Tool Chaining (8 tasks)
    BenchmarkTask(
        task_id="dag_01_db_decrypt_verify",
        suite="dag_chain",
        tier="level_2",
        prompt="Query user vault record for user_819, decrypt the base64 token, and output the decrypted authentication string.",
        context="Vault server: vault.pdx.internal:8200",
        tools=[{"name": "db_lookup"}, {"name": "crypto_transform"}],
        expected_answer="PDX_AUTH_9921",
        pdx_steps=[
            {"id": "step_1_lookup", "kind": "tool", "tool": "db_lookup", "instruction": "Query db_lookup for 'user_819'", "depends_on": []},
            {"id": "step_2_decrypt", "kind": "tool", "tool": "crypto_transform", "instruction": "Decode base64 payload from step_1_lookup", "depends_on": ["step_1_lookup"]},
            {"id": "step_3_verify", "kind": "verify", "instruction": "Extract authentication token string", "depends_on": ["step_2_decrypt"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_02_metrics_variance_calc",
        suite="dag_chain",
        tier="level_2",
        prompt="Lookup latency metrics for cluster 'cl_alpha', calculate the mean latency, and then calculate max deviation from the mean.",
        context="Cluster telemetry registry available via db_lookup.",
        tools=[{"name": "db_lookup"}, {"name": "calc"}],
        expected_answer="18.0",
        pdx_steps=[
            {"id": "step_1_metrics", "kind": "tool", "tool": "db_lookup", "instruction": "Lookup latency list for 'cl_alpha'", "depends_on": []},
            {"id": "step_2_mean", "kind": "tool", "tool": "calc", "instruction": "Compute average latency from step_1_metrics", "depends_on": ["step_1_metrics"]},
            {"id": "step_3_deviation", "kind": "tool", "tool": "calc", "instruction": "Compute max deviation (160 - mean)", "depends_on": ["step_2_mean"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_03_log_filter_aggregate",
        suite="dag_chain",
        tier="level_2",
        prompt="Filter server log for incidents with status >= 500, then calculate total affected users by summing affected_users across matching incidents.",
        context="Incident logs: [{'id': 101, 'status': 503, 'affected_users': 210}, {'id': 102, 'status': 200, 'affected_users': 0}, {'id': 103, 'status': 500, 'affected_users': 215}]",
        tools=[{"name": "json_filter"}, {"name": "calc"}],
        expected_answer="425",
        pdx_steps=[
            {"id": "step_1_filter", "kind": "tool", "tool": "json_filter", "instruction": "Filter incidents where status >= 500", "depends_on": []},
            {"id": "step_2_sum", "kind": "tool", "tool": "calc", "instruction": "Sum affected_users from step_1_filter: 210 + 215", "depends_on": ["step_1_filter"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_04_api_chain_exchange",
        suite="dag_chain",
        tier="level_2",
        prompt="Lookup exchange rates EUR->USD and USD->JPY from forex database, then compute the exact JPY conversion for 500 EUR.",
        context="Forex gateway online.",
        tools=[{"name": "db_lookup"}, {"name": "calc"}],
        expected_answer="83700",
        pdx_steps=[
            {"id": "step_1_forex", "kind": "tool", "tool": "db_lookup", "instruction": "Lookup forex rates EUR_USD and USD_JPY", "depends_on": []},
            {"id": "step_2_convert", "kind": "tool", "tool": "calc", "instruction": "Compute 500 * EUR_USD * USD_JPY (500 * 1.08 * 155.0)", "depends_on": ["step_1_forex"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_05_auth_hash_signature",
        suite="dag_chain",
        tier="level_2",
        prompt="Lookup secret salt for service 'auth_gate', concatenate with session token 'sess_8892', and compute sha256 digest prefix.",
        context="Auth security config partition.",
        tools=[{"name": "db_lookup"}, {"name": "crypto_transform"}],
        expected_answer="e5a190b2",
        pdx_steps=[
            {"id": "step_1_salt", "kind": "tool", "tool": "db_lookup", "instruction": "Lookup salt for auth_gate", "depends_on": []},
            {"id": "step_2_hash", "kind": "tool", "tool": "crypto_transform", "instruction": "Compute sha256 of sess_8892:SALT_772", "depends_on": ["step_1_salt"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_06_inventory_reorder_qty",
        suite="dag_chain",
        tier="level_2",
        prompt="Lookup stock of 'SKU_9021' (current=45, target=100, batch_size=20), then calculate how many integer batches must be ordered to reach or exceed target.",
        context="ERP inventory warehouse 3.",
        tools=[{"name": "db_lookup"}, {"name": "calc"}],
        expected_answer="3",
        pdx_steps=[
            {"id": "step_1_stock", "kind": "tool", "tool": "db_lookup", "instruction": "Lookup SKU_9021 parameters", "depends_on": []},
            {"id": "step_2_calc", "kind": "tool", "tool": "calc", "instruction": "Compute ceil((100 - 45) / 20)", "depends_on": ["step_1_stock"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_07_cas_blob_verify",
        suite="dag_chain",
        tier="level_2",
        prompt="Lookup CAS manifest for artifact 'pkg_linux_x64', verify checksum status, and report root verification status.",
        context="CAS Storage Cluster A.",
        tools=[{"name": "db_lookup"}, {"name": "crypto_transform"}],
        expected_answer="ROOT_MERKLE_OK",
        pdx_steps=[
            {"id": "step_1_manifest", "kind": "tool", "tool": "db_lookup", "instruction": "Lookup manifest for pkg_linux_x64", "depends_on": []},
            {"id": "step_2_verify", "kind": "verify", "instruction": "Check merkle root match", "depends_on": ["step_1_manifest"]},
        ],
    ),
    BenchmarkTask(
        task_id="dag_08_pipeline_stage_dependency",
        suite="dag_chain",
        tier="level_2",
        prompt="Trace job pipeline for 'deploy_prod', find which dependent stage failed and prevented deployment.",
        context="CI Pipeline trace: build -> unit_test -> lint_check (FAILED) -> integration_test (SKIPPED) -> deploy_prod (BLOCKED)",
        tools=[{"name": "json_filter"}],
        expected_answer="lint_check",
        pdx_steps=[
            {"id": "step_1_trace", "kind": "tool", "tool": "json_filter", "instruction": "Filter failed pipeline stages", "depends_on": []},
            {"id": "step_2_resolve", "kind": "verify", "instruction": "Identify blocking failed stage name", "depends_on": ["step_1_trace"]},
        ],
    ),

    # 5. GAIA Level 2 Multi-Tool Challenges (8 tasks)
    BenchmarkTask(
        task_id="gaia_l2_01_multisheet_finance",
        suite="gaia_l2",
        tier="level_2",
        prompt="From financial statement, compute Net Profit Margin: Total Revenue is $450M, Total Operating Costs are $310M, Tax is $57.2M. Margin = (Revenue - Costs - Tax) / Revenue.",
        context="Annual Statement: Revenue=$450,000,000; Operating_Cost=$310,000,000; Tax=$57,200,000.",
        tools=[{"name": "calc"}],
        expected_answer="18.4%",
        pdx_steps=[
            {"id": "step_1_net_profit", "kind": "tool", "tool": "calc", "instruction": "Compute 450 - 310 - 57.2", "depends_on": []},
            {"id": "step_2_margin", "kind": "tool", "tool": "calc", "instruction": "Compute (82.8 / 450) * 100", "depends_on": ["step_1_net_profit"]},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_02_server_fleet_capacity",
        suite="gaia_l2",
        tier="level_2",
        prompt="Determine minimum hourly cost to provision at least 128 vCPUs and 512GB RAM using fleet instances: type_a (32 vCPU, 128GB, $3.60/hr) vs type_b (64 vCPU, 256GB, $7.10/hr).",
        context="Cloud catalog: type_a=$3.60/hr (32 vCPU, 128GB RAM), type_b=$7.10/hr (64 vCPU, 256GB RAM). Need 128 vCPU, 512GB RAM.",
        tools=[{"name": "calc"}],
        expected_answer="$14.20",
        pdx_steps=[
            {"id": "step_1_cost_a", "kind": "tool", "tool": "calc", "instruction": "Compute 4 * 3.60", "depends_on": []},
            {"id": "step_2_cost_b", "kind": "tool", "tool": "calc", "instruction": "Compute 2 * 7.10", "depends_on": []},
            {"id": "step_3_min", "kind": "verify", "instruction": "Select minimal cost", "depends_on": ["step_1_cost_a", "step_2_cost_b"]},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_03_time_zone_flight",
        suite="gaia_l2",
        tier="level_2",
        prompt="A flight departs Tokyo (UTC+9) at 14:30 on Oct 1. Flight time is 9 hours 45 minutes. Arrival city is San Francisco (UTC-7). What is local arrival time in San Francisco?",
        context="Tokyo UTC+9, San Francisco UTC-7. Time difference = 16 hours behind Tokyo.",
        tools=[{"name": "calc"}],
        expected_answer="08:15",
        pdx_steps=[
            {"id": "step_1_utc", "kind": "tool", "tool": "calc", "instruction": "Calculate departure in UTC: 14.5 - 9 = 5.5 (05:30 UTC)", "depends_on": []},
            {"id": "step_2_arrival_utc", "kind": "tool", "tool": "calc", "instruction": "Add flight duration: 05:30 + 9h45m = 15:15 UTC", "depends_on": ["step_1_utc"]},
            {"id": "step_3_local", "kind": "tool", "tool": "calc", "instruction": "Convert to UTC-7: 15:15 - 7 hours = 08:15", "depends_on": ["step_2_arrival_utc"]},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_04_packet_loss_sla",
        suite="gaia_l2",
        tier="level_2",
        prompt="Examine 5 hourly network reports: [0.1%, 0.8%, 0.4%, 1.2%, 0.9%]. If threshold is >0.5%, how many hours breached, and is SLA violated (violated if breaches >= 3)?",
        context="SLA Contract clause 4.2: Max allowed breach hours is 2.",
        tools=[{"name": "calc"}],
        expected_answer="3 hours, breached",
        pdx_steps=[
            {"id": "step_1_count", "kind": "tool", "tool": "calc", "instruction": "Count elements > 0.5 in [0.1, 0.8, 0.4, 1.2, 0.9]", "depends_on": []},
            {"id": "step_2_sla", "kind": "verify", "instruction": "Check if count >= 3", "depends_on": ["step_1_count"]},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_05_energy_consumption_bill",
        suite="gaia_l2",
        tier="level_2",
        prompt="Calculate total electricity bill for 450 kWh with tiered rates: Tier 1 (first 100 kWh @ $0.12), Tier 2 (next 200 kWh @ $0.18), Tier 3 (remaining 150 kWh @ $0.25).",
        context="Tariff schedule 2026.",
        tools=[{"name": "calc"}],
        expected_answer="$85.50",
        pdx_steps=[
            {"id": "step_1_tier_calc", "kind": "tool", "tool": "calc", "instruction": "Compute 100*0.12 + 200*0.18 + 150*0.25", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_06_docker_layer_cache",
        suite="gaia_l2",
        tier="level_2",
        prompt="Identify the exact Dockerfile instruction that invalidated layer cache in build log.",
        context="Build log:\nStep 1/5: FROM python:3.12 (CACHED)\nStep 2/5: WORKDIR /app (CACHED)\nStep 3/5: COPY requirements.txt . (CACHED)\nStep 4/5: RUN pip install -r requirements.txt (CACHE MISS)\nStep 5/5: COPY . .",
        tools=[{"name": "grep"}],
        expected_answer="RUN pip install -r requirements.txt",
        pdx_steps=[
            {"id": "step_1_find_miss", "kind": "tool", "tool": "grep", "instruction": "Find line with CACHE MISS", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_07_geo_distance_shipping",
        suite="gaia_l2",
        tier="level_2",
        prompt="Given warehouse at X=0, Y=0 and recipient at X=120km, Y=160km, calculate Euclidean distance and assign shipping zone (<100km: Zone 1, 100-250km: Zone 2, >250km: Zone 3).",
        context="Logistics coordinate grid.",
        tools=[{"name": "calc"}],
        expected_answer="Zone 2",
        pdx_steps=[
            {"id": "step_1_distance", "kind": "tool", "tool": "calc", "instruction": "Compute sqrt(120**2 + 160**2) = 200km", "depends_on": []},
            {"id": "step_2_zone", "kind": "verify", "instruction": "Classify 200km into Zone", "depends_on": ["step_1_distance"]},
        ],
    ),
    BenchmarkTask(
        task_id="gaia_l2_08_semver_compatibility",
        suite="gaia_l2",
        tier="level_2",
        prompt="Given semver constraint '^2.4.0', which is the highest compatible release among ['2.3.9', '2.4.1', '2.4.8', '2.5.0', '3.0.0']?",
        context="Semver carets allow minor/patch bumps within major version 2.",
        tools=[{"name": "json_filter"}],
        expected_answer="2.5.0",
        pdx_steps=[
            {"id": "step_1_filter", "kind": "tool", "tool": "json_filter", "instruction": "Filter versions matching ^2.4.0 (>=2.4.0 <3.0.0)", "depends_on": []},
            {"id": "step_2_max", "kind": "verify", "instruction": "Pick max version: 2.5.0", "depends_on": ["step_1_filter"]},
        ],
    ),

    # 6. SWE Algorithmic Repair with Hidden Unit Tests (8 tasks)
    BenchmarkTask(
        task_id="swe_algo_01_binary_search_bounds",
        suite="swe_algo",
        tier="level_2",
        prompt="Fix the off-by-one error in binary_search(arr, target) when updating low pointer upon target > arr[mid]. What should low be set to?",
        context="Buggy code:\nif arr[mid] < target:\n    low = mid  # BUG: causes infinite loop on small arrays\nelse:\n    high = mid - 1",
        tools=[],
        expected_answer="low = mid + 1",
        pdx_steps=[
            {"id": "step_1_fix", "kind": "transform", "instruction": "Identify standard binary search lower bound update statement", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_02_lru_cache_eviction",
        suite="swe_algo",
        tier="level_2",
        prompt="In an OrderedDict-based LRU cache, which method call is required when a key is hit to mark it as most recently used?",
        context="class LRUCache:\n    def get(self, key):\n        if key not in self.cache: return -1\n        # Missing line to mark recent\n        return self.cache[key]",
        tools=[],
        expected_answer="move_to_end",
        pdx_steps=[
            {"id": "step_1_identify", "kind": "transform", "instruction": "Identify OrderedDict method to update item recency", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_03_cycle_detection_floyd",
        suite="swe_algo",
        tier="level_2",
        prompt="In Floyd's cycle detection algorithm, what condition must guard 'fast = fast.next.next' in the while loop condition to prevent AttributeError?",
        context="while fast and fast.next:\n    slow = slow.next\n    fast = fast.next.next",
        tools=[],
        expected_answer="fast and fast.next",
        pdx_steps=[
            {"id": "step_1_guard", "kind": "transform", "instruction": "State the pointer guard condition", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_04_merge_intervals",
        suite="swe_algo",
        tier="level_2",
        prompt="Before iterating to merge overlapping intervals [[x1, y1], [x2, y2]], what sorting statement is mandatory?",
        context="def merge_intervals(intervals):\n    # Missing sort statement!\n    merged = []\n    for intv in intervals: ...",
        tools=[],
        expected_answer="intervals.sort(key=lambda x: x[0])",
        pdx_steps=[
            {"id": "step_1_sort", "kind": "transform", "instruction": "Provide python interval sorting statement", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_05_json_cas_hash_deterministic",
        suite="swe_algo",
        tier="level_2",
        prompt="To ensure json.dumps() produces a deterministic SHA-256 digest regardless of key insertion order, which argument must be set to True?",
        context="import json, hashlib\ndef digest(d): return hashlib.sha256(json.dumps(d, ???).encode()).hexdigest()",
        tools=[],
        expected_answer="sort_keys=True",
        pdx_steps=[
            {"id": "step_1_flag", "kind": "transform", "instruction": "Identify deterministic json key ordering argument", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_06_tree_max_depth",
        suite="swe_algo",
        tier="level_2",
        prompt="What is the standard base case return for max_depth(root) of a binary tree when root is None?",
        context="def max_depth(root):\n    if not root:\n        return ???",
        tools=[],
        expected_answer="0",
        pdx_steps=[
            {"id": "step_1_base", "kind": "transform", "instruction": "Identify base case value for empty tree depth", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_07_rate_limiter_token_bucket",
        suite="swe_algo",
        tier="level_2",
        prompt="In a token bucket rate limiter, what python function prevents replenished tokens from exceeding max bucket capacity?",
        context="self.tokens = ???(self.capacity, self.tokens + added_tokens)",
        tools=[],
        expected_answer="min",
        pdx_steps=[
            {"id": "step_1_func", "kind": "transform", "instruction": "Identify boundary clamp function", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="swe_algo_08_topological_sort_kahn",
        suite="swe_algo",
        tier="level_2",
        prompt="In Kahn's algorithm for topological sort, when a node's in-degree reaches what integer value is it appended to the zero-in-degree queue?",
        context="for neighbor in graph[node]:\n    in_degree[neighbor] -= 1\n    if in_degree[neighbor] == ???:\n        queue.append(neighbor)",
        tools=[{"name": "run_python"}],
        expected_answer="0",
        pdx_steps=[
            {"id": "step_1_check", "kind": "transform", "instruction": "Identify queue push condition for Kahn's algorithm", "depends_on": []},
        ],
    ),

    # 7. GSM8K-Hard Multi-Step Arithmetic (6 tasks)
    BenchmarkTask(
        task_id="gsm_01_compound_depreciation",
        suite="gsm8k_hard",
        tier="level_2",
        prompt="A server cluster originally purchased for $12,000 depreciates by 15% each year. What is its exact residual book value at the end of 3 years?",
        context="Depreciation formula: Value = Principal * (1 - rate)^years = 12000 * (0.85)^3.",
        tools=[{"name": "calc"}],
        expected_answer="7369.5",
        pdx_steps=[
            {"id": "step_1_deprec", "kind": "tool", "tool": "calc", "instruction": "Compute 12000 * (0.85 ** 3)", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="gsm_02_compound_interest_quarterly",
        suite="gsm8k_hard",
        tier="level_2",
        prompt="A $5,000 investment earns 8% annual interest compounded quarterly for 2 years. Compute the final amount using A = P * (1 + r/n)^(n*t).",
        context="P=5000, r=0.08, n=4, t=2 -> A = 5000 * (1 + 0.02)^8.",
        tools=[{"name": "calc"}],
        expected_answer="5858.3",
        pdx_steps=[
            {"id": "step_1_interest", "kind": "tool", "tool": "calc", "instruction": "Compute round(5000 * (1.02 ** 8), 1)", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="gsm_03_worker_productivity_shifts",
        suite="gsm8k_hard",
        tier="level_2",
        prompt="12 workers produce 360 units in 5 days of 6-hour shifts. How many total units will 8 workers produce in 9 days of 8-hour shifts at the same productivity rate?",
        context="Rate = 360 / (12 * 5 * 6) = 1.0 unit / worker-hour. New = 8 * 9 * 8 * 1.0.",
        tools=[{"name": "calc"}],
        expected_answer="576",
        pdx_steps=[
            {"id": "step_1_rate", "kind": "tool", "tool": "calc", "instruction": "Compute 360 / (12 * 5 * 6)", "depends_on": []},
            {"id": "step_2_total", "kind": "tool", "tool": "calc", "instruction": "Compute 8 * 9 * 8 * 1.0", "depends_on": ["step_1_rate"]},
        ],
    ),
    BenchmarkTask(
        task_id="gsm_04_multitier_commission",
        suite="gsm8k_hard",
        tier="level_2",
        prompt="A sales rep earns 4% on first $50,000, 7% on the next $50,000, and 10% on anything exceeding $100,000. Calculate total commission for $145,000 total sales.",
        context="Tier 1: 50000*0.04; Tier 2: 50000*0.07; Tier 3: 45000*0.10.",
        tools=[{"name": "calc"}],
        expected_answer="10000",
        pdx_steps=[
            {"id": "step_1_tiers", "kind": "tool", "tool": "calc", "instruction": "Compute 50000*0.04 + 50000*0.07 + 45000*0.10", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="gsm_05_mixture_concentration",
        suite="gsm8k_hard",
        tier="level_2",
        prompt="40 liters of 20% acid solution is blended with 60 liters of 35% acid solution. What is the resulting acid concentration percentage?",
        context="Pure acid = 40*0.20 + 60*0.35 = 8 + 21 = 29 liters. Total volume = 100 liters.",
        tools=[{"name": "calc"}],
        expected_answer="29%",
        pdx_steps=[
            {"id": "step_1_blend", "kind": "tool", "tool": "calc", "instruction": "Compute ((40*0.20 + 60*0.35) / 100) * 100", "depends_on": []},
        ],
    ),
    BenchmarkTask(
        task_id="gsm_06_train_relative_speed",
        suite="gsm8k_hard",
        tier="level_2",
        prompt="Train A (250m long, speed 72 km/h = 20 m/s) and Train B (350m long, speed 108 km/h = 30 m/s) travel towards each other on parallel tracks. How many seconds elapse from initial engine encounter until tails completely clear?",
        context="Total clearance length = 250 + 350 = 600m. Relative speed = 20 + 30 = 50 m/s. Time = 600 / 50.",
        tools=[{"name": "calc"}],
        expected_answer="12",
        pdx_steps=[
            {"id": "step_1_time", "kind": "tool", "tool": "calc", "instruction": "Compute (250 + 350) / (20 + 30)", "depends_on": []},
        ],
    ),

    # 8. RULER Multi-Hop Long Context (6 tasks)
    BenchmarkTask(
        task_id="ruler_01_hop2_8k_crypto",
        suite="ruler_multihop",
        tier="level_2",
        prompt="Find the active vault session identifier, then find the specific decryption key assigned to that active session.",
        context=_noise(110) + "Active session established: session_id is SESSION_OMEGA_882.\n" + _noise(80) + "Session SESSION_OMEGA_882 decrypts with key KEY_CIPHER_99014.\n" + _noise(110),
        tools=[{"name": "grep"}],
        expected_answer="KEY_CIPHER_99014",
        pdx_steps=[
            {"id": "step_1_session", "kind": "tool", "tool": "grep", "instruction": "Search for active session_id in context", "depends_on": []},
            {"id": "step_2_key", "kind": "tool", "tool": "grep", "instruction": "Search for decryption key matching session_id", "depends_on": ["step_1_session"]},
        ],
    ),
    BenchmarkTask(
        task_id="ruler_02_hop2_8k_ip_port",
        suite="ruler_multihop",
        tier="level_2",
        prompt="Find which cluster node was elected as primary replica, then identify the internal IP:port address for that primary node.",
        context=_noise(120) + "Elected primary database replica is node-mel-srv7.\n" + _noise(70) + "Host node-mel-srv7 binds to internal socket 10.144.92.11:9042.\n" + _noise(110),
        tools=[{"name": "grep"}],
        expected_answer="10.144.92.11:9042",
        pdx_steps=[
            {"id": "step_1_replica", "kind": "tool", "tool": "grep", "instruction": "Search for elected primary node", "depends_on": []},
            {"id": "step_2_socket", "kind": "tool", "tool": "grep", "instruction": "Search for socket binding of elected primary node", "depends_on": ["step_1_replica"]},
        ],
    ),
    BenchmarkTask(
        task_id="ruler_03_hop2_8k_commit_author",
        suite="ruler_multihop",
        tier="level_2",
        prompt="Find the pull request number merged for release v3.2.0, then find the name of the author of that pull request.",
        context=_noise(100) + "Release v3.2.0 incorporates security PR #1492.\n" + _noise(90) + "PR #1492 author confirmed as Sarah Chen.\n" + _noise(110),
        tools=[{"name": "grep"}],
        expected_answer="Sarah Chen",
        pdx_steps=[
            {"id": "step_1_pr", "kind": "tool", "tool": "grep", "instruction": "Search for PR number in release v3.2.0", "depends_on": []},
            {"id": "step_2_author", "kind": "tool", "tool": "grep", "instruction": "Search for author of PR", "depends_on": ["step_1_pr"]},
        ],
    ),
    BenchmarkTask(
        task_id="ruler_04_hop2_12k_secret_hash",
        suite="ruler_multihop",
        tier="level_2",
        prompt="Find the reference hash for critical incident #804, then identify the root cause hardware failure tag linked to that hash.",
        context=_noise(160) + "Critical incident #804 archived under REF_HASH_EE492.\n" + _noise(140) + "REF_HASH_EE492 root cause identified as FLASH_SSD_SLOT3_FAILED.\n" + _noise(160),
        tools=[{"name": "grep"}],
        expected_answer="FLASH_SSD_SLOT3_FAILED",
        pdx_steps=[
            {"id": "step_1_ref", "kind": "tool", "tool": "grep", "instruction": "Search for incident #804 reference hash", "depends_on": []},
            {"id": "step_2_tag", "kind": "tool", "tool": "grep", "instruction": "Search for root cause failure tag linked to reference hash", "depends_on": ["step_1_ref"]},
        ],
    ),
    BenchmarkTask(
        task_id="ruler_05_hop3_8k_token_chain",
        suite="ruler_multihop",
        tier="level_2",
        prompt="Find the storage bucket for Project Apollo, find the KMS key alias for that bucket, and output the final KMS Key ARN.",
        context=_noise(110) + "Project Apollo storage bucket is config-apollo-prd.\n" + _noise(60) + "Bucket config-apollo-prd encrypted via alias/apollo-seal-kms.\n" + _noise(70) + "alias/apollo-seal-kms resolves to ARN arn:aws:kms:us-east-1:123456789:key/9918a.\n" + _noise(100),
        tools=[{"name": "grep"}],
        expected_answer="arn:aws:kms:us-east-1:123456789:key/9918a",
        pdx_steps=[
            {"id": "step_1_bucket", "kind": "tool", "tool": "grep", "instruction": "Search bucket for Project Apollo", "depends_on": []},
            {"id": "step_2_alias", "kind": "tool", "tool": "grep", "instruction": "Search KMS alias for bucket", "depends_on": ["step_1_bucket"]},
            {"id": "step_3_arn", "kind": "tool", "tool": "grep", "instruction": "Search KMS ARN for alias", "depends_on": ["step_2_alias"]},
        ],
    ),
    BenchmarkTask(
        task_id="ruler_06_hop2_12k_agent_id",
        suite="ruler_multihop",
        tier="level_2",
        prompt="Find which worker node was assigned task TASK_DISPATCH_774, then locate the completion receipt digest recorded by that worker.",
        context=_noise(150) + "TASK_DISPATCH_774 assigned to worker Worker_Bravo_9.\n" + _noise(130) + "Worker_Bravo_9 job completion receipt digest: sha256_e4c88219b.\n" + _noise(160),
        tools=[{"name": "grep"}],
        expected_answer="sha256_e4c88219b",
        pdx_steps=[
            {"id": "step_1_worker", "kind": "tool", "tool": "grep", "instruction": "Search worker assigned to TASK_DISPATCH_774", "depends_on": []},
            {"id": "step_2_digest", "kind": "tool", "tool": "grep", "instruction": "Search completion receipt digest for worker", "depends_on": ["step_1_worker"]},
        ],
    ),
]


def load_benchmark_suite(tier: Optional[str] = None, suite_name: Optional[str] = None) -> List[BenchmarkTask]:
    tasks = BENCHMARK_TASKS
    if tier and tier != "all":
        tasks = [t for t in tasks if t.tier == tier]
    if suite_name and suite_name != "all":
        tasks = [t for t in tasks if t.suite == suite_name]
    return tasks


if __name__ == "__main__":
    tasks = load_benchmark_suite()
    l1 = [t for t in tasks if t.tier == "level_1"]
    l2 = [t for t in tasks if t.tier == "level_2"]
    print(f"Loaded {len(tasks)} benchmark tasks across 2 tiers:")
    print(f"  - Level 1 Baseline: {len(l1)} tasks (Suites: {set(t.suite for t in l1)})")
    print(f"  - Level 2 Advanced: {len(l2)} tasks (Suites: {set(t.suite for t in l2)})")


# Filter benchmark tasks strictly to RULER suites (21 tasks: 15 ruler_l1 + 6 ruler_multihop)
ALL_TASKS = load_benchmark_suite()
BENCHMARK_TASKS = [t for t in ALL_TASKS if "ruler" in t.suite]
print(f"Loaded {len(BENCHMARK_TASKS)} RULER benchmark tasks for Experiment 2.")
assert len(BENCHMARK_TASKS) == 21, f"Expected exactly 21 RULER tasks, found {len(BENCHMARK_TASKS)}"
