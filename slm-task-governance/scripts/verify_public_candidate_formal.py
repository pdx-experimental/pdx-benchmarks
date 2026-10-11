"""Strict Verification and Reproducibility Audit of Public Formal Candidate Release.

Enforces:
1. Strict Filesystem Lockdown & Index Binding:
   - Root candidate directory contains ONLY candidate_manifest.json and the 28 authorized job directories.
   - Master manifest (candidate_manifest.json) self-digest verified under RFC 8785.
   - Every job's public_manifest_sha256 in master manifest strictly matches on-disk public_manifest.json SHA-256.
   - Every job directory strictly contains ONLY public_manifest.json and files listed in published_files (zero extra/unlisted files).
   - If sqlite_databases_count > 0, workflows/ contains only .sqlite3 files matching count; if 0, workflows/ must not exist.
   - Strict dual-hash bridges: original_manifest_sha256, original_ledger_sha256, candidate_ledger_sha256, sqlite_bundle_sha256.
2. Full Re-scoring of All 1,444 Rows:
   - Evaluates each row independently using score_answer() with zero discrepancies against recorded success.
3. Rigorous Paired Statistical Auditing:
   - Phase 0: 5 models, exact McNemar binomial tests on discordant pairs + Holm-Bonferroni (m=5).
   - Phase 3: 6 models, exact McNemar tests on post-hoc main-effect family (m=6, verifying Qwen 7B p_Holm=0.046875)
     and exploratory family (m=18, verifying Qwen 7B p_Holm=0.140625).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from scipy import stats
import sys

# Support running from public repository workspace root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import rfc8785
from src.scoring import score_answer


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_manifest_self_digest(manifest: dict) -> str:
    proj = {k: v for k, v in manifest.items() if k != "manifest_self_digest"}
    return hashlib.sha256(rfc8785.dumps(proj)).hexdigest()


def compute_canonical_sqlite_bundle_digest(workflows_dir: Path | None) -> str | None:
    if not workflows_dir or not workflows_dir.exists():
        return hashlib.sha256(rfc8785.dumps([])).hexdigest()
    files = [f for f in workflows_dir.rglob("*.sqlite3") if f.is_file() and not f.name.startswith(".")]
    if not files:
        return hashlib.sha256(rfc8785.dumps([])).hexdigest()
    sorted_files = sorted(files, key=lambda f: f.relative_to(workflows_dir).as_posix().encode("utf-8"))
    manifest_list = []
    for f in sorted_files:
        rel_posix = f.relative_to(workflows_dir).as_posix()
        content = f.read_bytes()
        manifest_list.append({
            "path": rel_posix,
            "sha256": hashlib.sha256(content).hexdigest(),
            "size_bytes": len(content),
        })
    return hashlib.sha256(rfc8785.dumps(manifest_list)).hexdigest()


def mcnemar_exact(b: int, c: int) -> float:
    n_discordant = b + c
    if n_discordant == 0:
        return 1.0
    res = stats.binomtest(b, n_discordant, 0.5, alternative="two-sided")
    return float(res.pvalue)


def holm_bonferroni(p_values: list[float]) -> list[float]:
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        adj_p = min(1.0, p * (m - rank))
        running_max = max(running_max, adj_p)
        adjusted[orig_idx] = running_max
    return adjusted


def verify_candidate_directory(candidate_dir: Path):
    print("=" * 80)
    print("PDX BENCHMARK: STRICT PUBLIC CANDIDATE VERIFICATION AUDIT")
    print(f"Target Directory: {candidate_dir}")
    print("=" * 80)

    # 1. Master Candidate Manifest & Root Lockdown
    master_p = candidate_dir / "candidate_manifest.json"
    assert master_p.exists(), f"Missing master candidate_manifest.json at {master_p}"
    master_data = json.loads(master_p.read_text(encoding="utf-8"))
    expected_master_self = compute_manifest_self_digest(master_data)
    assert master_data.get("manifest_self_digest") == expected_master_self, (
        f"Master manifest self_digest mismatch: {master_data.get('manifest_self_digest')} != {expected_master_self}"
    )
    print(f"[PASS] Master candidate_manifest.json self-digest verified (RFC 8785).")

    jobs = master_data["jobs"]
    assert len(jobs) == 28, f"Expected 28 jobs in candidate manifest, found {len(jobs)}"
    assert master_data["total_contracted_rows"] == 1444, f"Expected 1,444 total rows, found {master_data['total_contracted_rows']}"

    # Strict Root Directory Lockdown: reject any unexpected files or directories
    expected_job_keys = {j["job_key"] for j in jobs}
    for item in candidate_dir.iterdir():
        if item.is_file():
            assert item.name == "candidate_manifest.json", f"Strict Lockdown: unexpected file in candidate root: {item.name}"
        elif item.is_dir():
            assert item.name in expected_job_keys, f"Strict Lockdown: unexpected directory in candidate root: {item.name}"
        else:
            raise AssertionError(f"Strict Lockdown: unknown filesystem item: {item}")
    print(f"[PASS] Candidate root lockdown verified: zero extraneous files or unlisted directories.")

    total_rows_scored = 0
    all_job_ledgers = {}

    print("\n--- [1] Auditing Manifests, Index Associations, Strict File Sets & Re-scoring 1,444 Rows ---")
    for idx, job in enumerate(jobs, 1):
        key = job["job_key"]
        job_dir = candidate_dir / key
        assert job_dir.exists(), f"Job directory missing: {job_dir}"

        # A. Public Manifest Integrity & Top-Level Index Check
        pub_man_p = job_dir / "public_manifest.json"
        assert pub_man_p.exists(), f"Missing public_manifest.json in {key}"
        pub_man = json.loads(pub_man_p.read_text(encoding="utf-8"))

        # Check that top-level job entry public_manifest_sha256 strictly matches actual file SHA-256
        actual_pub_man_sha = sha256_file(pub_man_p)
        assert actual_pub_man_sha == job["public_manifest_sha256"], (
            f"[{key}] Master manifest public_manifest_sha256 mismatch: {actual_pub_man_sha} != {job['public_manifest_sha256']}"
        )

        # Self-digest
        expected_pub_self = compute_manifest_self_digest(pub_man)
        assert pub_man.get("manifest_self_digest") == expected_pub_self, (
            f"[{key}] public_manifest.json self_digest mismatch: {pub_man.get('manifest_self_digest')} != {expected_pub_self}"
        )

        # Dual-hash bridges alignment between master manifest and public manifest
        assert pub_man["ledger_sha256"] == job["candidate_ledger_sha256"], f"[{key}] Candidate ledger SHA mismatch"
        assert pub_man["sqlite_bundle_sha256"] == job["sqlite_bundle_sha256"], f"[{key}] SQLite bundle SHA mismatch"
        assert pub_man["provenance_bridge"]["original_manifest_sha256"] == job["original_manifest_sha256"], f"[{key}] Orig manifest SHA mismatch"
        assert pub_man["provenance_bridge"]["original_ledger_sha256"] == job["original_ledger_sha256"], f"[{key}] Orig ledger SHA mismatch"
        assert pub_man["sqlite_databases_count"] == job["sqlite_databases_count"], f"[{key}] SQLite DB count mismatch"

        # B. Strict Job Directory Lockdown: Reject any unlisted files or directories
        pub_files = pub_man.get("published_files", {})
        allowed_files = set(pub_files.keys()) | {"public_manifest.json"}
        sqlite_count = pub_man["sqlite_databases_count"]
        wf_dir = job_dir / "workflows"

        for entry in job_dir.iterdir():
            if entry.is_file():
                assert entry.name in allowed_files, (
                    f"[{key}] Strict Lockdown Violation: unlisted extra file found in job directory: {entry.name}"
                )
            elif entry.is_dir():
                assert entry.name == "workflows" and sqlite_count > 0, (
                    f"[{key}] Strict Lockdown Violation: unexpected directory in job directory: {entry.name}"
                )
            else:
                raise AssertionError(f"[{key}] Unexpected filesystem item: {entry}")

        if sqlite_count == 0:
            assert not wf_dir.exists(), f"[{key}] workflows directory should not exist when sqlite_count == 0"
        else:
            assert wf_dir.exists(), f"[{key}] workflows directory missing when sqlite_count == {sqlite_count}"
            wf_entries = list(wf_dir.iterdir())
            assert len(wf_entries) == sqlite_count, (
                f"[{key}] workflows/ count mismatch: {len(wf_entries)} != {sqlite_count}"
            )
            for db_entry in wf_entries:
                assert db_entry.is_file() and db_entry.name.endswith(".sqlite3") and not db_entry.name.startswith("."), (
                    f"[{key}] Strict Lockdown Violation: unexpected file in workflows/: {db_entry.name}"
                )

        # C. Published files cryptographic digests
        for fname, fmeta in pub_files.items():
            fpath = job_dir / fname
            assert fpath.exists(), f"[{key}] Published file missing: {fname}"
            actual_sha = sha256_file(fpath)
            actual_size = fpath.stat().st_size
            assert actual_sha == fmeta["sha256"], f"[{key}] SHA mismatch for {fname}: {actual_sha} != {fmeta['sha256']}"
            assert actual_size == fmeta["size_bytes"], f"[{key}] Size mismatch for {fname}: {actual_size} != {fmeta['size_bytes']}"

        # D. Original run manifest bridge
        orig_man_p = job_dir / "original_run_manifest.json"
        assert orig_man_p.exists(), f"[{key}] Missing original_run_manifest.json"
        assert sha256_file(orig_man_p) == pub_man["provenance_bridge"]["original_manifest_sha256"]

        # E. SQLite bundle canonical hash
        expected_sqlite_bundle_sha = compute_canonical_sqlite_bundle_digest(wf_dir if sqlite_count > 0 else None)
        assert pub_man["sqlite_bundle_sha256"] == expected_sqlite_bundle_sha, (
            f"[{key}] sqlite_bundle_sha256 mismatch: {pub_man['sqlite_bundle_sha256']} != {expected_sqlite_bundle_sha}"
        )

        # F. Ledger file hash
        ledger_p = job_dir / "benchmark_ledger.jsonl"
        assert ledger_p.exists(), f"[{key}] Missing benchmark_ledger.jsonl"
        assert sha256_file(ledger_p) == pub_man["ledger_sha256"]

        # G. Re-score all rows using score_answer
        rows = [json.loads(line) for line in ledger_p.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(rows) == pub_man["total_tasks"], f"[{key}] Row count mismatch: {len(rows)} != {pub_man['total_tasks']}"

        calc_pass_count = 0
        for r_idx, r in enumerate(rows):
            pred = r.get("final_answer")
            expected = r.get("expected_answer")
            suite = r.get("suite", r.get("task_suite", ""))
            scored_success, reason = score_answer(pred, expected, suite=suite)
            recorded_success = r.get("success") is True
            assert reason == r.get("score_reason"), f"[{key}] Score reason mismatch for {r.get("task_id")}"
            assert scored_success == recorded_success, (
                f"[{key} row {r_idx} task {r.get('task_id')}] Re-score mismatch! "
                f"Computed={scored_success} ({reason}), Recorded={recorded_success}. "
                f"Pred='{pred}', Expected='{expected}'"
            )
            if scored_success:
                calc_pass_count += 1

        assert calc_pass_count == pub_man["pass_count"], (
            f"[{key}] Pass count mismatch: computed {calc_pass_count} != recorded {pub_man['pass_count']}"
        )

        all_job_ledgers[key] = rows
        total_rows_scored += len(rows)
        print(f"  [{idx:02d}/28] [PASS] {key:<30}: {calc_pass_count:2d}/{len(rows):3d} rows 100% verified & rescored.")

    assert total_rows_scored == 1444, f"Total rescored rows {total_rows_scored} != 1444"
    print(f"\n[PASS] All 28 jobs and 1,444 rows independently rescored with ZERO discrepancies.")

    # 2. Verify Phase 0 Paired Statistical Results
    print("\n--- [2] Auditing Phase 0 Paired Contingency Tables and McNemar Tests (N=112) ---")
    p0_models = [
        {"key": "qwen25_15b", "name": "Qwen 2.5 Coder 1.5B", "expected_contingency": (15, 5, 23, 69), "p_raw_approx": 0.00091},
        {"key": "qwen25_3b", "name": "Qwen 2.5 Coder 3B", "expected_contingency": (19, 15, 22, 56), "p_raw_approx": 0.3240},
        {"key": "llama32_1b", "name": "Llama 3.2 1B", "expected_contingency": (4, 15, 2, 91), "p_raw_approx": 0.00235},
        {"key": "llama32_3b", "name": "Llama 3.2 3B", "expected_contingency": (14, 15, 12, 71), "p_raw_approx": 0.7011},
        {"key": "gemma3_1b", "name": "Gemma 3 1B", "expected_contingency": (7, 10, 11, 84), "p_raw_approx": 1.0000},
    ]

    p0_pvals = []
    for m in p0_models:
        r_rows = all_job_ledgers[f"phase0_{m['key']}_react"]
        i_rows = all_job_ledgers[f"phase0_{m['key']}_isolated"]
        r_by_t = {row["task_id"]: row.get("success") is True for row in r_rows}
        i_by_t = {row["task_id"]: row.get("success") is True for row in i_rows}

        a = sum(1 for t, r_s in r_by_t.items() if r_s and i_by_t[t])
        b = sum(1 for t, r_s in r_by_t.items() if r_s and not i_by_t[t])
        c = sum(1 for t, r_s in r_by_t.items() if not r_s and i_by_t[t])
        d = sum(1 for t, r_s in r_by_t.items() if not r_s and not i_by_t[t])

        assert (a, b, c, d) == m["expected_contingency"], (
            f"Phase 0 contingency mismatch for {m['key']}: actual {(a, b, c, d)} != expected {m['expected_contingency']}"
        )
        p_val = mcnemar_exact(b, c)
        assert math.isclose(p_val, m["p_raw_approx"], rel_tol=1e-2, abs_tol=1e-4), (
            f"Phase 0 p-value mismatch for {m['key']}: {p_val} != {m['p_raw_approx']}"
        )
        p0_pvals.append(p_val)
        print(f"  [PASS] {m['name']:<22}: Both={a:2d}, ReAct-only={b:2d}, Iso-only={c:2d}, Neither={d:2d} | p_raw={p_val:.5f}")

    p0_holm = holm_bonferroni(p0_pvals)
    assert p0_holm[0] < 0.05, f"Qwen 1.5B Holm p-value should be < 0.05, got {p0_holm[0]}"
    assert p0_holm[2] < 0.05, f"Llama 1B Holm p-value should be < 0.05, got {p0_holm[2]}"
    print(f"  [PASS] Phase 0 Holm adjustments verified: Qwen 1.5B p_Holm={p0_holm[0]:.4f}, Llama 1B p_Holm={p0_holm[2]:.4f}")

    # 3. Verify Phase 3 Paired Statistical Results
    print("\n--- [3] Auditing Phase 3 Paired Comparisons, Dual-Scope Holm Corrections ---")
    p3_models = [
        {"key": "qwen7", "name": "Qwen 2.5 Coder 7B", "c0_c2sf": (2, 0, 8, 8, 0.0078125)},
        {"key": "llama8", "name": "Llama 3.1 8B", "c0_c2sf": (0, 0, 6, 12, 0.03125)},
        {"key": "apertus", "name": "Apertus 8B", "c0_c2sf": (2, 0, 5, 11, 0.06250)},
        {"key": "mistral", "name": "Mistral 7B", "c0_c2sf": (0, 0, 1, 17, 1.00000)},
        {"key": "qwen15", "name": "Qwen 2.5 Coder 1.5B", "c0_c2sf": (0, 0, 1, 17, 1.00000)},
        {"key": "llama3", "name": "Llama 3.2 3B", "c0_c2sf": (0, 0, 0, 18, 1.00000)},
    ]

    main_effect_p = []
    all_18_comparisons = []

    for m in p3_models:
        c0_rows = all_job_ledgers[f"phase3_{m['key']}_c0"]
        c2s_rows = all_job_ledgers[f"phase3_{m['key']}_c2s"]
        c2sf_rows = all_job_ledgers[f"phase3_{m['key']}_c2sf"]

        c0_by_t = {row["task_id"]: row.get("success") is True for row in c0_rows}
        c2s_by_t = {row["task_id"]: row.get("success") is True for row in c2s_rows}
        c2sf_by_t = {row["task_id"]: row.get("success") is True for row in c2sf_rows}

        def get_contingency(d1, d2):
            a = sum(1 for t, s1 in d1.items() if s1 and d2[t])
            b = sum(1 for t, s1 in d1.items() if s1 and not d2[t])
            c = sum(1 for t, s1 in d1.items() if not s1 and d2[t])
            d = sum(1 for t, s1 in d1.items() if not s1 and not d2[t])
            return a, b, c, d, mcnemar_exact(b, c)

        a, b, c, d, p_val = get_contingency(c0_by_t, c2sf_by_t)
        exp_a, exp_b, exp_c, exp_d, exp_p = m["c0_c2sf"]
        assert (a, b, c, d) == (exp_a, exp_b, exp_c, exp_d), f"Contingency mismatch in {m['key']} C0->C2sf"
        assert math.isclose(p_val, exp_p, rel_tol=1e-5), f"P-value mismatch in {m['key']} C0->C2sf: {p_val} != {exp_p}"
        main_effect_p.append(p_val)
        all_18_comparisons.append((f"{m['name']} C0->C2sf", p_val))

        # C0 -> C2s
        _, _, _, _, p_c0_c2s = get_contingency(c0_by_t, c2s_by_t)
        all_18_comparisons.append((f"{m['name']} C0->C2s", p_c0_c2s))

        # C2s -> C2sf
        _, _, _, _, p_c2s_c2sf = get_contingency(c2s_by_t, c2sf_by_t)
        all_18_comparisons.append((f"{m['name']} C2s->C2sf", p_c2s_c2sf))

        print(f"  [PASS] {m['name']:<22} C0->C2sf: a={a}, b={b}, c={c}, d={d} | p_raw={p_val:.5f}")

    # Dual-scope Holm correction verification
    # Scope 1: Post-hoc selected main-effect family (m=6)
    holm_m6 = holm_bonferroni(main_effect_p)
    qwen7_m6 = holm_m6[0]
    assert math.isclose(qwen7_m6, 0.046875, rel_tol=1e-5), f"Qwen 7B m=6 Holm p mismatch: {qwen7_m6} != 0.046875"
    print(f"\n  [PASS] Post-Hoc Main-Effect Family (m=6): Qwen 7B p_Holm = {qwen7_m6:.5f} (< 0.05)")

    # Scope 2: Full exploratory family (m=18)
    p_all_18 = [p for _, p in all_18_comparisons]
    holm_m18 = holm_bonferroni(p_all_18)
    qwen7_m18 = holm_m18[0]
    assert math.isclose(qwen7_m18, 0.140625, rel_tol=1e-5), f"Qwen 7B m=18 Holm p mismatch: {qwen7_m18} != 0.140625"
    print(f"  [PASS] Full Exploratory Family (m=18): Qwen 7B p_Holm = {qwen7_m18:.5f} (>= 0.05)")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE: ALL 28 JOBS, 1,444 ROWS, AND STATISTICAL TESTS PASSED.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Strict Verification of Formal Candidate Release.")
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        default=ROOT / "data" / "results_formal_candidate" if (ROOT / "data" / "results_formal_candidate").exists() else Path(r"D:\ProDocuX\pdx-experimental\pdx-benchmarks\slm-task-governance\data\results_formal_candidate"),
        help="Path to candidate data directory",
    )
    args = parser.parse_args()
    verify_candidate_directory(args.candidate_dir)


if __name__ == "__main__":
    main()
