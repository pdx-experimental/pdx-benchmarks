"""Builds notebooks/pdx_phase2_2x2_factorial.ipynb for Phase 2 2x2 Factorial Benchmark.

Protocol:
- 3 Candidate Models:
  1. Qwen/Qwen2.5-Coder-1.5B-Instruct
  2. Qwen/Qwen2.5-Coder-3B-Instruct
  3. unsloth/Llama-3.2-3B-Instruct
- 4 Conditions (Frozen to goldplan_isolated runtime):
  - C0_anchor: Zero-shot + Free Greedy (temp=0.0)
  - C1_grammar: Zero-shot + JSON Schema Constrained
  - C2_oneshot: 1-Shot Generic Exemplar (calc 1+1) + Free Greedy
  - C3_dual_governed: 1-Shot Generic Exemplar + JSON Schema Constrained
- 76 standardized tasks (Total: 3 x 4 x 76 = 912 evaluations)
- Hardened scorer with strict numeric gating.
- Failure safeguard: constrained decoding failures marked 'invalid_constrained_generation', never 0%.
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
            """# PDX SLM Governance Phase 2 — 2x2 Factorial Benchmark (Dual Tesla T4)
## Disentangling Schema Noise from Cognitive Ceiling in Small Language Models

This benchmark executes a strictly controlled 2x2 factorial experiment across 3 candidate models on Dual Tesla T4 GPUs:
- **Factor A (Prompt Scaffolding)**: Zero-Shot vs 1-Shot Generic Exemplar (`calc 1+1`)
- **Factor B (Decoding Governance)**: Free Greedy (`temp=0.0`) vs Dynamic JSON Schema Constrained Decoding (`outlines`)

### The 4 Factorial Conditions (Runtime frozen to `goldplan_isolated`):
1. **`C0_anchor`**: Zero-Shot + Free Greedy (Calibration baseline)
2. **`C1_grammar`**: Zero-Shot + Constrained JSON Schema (Testing format failure removal)
3. **`C2_oneshot`**: 1-Shot Exemplar + Free Greedy (Testing in-context grounding)
4. **`C3_dual_governed`**: 1-Shot Exemplar + Constrained JSON Schema (Testing combined maximum governance)

### Evaluated Models (3 Models, 912 Evaluations):
- `qwen2.5_coder_1.5b` (`Qwen/Qwen2.5-Coder-1.5B-Instruct`)
- `qwen2.5_coder_3b` (`Qwen/Qwen2.5-Coder-3B-Instruct`)
- `llama3.2_3b` (`unsloth/Llama-3.2-3B-Instruct`)
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
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "transformers>=4.50.0", "accelerate", "outlines>=1.3.0", "pdx-artifact-engine==0.3.0a9"], check=True)
import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
import torch
import transformers
import outlines
import pdx_artifact_engine

print("PyTorch Version:", torch.__version__, "| CUDA Available:", torch.cuda.is_available(), "| GPU Count:", torch.cuda.device_count())
print("Transformers Version:", transformers.__version__)
print("Outlines Version Installed successfully.")
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

    # Code 5: Constrained Decoding Engine
    constrained_code = (ROOT / "src" / "constrained_decoding.py").read_text(encoding="utf-8")
    cells.append(create_code_cell(f"# === 5. Dynamic JSON Schema Constrained Engine ===\n{constrained_code}"))

    # Code 6: Benchmark Tasks Loader
    loader_code = (ROOT / "src" / "benchmark_loader.py").read_text(encoding="utf-8")
    cells.append(create_code_cell(f"# === 6. Standardized 76 Benchmark Tasks ===\n{loader_code}"))

    # Code 7: Phase 2 Factorial Runner
    runner_code = (ROOT / "src" / "runners" / "phase2_runner.py").read_text(encoding="utf-8")
    runner_code_clean = runner_code.replace(
        "from src.runners.goldplan_react import parse_model_json",
        "# parse_model_json defined above"
    )
    # JSON parser helper for runner
    react_json_parser_code = """
# JSON parser helper for runner
import re
def parse_model_json(text: str, allowed_tools: List[str] = None) -> Tuple[Optional[Dict[str, Any]], str]:
    if not text:
        return None, "empty_generation"
    cleaned = text.strip()
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
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
    cells.append(create_code_cell(f"# === 7. Phase 2 2x2 Factorial Runner ===\n{react_json_parser_code}\n{runner_code_clean}"))

    # Code 8: Model Execution Loop
    exec_loop_code = r"""# === 8. Candidate Models & 2x2 Factorial Execution Loop ===
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM

CANDIDATE_MODELS = [
    {"name": "qwen2.5_coder_1.5b", "model_id": "Qwen/Qwen2.5-Coder-1.5B-Instruct"},
    {"name": "qwen2.5_coder_3b", "model_id": "Qwen/Qwen2.5-Coder-3B-Instruct"},
    {"name": "llama3.2_3b", "model_id": "unsloth/Llama-3.2-3B-Instruct"}
]

CONDITIONS = ["C0_anchor", "C1_grammar", "C2_oneshot", "C3_dual_governed"]

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

    print(f"Initializing DynamicSchemaGenerator for {model_name}...")
    dynamic_gen = DynamicSchemaGenerator(model, tokenizer)

    runner = Phase2FactorialRunner(generate_free_fn, dynamic_gen)
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
            if res.get("status") == "invalid_constrained_generation" or res.get("invalid_outputs", 0) > 0:
                invalid_count += 1

            all_eval_results.append(res)
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

            if (idx + 1) % 15 == 0 or (idx + 1) == len(BENCHMARK_TASKS):
                print(f"[{model_name} | {cond}] Step {idx+1}/{len(BENCHMARK_TASKS)} -> Passed: {passed_count}, Invalids: {invalid_count}")

    del dynamic_gen
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    print(f"Model {model_name} evaluation complete and memory released.")
"""
    cells.append(create_code_cell(exec_loop_code))

    # Code 9: Run Manifest & Digest Generation
    digest_code = r"""# === 9. Audit Manifest & Cryptographic Ledger SHA-256 Receipts ===
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
    "benchmark_version": "phase2_2x2_factorial_v1",
    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "hardware": {
        "platform": "Kaggle",
        "accelerator": "Dual Tesla T4",
        "gpu_count": torch.cuda.device_count()
    },
    "factorial_design": {
        "factor_a_prompting": ["zero_shot", "one_shot_calc_generic"],
        "factor_b_decoding": ["free_greedy", "dynamic_json_schema_constrained"],
        "conditions": CONDITIONS
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

print("\n=== BENCHMARK EXECUTION SUMMARY ===")
print(f"Total Evaluations Completed: {total_evaluations} (Expected: {len(CANDIDATE_MODELS) * len(CONDITIONS) * len(BENCHMARK_TASKS)})")
print(f"Ledger SHA-256: {ledger_sha256}")
print(f"Manifest written to: {manifest_path}")

print("\n=== Condition Pass Rates ===")
for cand in CANDIDATE_MODELS:
    m_name = cand["name"]
    print(f"\nModel: {m_name}")
    for cond in CONDITIONS:
        sub = [r for r in all_eval_results if r["model"] == m_name and r["mode"] == cond]
        p = sum(1 for r in sub if r["success"])
        inv = sum(r["invalid_outputs"] for r in sub)
        fail_cg = sum(r["constrained_failures"] for r in sub)
        print(f"  {cond:18}: Passed {p:2d}/76 ({p/76*100:5.1f}%) | Invalids: {inv:3d} | Grammar Fails: {fail_cg}")
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
    import ast
    nb = build_notebook()
    # Pre-validate all code cells syntax!
    for idx, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            source_text = "".join(c["source"])
            try:
                ast.parse(source_text)
            except SyntaxError as e:
                print(f"FATAL: SyntaxError in Cell {idx+1}: {e}")
                raise

    out_path = ROOT / "notebooks" / "pdx_phase2_2x2_factorial.ipynb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {out_path.name} with {len(nb['cells'])} cells (all syntax validated).")


if __name__ == "__main__":
    main()

