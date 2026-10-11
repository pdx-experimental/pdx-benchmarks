"""Condition Runner for Phase 2 Experiment 2: C4 Leaf-Worker Context Window on RULER.

Tests the ProDocuX C4 Leaf-Worker Context Window Hypothesis on long-context RULER tasks.
Fixed runtime: goldplan_isolated
Fixed prompt: 1-Shot generic exemplar (calc 1+1)
Fixed decoding: Free greedy decode (temp=0.0)

Three Window Conditions:
- W0_full: Full uncropped context (~9k-40k chars)
- W1_head_2k: Exact head 2,000 chars (task.context[:2000])
- W2_keyword_2k: Instruction-driven keyword search window (<= 2,000 chars)
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any, Callable, Dict, List, Optional
from src.runners.goldplan_react import parse_model_json

STOPWORDS = {
    "search", "for", "the", "in", "to", "of", "and", "a", "an", "is", "step",
    "assigned", "matching", "with", "from", "by", "linked", "identify", "count",
    "distinct", "listed", "most", "frequent", "use", "find", "get", "what",
    "which", "that", "this", "was", "then", "context", "only", "output", "task",
    "final", "answer", "goal"
}

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


def extract_instruction_keywords(instruction: str, parent_artifacts: Optional[List[str]] = None, task_prompt: str = "") -> List[str]:
    """Extract content keywords from instruction and parent artifacts without ground-truth oracle."""
    combined_text = instruction
    if task_prompt:
        combined_text += f" {task_prompt}"
    if parent_artifacts:
        for art in parent_artifacts:
            if art and isinstance(art, str):
                combined_text += f" {art}"

    tokens = re.findall(r"[A-Za-z0-9_\-#]+", combined_text)
    keywords: List[str] = []
    for tok in tokens:
        clean = tok.strip(".,:;()[]{}'\"")
        if clean.lower() not in STOPWORDS and len(clean) >= 3:
            if clean not in keywords:
                keywords.append(clean)
    return keywords


def build_head_window(context: str, max_chars: int = 2000) -> str:
    """Extract head 2k characters control window."""
    if not context:
        return ""
    return context[:max_chars]


def build_keyword_window(context: str, keywords: List[str], max_chars: int = 2000) -> str:
    """Build bounded <=2k window centered on instruction keyword matches (Zero-Oracle)."""
    if not context:
        return ""
    lines = context.splitlines(keepends=True)
    if not lines:
        return ""
    if len(context) <= max_chars:
        return context

    # Score each line by keyword hits
    line_scores: List[int] = []
    for line in lines:
        line_lower = line.lower()
        score = sum(1 for kw in keywords if kw.lower() in line_lower)
        line_scores.append(score)

    max_score = max(line_scores) if line_scores else 0
    if max_score == 0:
        # Fallback to head window if no keywords match
        return build_head_window(context, max_chars)

    # Pick the line index with the highest score
    best_idx = line_scores.index(max_score)

    # Symmetrically expand around best_idx
    start_idx = best_idx
    end_idx = best_idx + 1

    while True:
        expanded = False
        # Try expanding before
        if start_idx > 0:
            candidate_len = len("".join(lines[start_idx - 1 : end_idx]))
            if candidate_len <= max_chars:
                start_idx -= 1
                expanded = True
            else:
                break
        # Try expanding after
        if end_idx < len(lines):
            candidate_len = len("".join(lines[start_idx : end_idx + 1]))
            if candidate_len <= max_chars:
                end_idx += 1
                expanded = True
            else:
                break
        if not expanded:
            break

    window = "".join(lines[start_idx:end_idx])
    if len(window) > max_chars:
        window = window[:max_chars]
    return window


class C4WindowRunner:
    def __init__(self, generate_free_fn: Callable[[List[Dict[str, str]], int], str]):
        self.generate_free_fn = generate_free_fn

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

            parent_receipts_text = ""
            parent_artifacts = []
            if depends_on:
                receipt_lines = []
                for pid in depends_on:
                    r = receipts.get(pid, {"artifact": "", "sha256": "none", "status": "missing"})
                    receipt_lines.append(f"- Step '{pid}': artifact='{r['artifact']}' (sha256={r['sha256']}, status={r['status']})")
                    if r.get("artifact"):
                        parent_artifacts.append(r["artifact"])
                parent_receipts_text = "Parent Step Receipts:\n" + "\n".join(receipt_lines) + "\n\n"

            # Apply Context Window condition
            if condition == "W0_full":
                step_context = task.context
            elif condition == "W1_head_2k":
                step_context = build_head_window(task.context, max_chars=2000)
            elif condition == "W2_keyword_2k":
                keywords = extract_instruction_keywords(instruction, parent_artifacts=parent_artifacts, task_prompt=task.prompt)
                step_context = build_keyword_window(task.context, keywords, max_chars=2000)
            else:
                raise ValueError(f"Unknown window condition: {condition}")

            user_prompt = (
                f"Goal: {task.prompt}\n\n"
                f"Context:\n{step_context}\n\n"
                f"{parent_receipts_text}"
                f"Current Step: {step_id}\n"
                f"Step Instruction: {instruction}\n\n"
                "Execute this step and return your JSON decision."
            )

            # Fixed 1-shot exemplar prompt
            step_messages = [
                {"role": "system", "content": system_prompt},
                EXEMPLAR_MESSAGES[0],
                EXEMPLAR_MESSAGES[1],
                {"role": "user", "content": user_prompt},
            ]

            step_chars = sum(len(m["content"]) for m in step_messages)
            context_growth.append(step_chars)

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
                # Leaf-worker tool executes against assigned step_context
                obs = execute_tool_fn(tool_call["name"], tool_call["args"], step_context)
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
            "mode": condition,
            "task_id": task.task_id,
            "suite": task.suite,
            "tier": task.tier,
            "status": "completed",
            "success": False,  # Scored afterwards by score_answer
            "invalid_outputs": invalid_outputs,
            "empty_generations": empty_generations,
            "steps_taken": step_count,
            "elapsed_s": elapsed_s,
            "final_answer": final_answer,
            "expected_answer": task.expected_answer,
            "context_chars_last": context_chars_last,
            "context_growth": context_growth,
            "score_reason": "",
        }
