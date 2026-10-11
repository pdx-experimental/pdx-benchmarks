"""Condition B: Gold Plan Isolated Dispatch Runner (Fresh O(1) Context Per Step).

Strictly follows Section 2B and Section 3 of FAIR_COMPARISON_PLAN.md:
- One fresh messages list per gold step.
- Context receives only: goal, current step instruction, parent receipts (artifact + sha256), and full context.
- No earlier assistant turns are carried forward.
- Same JSON output schema, same tools, same terminal answer requirement.
- Never calls tools on empty or malformed outputs.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional

from src.runners.goldplan_react import parse_model_json


class GoldPlanIsolatedRunner:
    def __init__(self, generate_chat_fn: Callable[[List[Dict[str, str]], int], str]):
        self.generate_chat_fn = generate_chat_fn

    def run_task(
        self,
        task: Any,
        execute_tool_fn: Callable[[str, Dict[str, Any], str], str],
        model_name: str = "unknown_model",
        max_steps: Optional[int] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        gold_steps = task.get_full_gold_steps()
        available_tools = [t["name"] for t in task.tools]
        tools_desc = json.dumps(task.tools, indent=2)

        receipts: Dict[str, Dict[str, Any]] = {}
        step_count = 0
        invalid_outputs = 0
        empty_generations = 0
        final_answer = ""
        context_growth = []

        system_prompt = (
            "You are an isolated step execution agent.\n"
            "You must respond ONLY with valid JSON conforming to the following schema:\n"
            "{\n"
            '  "thought": "one short sentence",\n'
            '  "action": "execute_tool" | "final_answer",\n'
            '  "tool_call": {"name": "<tool>", "args": {"key": "val"}},\n'
            '  "answer": "<string>"\n'
            "}\n\n"
            f"Available Tools:\n{tools_desc}\n\n"
            "Rules:\n"
            "1. Output ONLY the JSON object. No Markdown conversation, no preamble.\n"
            "2. If action is 'execute_tool', 'tool_call' must specify a valid tool and non-empty args.\n"
            "3. If action is 'final_answer', 'answer' must contain the final answer string.\n"
        )

        for step in gold_steps:
            step_count += 1
            step_id = step["id"]
            instruction = step.get("instruction", "")
            depends_on = step.get("depends_on", [])

            # Format parent receipts
            parent_receipts_text = ""
            if depends_on:
                receipt_lines = []
                for pid in depends_on:
                    r = receipts.get(pid, {"artifact": "", "sha256": "none", "status": "missing"})
                    receipt_lines.append(f"- Step '{pid}': artifact='{r['artifact']}' (sha256={r['sha256']}, status={r['status']})")
                parent_receipts_text = "Parent Step Receipts:\n" + "\n".join(receipt_lines) + "\n\n"

            user_prompt = (
                f"Goal: {task.prompt}\n\n"
                f"Context:\n{task.context}\n\n"
                f"{parent_receipts_text}"
                f"Current Step: {step_id}\n"
                f"Step Instruction: {instruction}\n\n"
                "Execute this step and return your JSON decision."
            )

            # Fresh messages for this step!
            step_messages: List[Dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            step_chars = sum(len(m["content"]) for m in step_messages)
            context_growth.append(step_chars)

            raw_response = self.generate_chat_fn(step_messages, 256)
            parsed, reason = parse_model_json(raw_response, available_tools)

            if parsed is None:
                invalid_outputs += 1
                if reason == "empty_generation":
                    empty_generations += 1
                receipts[step_id] = {
                    "artifact": "",
                    "sha256": "invalid",
                    "status": "invalid_output",
                    "reason": reason,
                }
                continue

            action = parsed["action"]
            if action == "final_answer":
                ans = str(parsed["answer"]).strip()
                final_answer = ans
                receipts[step_id] = {
                    "artifact": ans,
                    "sha256": hashlib.sha256(ans.encode("utf-8")).hexdigest()[:16],
                    "status": "completed",
                }
            elif action == "execute_tool":
                tool_call = parsed["tool_call"]
                obs = execute_tool_fn(tool_call["name"], tool_call["args"], task.context)
                digest = hashlib.sha256(str(obs).encode("utf-8")).hexdigest()[:16]
                receipts[step_id] = {
                    "artifact": str(obs),
                    "sha256": digest,
                    "status": "completed",
                }

        elapsed_s = round(time.time() - start_time, 3)
        context_chars_last = context_growth[-1] if context_growth else 0

        return {
            "model": model_name,
            "mode": "goldplan_isolated",
            "task_id": task.task_id,
            "suite": task.suite,
            "tier": task.tier,
            "success": False,  # Will be evaluated by scorer
            "invalid_outputs": invalid_outputs,
            "empty_generations": empty_generations,
            "steps_taken": step_count,
            "elapsed_s": elapsed_s,
            "final_answer": final_answer,
            "expected_answer": task.expected_answer,
            "context_chars_last": context_chars_last,
            "context_growth": context_growth,
        }
