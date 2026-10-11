"""Builds pdx_phase0_t4x2_benchmark_fair_v1.ipynb for the Fair SLM Comparison.

Strictly follows FAIR_COMPARISON_PLAN.md:
- Title: 'PDX Synthetic SLM Dispatch Fair Comparison'
- Exactly two conditions: goldplan_react vs goldplan_isolated
- Same gold plan, same honest tools, same JSON schema, same answer scorer.
- No gold fallbacks, no context cropping, no auto-execution of instructions.
- Gemma 3 4B guarded smoke test (skips if empty generation).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def create_code_cell(source_code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source_code.strip().split("\n")],
    }


def create_markdown_cell(markdown_text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in markdown_text.strip().split("\n")],
    }


def build_notebook() -> dict:
    cells = []

    # Markdown 1: Title & Purpose
    cells.append(
        create_markdown_cell(
            """# PDX Synthetic SLM Dispatch Fair Comparison (Dual Tesla T4)
## Evaluating Isolated Step Dispatch vs Accumulating ReAct with Gold Plan Held Constant

This benchmark executes a strictly controlled empirical test of:
- **Condition A: `goldplan_react`** (Single accumulating multi-turn conversation)
- **Condition B: `goldplan_isolated`** (Fresh messages per step, only parent receipts)

### Strict Experimental Controls:
1. **Same Gold Plan**: Both conditions receive identical step breakdown and instructions.
2. **Same Full Context**: Zero head/tail cropping (no 150-char truncation).
3. **Same Honest Tools**: No gold fallbacks; tools operate strictly on model-provided arguments.
4. **Same JSON Output Schema**: Strict JSON output required from both conditions.
5. **Same Generation Parameters**: `temperature=0.0`, `do_sample=False`, `max_new_tokens=256` (repetition penalty removed).
6. **Same Scorer**: Identical terminal answer evaluation (`score_answer`).
7. **Synthetic Fixtures**: All tasks are synthetic benchmark fixtures (not real GAIA/RULER/SWE).
"""
        )
    )

    # Code 1: Hardware Preflight Check
    cells.append(
        create_code_cell(
            """import subprocess
import os
import sys

print("=== 1. Hardware Preflight Check ===")
gpu_query = subprocess.run(
    ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
    text=True, capture_output=True, check=True
).stdout.strip().splitlines()

print('Detected GPUs:', gpu_query)
assert len(gpu_query) == 2, f'Dual T4 benchmark requires two GPUs, found {gpu_query}'
assert all('T4' in item.upper() for item in gpu_query), f'Dual T4 required; found: {gpu_query}'
print("Hardware check passed: Dual Tesla T4 present.")
"""
        )
    )

    # Code 2: Package Setup
    cells.append(
        create_code_cell(
            """print("=== 2. Environment Setup ===")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "transformers>=4.50.0", "accelerate", "pdx-artifact-engine==0.3.0a9"], check=True)
import torch
import transformers
import pdx_artifact_engine

print("PyTorch Version:", torch.__version__, "| CUDA:", torch.cuda.is_available(), "| GPU Count:", torch.cuda.device_count())
print("Transformers Version:", transformers.__version__)
print("PDX Artifact Engine Installed (engine_invocations will be recorded in manifest).")
"""
        )
    )

    # Code 3: Honest Tools Environment
    tools_code = (ROOT / "src" / "tools.py").read_text(encoding="utf-8")
    cells.append(
        create_code_cell(
            f"""# === 3. Honest Benchmark Tools Environment ===\n{tools_code}"""
        )
    )

    # Code 4: Fair Answer Scoring Module
    scoring_code = (ROOT / "src" / "scoring.py").read_text(encoding="utf-8")
    cells.append(
        create_code_cell(
            f"""# === 4. Fair Answer Scoring Module ===\n{scoring_code}"""
        )
    )

    # Code 5: Standardized Tasks Fixtures
    loader_code = (ROOT / "src" / "benchmark_loader.py").read_text(encoding="utf-8")
    cells.append(
        create_code_cell(
            f"""# === 5. Standardized Benchmark Tasks Fixtures ===\n{loader_code}"""
        )
    )

    # Code 6: Condition Runners (GoldPlanReActRunner & GoldPlanIsolatedRunner)
    react_code = (ROOT / "src" / "runners" / "goldplan_react.py").read_text(encoding="utf-8")
    iso_code = (ROOT / "src" / "runners" / "goldplan_isolated.py").read_text(encoding="utf-8")
    # Avoid duplicate parse_model_json definition by stripping import
    iso_code_clean = iso_code.replace("from src.runners.goldplan_react import parse_model_json", "# parse_model_json already defined above")
    cells.append(
        create_code_cell(
            f"""# === 6. Condition Runners ===\n# Condition A: GoldPlanReActRunner\n{react_code}\n\n# Condition B: GoldPlanIsolatedRunner\n{iso_code_clean}"""
        )
    )

    # Code 7: Model Loading, Smoke Testing, and Execution Loop
    exec_loop_code = r'''# === 7. Candidate Models & Execution Loop ===
import time
import os
import gc

CANDIDATE_MODELS = [
    {"name": "qwen2.5_coder_1.5b", "model_id": "Qwen/Qwen2.5-Coder-1.5B-Instruct"},
    {"name": "qwen2.5_coder_3b", "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct"},
    {"name": "llama3.2_1b", "model_id": "unsloth/Llama-3.2-1B-Instruct"},
    {"name": "llama3.2_3b", "model_id": "unsloth/Llama-3.2-3B-Instruct"},
    {"name": "gemma3_1b", "model_id": "unsloth/gemma-3-1b-it"},
    {"name": "gemma3_4b", "model_id": "unsloth/gemma-3-4b-it", "smoke_test_required": True}
]

ledger_path = "/kaggle/working/benchmark_ledger.jsonl"
os.makedirs("/kaggle/working", exist_ok=True)
if not os.path.exists(ledger_path):
    with open(ledger_path, "w", encoding="utf-8") as f:
        pass

all_eval_results = []
model_statuses = {}

for cand in CANDIDATE_MODELS:
    model_name = cand["name"]
    model_id = cand["model_id"]
    smoke_required = cand.get("smoke_test_required", False)

    print(f"\n=================== Loading Model: {model_name} ({model_id}) ===================")
    gc.collect()
    torch.cuda.empty_cache()

    model = None
    tokenizer = None
    processor = None
    is_processor = False

    try:
        if "gemma-3-4b" in model_id.lower():
            try:
                from transformers import AutoProcessor, Gemma3ForConditionalGeneration
                processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                model = Gemma3ForConditionalGeneration.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
                is_processor = True
                print(f"Loaded {model_name} via Gemma3ForConditionalGeneration.")
            except Exception as ex_gem:
                print(f"Gemma 3 processor load fallback ({ex_gem}); using AutoModelForCausalLM...")
                from transformers import AutoTokenizer, AutoModelForCausalLM
                tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
                is_processor = False
        else:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            is_processor = False

        model.eval()
        print(f"Model {model_name} successfully loaded.")
    except Exception as e:
        print(f"CRITICAL: Failed to load {model_name}: {e}")
        model_statuses[model_name] = f"load_failed: {e}"
        continue

    def generate_chat_fn(messages, max_tokens=256) -> str:
        if model is None:
            return ""
        try:
            if is_processor:
                proc_messages = []
                for m in messages:
                    c = m["content"]
                    if isinstance(c, str):
                        proc_messages.append({"role": m["role"], "content": [{"type": "text", "text": c}]})
                    else:
                        proc_messages.append(m)
                inputs = processor.apply_chat_template(
                    proc_messages,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_dict=True,
                    return_tensors="pt"
                ).to(model.device)
                with torch.no_grad():
                    output_tokens = model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=False
                    )
                input_len = inputs["input_ids"].shape[1]
                if output_tokens.shape[1] > input_len:
                    gen_ids = output_tokens[0, input_len:]
                else:
                    gen_ids = output_tokens[0]
                return processor.decode(gen_ids, skip_special_tokens=True).strip()
            else:
                prompt_str = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                inputs = tokenizer(prompt_str, return_tensors="pt", truncation=False).to(model.device)
                with torch.no_grad():
                    output_tokens = model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=False,
                        pad_token_id=tokenizer.eos_token_id
                    )
                input_len = inputs.input_ids.shape[1]
                if output_tokens.shape[1] > input_len:
                    gen_ids = output_tokens[0, input_len:]
                else:
                    gen_ids = output_tokens[0]
                return tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            return ""
        except Exception as ex:
            return ""

    # Smoke test for Gemma 3 4B (Section 6 of plan)
    if smoke_required:
        print("Running decoder smoke test for Gemma 3 4B...")
        smoke_messages = [{"role": "user", "content": 'Reply with JSON {"action":"final_answer","answer":"ok"}'}]
        smoke_resp = generate_chat_fn(smoke_messages, max_tokens=64)
        print(f"Smoke test response: '{smoke_resp}'")
        if not smoke_resp or not smoke_resp.strip():
            print("WARNING: Gemma 3 4B smoke test emitted empty generation! Marking invalid_empty_generation and skipping.")
            model_statuses[model_name] = "invalid_empty_generation"
            del model
            if tokenizer: del tokenizer
            if processor: del processor
            gc.collect()
            torch.cuda.empty_cache()
            continue

    model_statuses[model_name] = "evaluated"

    # Instantiate the two fair runners
    react_runner = GoldPlanReActRunner(generate_chat_fn)
    isolated_runner = GoldPlanIsolatedRunner(generate_chat_fn)

    runners_map = {
        "goldplan_react": react_runner,
        "goldplan_isolated": isolated_runner
    }

    # Evaluate both modes across all tasks
    for mode_name in ["goldplan_react", "goldplan_isolated"]:
        runner = runners_map[mode_name]
        print(f"\n--- Running {model_name} in {mode_name} mode ({len(BENCHMARK_TASKS)} tasks) ---")
        passed_count = 0
        total_tasks = len(BENCHMARK_TASKS)

        for idx, task in enumerate(BENCHMARK_TASKS):
            res = runner.run_task(task, execute_benchmark_tool, model_name=model_name)
            # Fair scoring of terminal answer
            is_success, score_reason = score_answer(res["final_answer"], task.expected_answer, suite=task.suite)
            res["success"] = is_success
            res["score_reason"] = score_reason

            if is_success:
                passed_count += 1

            all_eval_results.append(res)

            # Write ledger entry immediately
            with open(ledger_path, "a", encoding="utf-8") as f_ledger:
                f_ledger.write(json.dumps(res, ensure_ascii=False) + "\n")

            if (idx + 1) % 10 == 0 or (idx + 1) == total_tasks:
                print(f"  [{idx+1}/{total_tasks}] Passed: {passed_count}/{idx+1} ({passed_count/(idx+1)*100:.1f}%) | Last ans: '{res['final_answer'][:40]}'")

    # Free model memory
    del model
    if tokenizer: del tokenizer
    if processor: del processor
    gc.collect()
    torch.cuda.empty_cache()
'''
    cells.append(create_code_cell(exec_loop_code))

    # Code 8: Summary Reporting & Artifact Manifest
    summary_code = r'''# === 8. Summary Reporting & Artifact Manifest ===
import json
import math
import hashlib
from collections import defaultdict
from datetime import datetime, timezone

def wilson_score_interval(k: int, n: int, confidence: float = 0.95):
    if n == 0:
        return 0.0, 0.0
    z = 1.95996  # 95% confidence
    p = k / n
    denominator = 1 + z**2 / n
    centre_adjusted_probability = p + z**2 / (2 * n)
    adjusted_std_error = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    lower = max(0.0, (centre_adjusted_probability - adjusted_std_error) / denominator)
    upper = min(1.0, (centre_adjusted_probability + adjusted_std_error) / denominator)
    return round(lower * 100, 1), round(upper * 100, 1)

print("\n=================== FAIR COMPARISON BENCHMARK REPORT ===================")
# Group results by model, mode
overall = defaultdict(lambda: {"total": 0, "passed": 0, "empty_gen": 0, "invalid_out": 0, "elapsed": 0.0})
tier_stats = defaultdict(lambda: {"total": 0, "passed": 0})
suite_stats = defaultdict(lambda: {"total": 0, "passed": 0})

for r in all_eval_results:
    m = r["model"]
    mode = r["mode"]
    k_ov = (m, mode)
    overall[k_ov]["total"] += 1
    if r["success"]:
        overall[k_ov]["passed"] += 1
    overall[k_ov]["empty_gen"] += r.get("empty_generations", 0)
    overall[k_ov]["invalid_out"] += r.get("invalid_outputs", 0)
    overall[k_ov]["elapsed"] += r.get("elapsed_s", 0.0)

    tier = r.get("tier", "unspecified")
    tier_stats[(m, mode, tier)]["total"] += 1
    if r["success"]:
        tier_stats[(m, mode, tier)]["passed"] += 1

    suite = r.get("suite", "unspecified")
    suite_stats[(m, mode, suite)]["total"] += 1
    if r["success"]:
        suite_stats[(m, mode, suite)]["passed"] += 1

print(f"{'Model':<20} {'Mode':<18} {'Total':<6} {'Passed':<7} {'Pass Rate':<10} {'95% CI':<15} {'EmptyGen':<10} {'InvalidOut':<10}")
print("-" * 105)
for (m, mode), d in sorted(overall.items()):
    n = d["total"]
    k = d["passed"]
    rate = f"{k/n*100:.1f}%" if n else "0%"
    low, high = wilson_score_interval(k, n)
    ci_str = f"[{low}%, {high}%]"
    print(f"{m:<20} {mode:<18} {n:<6} {k:<7} {rate:<10} {ci_str:<15} {d['empty_gen']:<10} {d['invalid_out']:<10}")
print("=" * 105)

# Tier Table
print("\n--- Two-Tier Breakdown (Level 1 Baseline vs Level 2 Advanced) ---")
print(f"{'Model':<20} {'Mode':<18} {'Tier':<10} {'Total':<6} {'Passed':<7} {'Pass Rate':<10}")
print("-" * 75)
for (m, mode, tier), d in sorted(tier_stats.items()):
    n = d["total"]
    k = d["passed"]
    rate = f"{k/n*100:.1f}%" if n else "0%"
    print(f"{m:<20} {mode:<18} {tier:<10} {n:<6} {k:<7} {rate:<10}")

# Suite Table
print("\n--- Suite Breakdown (Synthetic Fixtures) ---")
print(f"{'Model':<20} {'Mode':<18} {'Suite (synthetic)':<22} {'Total':<6} {'Passed':<7} {'Pass Rate':<10}")
print("-" * 85)
for (m, mode, suite), d in sorted(suite_stats.items()):
    n = d["total"]
    k = d["passed"]
    rate = f"{k/n*100:.1f}%" if n else "0%"
    note = " (underpowered)" if n < 8 else ""
    print(f"{m:<20} {mode:<18} {suite + note:<22} {n:<6} {k:<7} {rate:<10}")

# Generate run_manifest.json
manifest = {
    "schema_version": "pdx_fair_run_manifest_v1",
    "benchmark": "PDX Synthetic SLM Dispatch Fair Comparison",
    "conditions": ["goldplan_react", "goldplan_isolated"],
    "engine_invocations": 0,
    "completed_at": datetime.now(timezone.utc).isoformat(),
    "total_evaluations": len(all_eval_results),
    "model_statuses": model_statuses,
    "status": "completed"
}

with open("/kaggle/working/run_manifest.json", "w", encoding="utf-8") as f_m:
    json.dump(manifest, f_m, indent=2, ensure_ascii=False)

# Generate artifact_manifest.json with SHA-256 CAS
artifacts = []
for filename in ["benchmark_ledger.jsonl", "run_manifest.json"]:
    filepath = os.path.join("/kaggle/working", filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f_b:
            sha = hashlib.sha256(f_b.read()).hexdigest()
        artifacts.append({"path": filename, "sha256": sha})

artifact_manifest = {
    "schema_version": "pdx_artifact_manifest_v1",
    "artifacts": artifacts
}

with open("/kaggle/working/artifact_manifest.json", "w", encoding="utf-8") as f_am:
    json.dump(artifact_manifest, f_am, indent=2, ensure_ascii=False)

print("\nManifests generated: run_manifest.json & artifact_manifest.json.")
print("Benchmark Run Completed Successfully.")
'''
    cells.append(create_code_cell(summary_code))

    notebook = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"provenance": []},
            "gpuClass": "standard",
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbformat": 4,
                "nbformat_minor": 2,
                "version": "3.10.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }
    return notebook


def main():
    nb = build_notebook()
    out_path = ROOT / "notebooks" / "pdx_phase0_fair_benchmark.ipynb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print(f"Generated fair benchmark notebook: {out_path} ({len(nb['cells'])} cells)")


if __name__ == "__main__":
    main()
