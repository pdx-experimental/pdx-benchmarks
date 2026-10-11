"""PDX Artifact Engine Runner for Phase 0 Baseline (Governed Group).

Implements canonical pdx_execution_plan_v1 DAG step dispatch, bounded
dependency context passing, SHA-256 receipt generation, and checkpoint CAS.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class PDXEngineRunner:
    def __init__(self, llm_generate_fn: Callable[[str], str], chat_template_fn: Optional[Callable[[List[Dict[str, str]]], str]] = None):
        self.generate = llm_generate_fn
        self.apply_chat_template = chat_template_fn

    def format_prompt(self, system: str, user: str) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        if self.apply_chat_template is not None:
            try:
                return self.apply_chat_template(messages)
            except Exception:
                pass
        # Fallback to standard ChatML format if template function unavailable
        return f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"

    def run_task(self, task: Any, tool_executor: Callable[[str, Dict[str, Any]], str]) -> Dict[str, Any]:
        start_time = time.time()
        pdx_plan = task.to_pdx_plan()
        request_id = pdx_plan["request_id"]
        steps = pdx_plan.get("steps", [])

        # Step Receipts and Checkpoints ledger
        step_receipts: Dict[str, Dict[str, Any]] = {}
        checkpoint: Dict[str, Any] = {
            "schema_version": "pdx_checkpoint_v1",
            "request_id": request_id,
            "completed_steps": [],
            "pending_steps": [s["id"] for s in steps],
        }

        system_instruction = (
            "You are the PDX Step Dispatcher and Executor under pdx_execution_plan_v1.\n"
            "You execute one discrete, bounded step in a governed execution DAG.\n"
            "You must output ONLY a valid JSON object matching this exact schema:\n"
            "{\n"
            '  "thought": "one-sentence concise reasoning",\n'
            '  "action": "execute_tool" | "emit_artifact" | "complete_task",\n'
            '  "tool_call": {"name": "...", "args": {...}},\n'
            '  "artifact": "string result or value produced by this step"\n'
            "}\n"
            "Do not include any conversational commentary or markdown outside the JSON object."
        )

        steps_taken = 0
        schema_violations = 0
        total_prompt_chars = 0
        prompt_lengths_per_step: List[int] = []
        final_answer = ""
        overall_status = "in_progress"

        # Execute DAG steps in order
        for step_def in steps:
            steps_taken += 1
            step_id = step_def["id"]
            kind = step_def.get("kind", "tool")
            instruction = step_def.get("instruction", "")
            depends_on = step_def.get("depends_on", [])

            # Bounded context: ONLY upstream receipts declared in depends_on
            dep_receipts: List[Dict[str, Any]] = []
            for dep_id in depends_on:
                if dep_id in step_receipts:
                    r = step_receipts[dep_id]
                    dep_receipts.append({
                        "step_id": dep_id,
                        "status": r["status"],
                        "output_digest": r["output_digest"],
                        "artifact": r["artifact"]
                    })

            user_step_prompt = (
                f"Task Goal: {task.prompt}\n"
                f"Step ID: {step_id}\n"
                f"Kind: {kind}\n"
                f"Instruction: {instruction}\n"
                f"Declared Upstream Receipts: {json.dumps(dep_receipts, indent=2)}\n"
                f"Available Tools: {[t.get('name') for t in task.tools]}\n"
                f"Context Reference: {task.context[:500]}\n"
                f"Provide the execution decision JSON:"
            )

            formatted_prompt = self.format_prompt(system_instruction, user_step_prompt)
            prompt_len = len(formatted_prompt)
            prompt_lengths_per_step.append(prompt_len)
            total_prompt_chars += prompt_len

            response_raw = self.generate(formatted_prompt)

            # Parse schema
            parsed_decision: Dict[str, Any] = {}
            try:
                clean_json = response_raw.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                elif "{" in clean_json and "}" in clean_json:
                    clean_json = clean_json[clean_json.find("{"):clean_json.rfind("}")+1]
                parsed_decision = json.loads(clean_json)
            except Exception:
                schema_violations += 1
                # Robust recovery: extract key value directly or fallback
                parsed_decision = {"thought": "Schema parse error", "action": "emit_artifact", "artifact": response_raw.strip()}

            action = parsed_decision.get("action", "emit_artifact")
            artifact_val = str(parsed_decision.get("artifact", ""))

            # Execute tool if requested
            if action == "execute_tool" or step_def.get("tool"):
                tool_call = parsed_decision.get("tool_call") or {}
                tool_name = tool_call.get("name") or step_def.get("tool")
                tool_args = tool_call.get("args") or {"input": instruction, "context": task.context}
                try:
                    tool_res = tool_executor(tool_name, tool_args)
                    artifact_val = str(tool_res)
                    step_status = "success"
                except Exception as ex:
                    artifact_val = f"Tool Error: {str(ex)}"
                    step_status = "tool_error"
            else:
                step_status = "success"

            # Create immutable SHA-256 step receipt
            digest = compute_sha256(artifact_val)
            receipt = {
                "schema_version": "pdx_step_receipt_v1",
                "receipt_id": f"{request_id}:{step_id}:{steps_taken}",
                "step_id": step_id,
                "status": step_status,
                "input_digest": compute_sha256(user_step_prompt),
                "output_digest": digest,
                "artifact": artifact_val,
                "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

            step_receipts[step_id] = receipt
            checkpoint["completed_steps"].append(step_id)
            if step_id in checkpoint["pending_steps"]:
                checkpoint["pending_steps"].remove(step_id)

            final_answer = artifact_val

        elapsed = time.time() - start_time
        success = (task.expected_answer.lower() in final_answer.lower()) if final_answer else False
        overall_status = "success" if success else "failed"

        run_manifest = {
            "schema_version": "pdx_run_manifest_v1",
            "request_id": request_id,
            "overall_status": overall_status,
            "steps_taken": steps_taken,
            "schema_violations": schema_violations,
            "step_receipts": list(step_receipts.values()),
            "checkpoint": checkpoint,
        }

        return {
            "mode": "pdx_engine",
            "task_id": task.task_id,
            "suite": task.suite,
            "status": overall_status,
            "success": success,
            "steps_taken": steps_taken,
            "schema_violations": schema_violations,
            "final_answer": final_answer,
            "elapsed_seconds": round(elapsed, 3),
            "estimated_tokens_consumed": total_prompt_chars // 4,
            "context_growth": prompt_lengths_per_step,
            "run_manifest": run_manifest,
        }
