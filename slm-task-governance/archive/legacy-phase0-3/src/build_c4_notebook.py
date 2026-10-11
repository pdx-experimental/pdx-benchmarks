"""Builds notebooks/pdx_phase2_c4_ruler_window.ipynb for Phase 2 Experiment 2: C4 Leaf-Worker Window.

Protocol:
- 3 Candidate Models:
  1. Qwen/Qwen2.5-Coder-1.5B-Instruct
  2. Qwen/Qwen2.5-Coder-3B-Instruct
  3. unsloth/Llama-3.2-3B-Instruct
- 3 Window Conditions (Runtime frozen to goldplan_isolated, 1-shot prompt, free greedy decoding):
  - W0_full: Full uncropped context (~9k-40k chars)
  - W1_head_2k: Exact head 2,000 chars (task.context[:2000])
  - W2_keyword_2k: Instruction-driven keyword search window (<= 2,000 chars, Zero-Oracle)
- 21 RULER tasks (15 ruler_l1 + 6 ruler_multihop)
- Total Evaluations: 3 models x 3 conditions x 21 tasks = 189 evaluations
- Hardened scorer with strict numeric gating.
"""

from __future__ import annotations

import ast
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
            """# PDX SLM Governance Phase 2 -- Experiment 2: C4 Leaf-Worker Context Window (Dual Tesla T4)
## Testing the Local Receptive Field Hypothesis on Long-Context RULER Tasks

This benchmark tests the **ProDocuX C4 Leaf-Worker Context Window Hypothesis** across 3 candidate models on Dual Tesla T4 GPUs:
- **Core Hypothesis**: Confining the leaf worker's receptive field to an orchestrator-directed keyword window (<= 2k chars) eliminates long-context attention distraction, boosting task success over full context (~9k-40k chars).
- **Control**: `W1_head_2k` controls for input length reduction (proves gain is NOT merely due to shorter input).

### The 3 Window Conditions (Runtime frozen to `goldplan_isolated`, 1-Shot Exemplar, Free Greedy Decoding):
1. **`W0_full`**: Full uncropped context (~9k-40k chars, baseline control)
2. **`W1_head_2k`**: Head 2,000 chars (`task.context[:2000]`, length control)
3. **`W2_keyword_2k`**: Instruction keyword search +/- symmetric expansion (<= 2000 chars, Zero-Oracle treatment)

### Evaluated Models & Scope (3 Models x 3 Conditions x 21 RULER Tasks = 189 Evaluations):
- `qwen2.5_coder_1.5b` (`Qwen/Qwen2.5-Coder-1.5B-Instruct`)
- `qwen2.5_coder_3b` (`Qwen/Qwen2.5-Coder-3B-Instruct`)
- `llama3.2_3b` (`unsloth/Llama-3.2-3B-Instruct`)
- **Tasks**: 21 standardized RULER tasks (15 in `ruler_l1` + 6 in `ruler_multihop`)
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

    # Code 2: Environment Setup
    cells.append(
        create_code_cell(
            """print("=== 2. Environment Setup ===")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "transformers>=4.50.0", "accelerate", "pdx-artifact-engine==0.3.0a9"], check=True)
import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
import torch
import transformers
import pdx_artifact_engine

print("PyTorch Version:", torch.__version__, "| CUDA Available:", torch.cuda.is_available(), "| GPU Count:", torch.cuda.device_count())
print("Transformers Version:", transformers.__version__)
print("PDX Artifact Engine Installed.")
"""
        )
    )

    # Code 3: Honest Tools
    tools_code = (ROOT / "src" / "tools.py").read_text(encoding="utf-8")
    cells.append(create_code_cell(f"# === 3. Honest Tools Fixture Environment ===\n{tools_code}"))

    # Code 4: Hardened Scorer
    scoring_code = (ROOT / "src" / "scoring.py").read_text(encoding="utf-8")
    cells.append(create_code_cell(f"# === 4. Hardened Answer Scorer ===\n{scoring_code}"))

    # Code 5: RULER Tasks Loader (21 Tasks)
    loader_code = (ROOT / "src" / "benchmark_loader.py").read_text(encoding="utf-8")
    filter_code = """
# Filter benchmark tasks strictly to RULER suites (21 tasks: 15 ruler_l1 + 6 ruler_multihop)
ALL_TASKS = load_benchmark_suite()
BENCHMARK_TASKS = [t for t in ALL_TASKS if "ruler" in t.suite]
print(f"Loaded {len(BENCHMARK_TASKS)} RULER benchmark tasks for Experiment 2.")
assert len(BENCHMARK_TASKS) == 21, f"Expected exactly 21 RULER tasks, found {len(BENCHMARK_TASKS)}"
"""
    cells.append(create_code_cell(f"# === 5. Standardized 21 RULER Benchmark Tasks ===\n{loader_code}\n{filter_code}"))

    # Code 6: C4 Window Runner & Parser
    runner_code = (ROOT / "src" / "runners" / "c4_window_runner.py").read_text(encoding="utf-8")
    runner_code_clean = runner_code.replace(
        "from src.runners.goldplan_react import parse_model_json",
        "# parse_model_json defined inline below"
    )
    react_json_parser_code = """
import re
from typing import Tuple, Optional

def parse_model_json(text: str, allowed_tools: List[str] = None) -> Tuple[Optional[Dict[str, Any]], str]:
    if not text:
        return None, "empty_generation"
    cleaned = text.strip()
    match = re.search(r'\\{.*\\}', cleaned, re.DOTALL)
    if not match:
        return None, "no_json_object"
    json_candidate = match.group(0)
    try:
        data = json.loads(json_candidate)
    except Exception as e:
        return None, f"json_syntax_error: {e}"
    if not isinstance(data, dict):
        return None, "json_not_object"
    action = data.get("action")
    if action not in ["execute_tool", "final_answer"]:
        return None, f"invalid_action: {action}"
    if action == "execute_tool":
        tool_call = data.get("tool_call")
        if not isinstance(tool_call, dict) or "name" not in tool_call or "args" not in tool_call:
            return None, "invalid_tool_call_structure"
        name = tool_call.get("name")
        if allowed_tools is not None and name not in allowed_tools:
            return None, f"unknown_tool: {name}"
    elif action == "final_answer":
        if "answer" not in data or data.get("answer") is None:
            return None, "missing_answer_field"
    return data, "valid"
"""
    cells.append(create_code_cell(f"# === 6. C4 Leaf-Worker Window Runner ===\n{react_json_parser_code}\n{runner_code_clean}"))

    # Code 7: Model Execution Loop (3 models x 3 conditions x 21 tasks = 189 evaluations)
    exec_loop_code = r"""# === 7. Candidate Models & C4 Window Execution Loop ===
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM

CANDIDATE_MODELS = [
    {"name": "qwen2.5_coder_1.5b", "model_id": "Qwen/Qwen2.5-Coder-1.5B-Instruct"},
    {"name": "qwen2.5_coder_3b", "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct"},
    {"name": "llama3.2_3b", "model_id": "unsloth/Llama-3.2-3B-Instruct"}
]

CONDITIONS = ["W0_full", "W1_head_2k", "W2_keyword_2k"]

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

    print(f"\n=================== Loading Model: {model_name} ({model_id}) ===================")
    gc.collect()
    torch.cuda.empty_cache()

    model = None
    tokenizer = None

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        model.eval()
        print(f"Model {model_name} loaded successfully on {model.device}.")
    except Exception as e:
        print(f"CRITICAL: Failed to load {model_name}: {e}")
        model_statuses[model_name] = f"load_failed: {e}"
        continue

    def generate_free_fn(messages, max_tokens=256) -> str:
        if model is None:
            return ""
        try:
            prompt_str = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt_str, return_tensors="pt", truncation=False).to(model.device)
            with torch.no_grad():
                output_tokens = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            input_len = inputs.input_ids.shape[1]
            gen_ids = output_tokens[0, input_len:] if output_tokens.shape[1] > input_len else output_tokens[0]
            return tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        except Exception:
            return ""

    runner = C4WindowRunner(generate_free_fn)
    model_statuses[model_name] = "evaluated"

    for cond in CONDITIONS:
        print(f"\n--- Running {model_name} in {cond} mode ({len(BENCHMARK_TASKS)} tasks) ---")
        passed_count = 0
        invalid_count = 0

        for idx, task in enumerate(BENCHMARK_TASKS):
            res = runner.run_task(task, cond, execute_benchmark_tool, model_name=model_name, tokenizer=tokenizer)
            is_success, score_reason = score_answer(res["final_answer"], task.expected_answer, suite=task.suite)
            res["success"] = is_success
            res["score_reason"] = score_reason

            if is_success:
                passed_count += 1
            if res.get("invalid_outputs", 0) > 0:
                invalid_count += 1

            all_eval_results.append(res)
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

            if (idx + 1) % 7 == 0 or (idx + 1) == len(BENCHMARK_TASKS):
                print(f"[{model_name} | {cond}] Task {idx+1}/{len(BENCHMARK_TASKS)} -> Passed: {passed_count}, Invalids: {invalid_count}")

    del runner
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    print(f"Model {model_name} evaluation complete and memory released.")
"""
    cells.append(create_code_cell(exec_loop_code))

    # Code 8: Audit Manifest & Cryptographic Receipts
    digest_code = r"""# === 8. Audit Manifest & Cryptographic Receipts ===
import hashlib
import json
import datetime
from pathlib import Path

working_dir = Path("/kaggle/working")
ledger_file = working_dir / "benchmark_ledger.jsonl"

ledger_sha256 = "none"
total_evaluations = len(all_eval_results)

if ledger_file.exists():
    ledger_sha256 = hashlib.sha256(ledger_file.read_bytes()).hexdigest()

manifest = {
    "benchmark_version": "phase2_c4_ruler_window_v1",
    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "hardware": {
        "platform": "Kaggle",
        "accelerator": "Dual Tesla T4",
        "gpu_count": torch.cuda.device_count()
    },
    "experimental_design": {
        "independent_variable": "leaf_worker_context_window",
        "conditions": CONDITIONS,
        "runtime": "goldplan_isolated",
        "prompt_scaffolding": "one_shot_calc_generic",
        "decoding": "free_greedy_temp_0"
    },
    "evaluated_models": CANDIDATE_MODELS,
    "model_statuses": model_statuses,
    "total_tasks_per_condition": len(BENCHMARK_TASKS),
    "total_evaluations": total_evaluations,
    "engine_invocations": 0,
    "ledger_cas_sha256": ledger_sha256
}

manifest_path = working_dir / "run_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

print("\n=== C4 RULER BENCHMARK EXECUTION SUMMARY ===")
print(f"Total Evaluations Completed: {total_evaluations} (Expected: {len(CANDIDATE_MODELS) * len(CONDITIONS) * len(BENCHMARK_TASKS)})")
print(f"Ledger SHA-256: {ledger_sha256}")
print(f"Manifest written to: {manifest_path}")

print("\n=== Window Condition Performance Matrix (21 RULER Tasks) ===")
print(f"{'Model':<20} | {'Condition':<15} | {'Passed/Total':<12} | {'Pass Rate':<10} | {'Invalids':<8} | {'Avg Latency'}")
print("-" * 80)
for cand in CANDIDATE_MODELS:
    m_name = cand["name"]
    for cond in CONDITIONS:
        sub = [r for r in all_eval_results if r["model"] == m_name and r["mode"] == cond]
        p = sum(1 for r in sub if r["success"])
        inv = sum(r["invalid_outputs"] for r in sub)
        lat = sum(r["elapsed_s"] for r in sub) / max(len(sub), 1)
        print(f"{m_name:<20} | {cond:<15} | {f'{p}/{len(sub)}':<12} | {p/max(len(sub),1)*100:5.1f}%     | {inv:<8} | {lat:5.2f}s")
"""
    cells.append(create_code_cell(digest_code))

    return {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"provenance": []},
            "gpuClass": "standard",
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }


def main():
    nb = build_notebook()
    # Pre-validate all code cells syntax with AST
    for idx, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            source_text = "".join(c["source"])
            try:
                ast.parse(source_text)
            except SyntaxError as e:
                print(f"FATAL: SyntaxError in Cell {idx+1}: {e}")
                raise

    out_path = ROOT / "notebooks" / "pdx_phase2_c4_ruler_window.ipynb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {out_path.name} with {len(nb['cells'])} cells (all AST syntax validated).")


if __name__ == "__main__":
    main()
