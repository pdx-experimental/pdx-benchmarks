"""Condition A: Gold Plan ReAct Runner (Accumulating Conversation Loop).

Strictly follows Section 2A and Section 3 of FAIR_COMPARISON_PLAN.md:
- One ongoing conversation that accumulates history over steps.
- Sees the gold execution plan and full context.
- Requires JSON schema for all turns.
- On invalid output, appends retry observation and continues.
- Never calls tools on empty or malformed outputs.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple


def parse_model_json(response: str, available_tools: List[str]) -> Tuple[Optional[Dict[str, Any]], str]:
    """Validate model output against Section 3 schema.
    
    Returns:
        (parsed_dict_or_None, reason_string)
    """
    if not response or not response.strip():
        return None, "empty_generation"
    
    text = response.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    raw_json = match.group(1).strip() if match else text
    
    start = raw_json.find("{")
    end = raw_json.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw_json = raw_json[start:end+1]
    
    try:
        data = json.loads(raw_json)
    except Exception as exc:
        return None, f"json_parse_error: {exc}"
    
    if not isinstance(data, dict):
        return None, "json_not_a_dict"
    
    action = data.get("action")
    if action not in ["execute_tool", "final_answer"]:
        return None, f"invalid_action: '{action}'"
    
    if action == "execute_tool":
        tool_call = data.get("tool_call")
        if not isinstance(tool_call, dict):
            return None, "missing_or_invalid_tool_call"
        name = tool_call.get("name")
        if name not in available_tools:
            return None, f"tool_not_available: '{name}'"
        args = tool_call.get("args")
        if not isinstance(args, dict):
            return None, "tool_args_not_a_dict"
        has_val = any(v is not None and str(v).strip() != "" for v in args.values())
        if not has_val:
            return None, "empty_tool_args"
        return data, "valid"
    
    elif action == "final_answer":
        ans = data.get("answer")
        if ans is None or not str(ans).strip():
            return None, "empty_final_answer"
        return data, "valid"
    
    return None, "unknown_schema_violation"


class GoldPlanReActRunner:
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
        step_limit = max_steps or (len(gold_steps) + 2)

        gold_plan_text = json.dumps(
            [{"id": s["id"], "instruction": s["instruction"], "depends_on": s.get("depends_on", [])} for s in gold_steps],
            indent=2
        )
        tools_desc = json.dumps(task.tools, indent=2)

        system_prompt = (
            "You are an assistant executing a task according to a gold plan.\n"
            "You must respond ONLY with valid JSON conforming to the following schema:\n"
            "{\n"
            '  "thought": "one short sentence",\n'
            '  "action": "execute_tool" | "final_answer",\n'
            '  "tool_call": {"name": "<tool>", "args": {"key": "val"}},\n'
            '  "answer": "<string>"\n'
            "}\n\n"
            f"Available Tools:\n{tools_desc}\n\n"
            f"Gold Plan:\n{gold_plan_text}\n\n"
            "Rules:\n"
            "1. Output ONLY the JSON object. No Markdown conversation, no preamble.\n"
            "2. If action is 'execute_tool', 'tool_call' must specify a valid tool and non-empty args.\n"
            "3. If action is 'final_answer', 'answer' must contain the final answer string.\n"
        )

        user_prompt = (
            f"Goal: {task.prompt}\n\n"
            f"Context:\n{task.context}\n\n"
            "Execute the task steps and provide the final answer."
        )

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        step_count = 0
        invalid_outputs = 0
        empty_generations = 0
        final_answer = ""
        context_growth = []

        while step_count < step_limit:
            step_count += 1
            total_chars = sum(len(m["content"]) for m in messages)
            context_growth.append(total_chars)

            raw_response = self.generate_chat_fn(messages, 256)
            messages.append({"role": "assistant", "content": raw_response})

            parsed, reason = parse_model_json(raw_response, available_tools)

            if parsed is None:
                invalid_outputs += 1
                if reason == "empty_generation":
                    empty_generations += 1
                messages.append({
                    "role": "user",
                    "content": f"Observation: invalid_output ({reason}); emit valid JSON schema with action and non-empty args."
                })
                continue

            action = parsed["action"]
            if action == "final_answer":
                final_answer = str(parsed["answer"]).strip()
                break
            elif action == "execute_tool":
                tool_call = parsed["tool_call"]
                obs = execute_tool_fn(tool_call["name"], tool_call["args"], task.context)
                messages.append({"role": "user", "content": f"Observation: {obs}"})

        elapsed_s = round(time.time() - start_time, 3)
        context_chars_last = sum(len(m["content"]) for m in messages)

        return {
            "model": model_name,
            "mode": "goldplan_react",
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
