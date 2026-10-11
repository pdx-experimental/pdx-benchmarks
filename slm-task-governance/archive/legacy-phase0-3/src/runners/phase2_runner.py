"""Condition Runner for Phase 2 2x2 Factorial Benchmark.

Frozen runtime: goldplan_isolated (fresh messages per step, parent receipts).
Supports 4 conditions:
- C0_anchor: Zero-shot prompt + Free greedy decode
- C1_grammar: Zero-shot prompt + Dynamic JSON schema constrained decode
- C2_oneshot: 1-Shot generic exemplar (calc 1+1) + Free greedy decode
- C3_dual_governed: 1-Shot generic exemplar + Dynamic JSON schema constrained decode
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional
from src.runners.goldplan_react import parse_model_json

EXEMPLAR_MESSAGES = [
    {
        "role": "user",
        "content": (
            "Goal: Calculate 1 + 1\n\n"
            "Context:\n\n"
            "Current Step: step_calc\n"
            "Step Instruction: Use calc to compute 1 + 1.\n\n"
            "Execute this step and return your JSON decision."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "{\n"
            '  "thought": "Calculate the sum of 1 and 1.",\n'
            '  "action": "execute_tool",\n'
            '  "tool_call": {"name": "calc", "args": {"expression": "1 + 1"}},\n'
            '  "answer": ""\n'
            "}"
        ),
    },
]


class Phase2FactorialRunner:
    def __init__(self, generate_free_fn: Callable[[List[Dict[str, str]], int], str], dynamic_generator: Any):
        self.generate_free_fn = generate_free_fn
        self.dynamic_generator = dynamic_generator

    def run_task(
        self,
        task: Any,
        condition: str,
        execute_tool_fn: Callable[[str, Dict[str, Any], str], str],
        model_name: str = "unknown_model",
        tokenizer: Optional[Any] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        gold_steps = task.get_full_gold_steps()
        available_tools = [t["name"] for t in task.tools]
        tools_desc = json.dumps(task.tools, indent=2)

        receipts: Dict[str, Dict[str, Any]] = {}
        step_count = 0
        invalid_outputs = 0
        empty_generations = 0
        constrained_failures = 0
        final_answer = ""
        context_growth = []

        is_oneshot = condition in ["C2_oneshot", "C3_dual_governed"]
        is_constrained = condition in ["C1_grammar", "C3_dual_governed"]

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

            if is_oneshot:
                step_messages = [
                    {"role": "system", "content": system_prompt},
                    EXEMPLAR_MESSAGES[0],
                    EXEMPLAR_MESSAGES[1],
                    {"role": "user", "content": user_prompt},
                ]
            else:
                step_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

            step_chars = sum(len(m["content"]) for m in step_messages)
            context_growth.append(step_chars)

            raw_response = ""
            if is_constrained:
                try:
                    if tokenizer is not None:
                        prompt_str = tokenizer.apply_chat_template(step_messages, tokenize=False, add_generation_prompt=True)
                    else:
                        prompt_str = "\n".join([f"{m['role']}: {m['content']}" for m in step_messages]) + "\nassistant:"
                    raw_response = self.dynamic_generator.generate(prompt_str, allowed_tools=available_tools, max_new_tokens=256)
                except Exception as ex:
                    constrained_failures += 1
                    invalid_outputs += 1
                    receipts[step_id] = {
                        "artifact": "",
                        "sha256": "invalid",
                        "status": "invalid_constrained_generation",
                        "reason": str(ex),
                    }
                    continue
            else:
                raw_response = self.generate_free_fn(step_messages, max_tokens=256)

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

        status_tag = "completed"
        if constrained_failures > 0:
            status_tag = "invalid_constrained_generation"

        return {
            "model": model_name,
            "mode": condition,
            "task_id": task.task_id,
            "suite": task.suite,
            "tier": task.tier,
            "status": status_tag,
            "success": False,
            "invalid_outputs": invalid_outputs,
            "empty_generations": empty_generations,
            "constrained_failures": constrained_failures,
            "steps_taken": step_count,
            "elapsed_s": elapsed_s,
            "final_answer": final_answer,
            "expected_answer": task.expected_answer,
            "context_chars_last": context_chars_last,
            "context_growth": context_growth,
        }
