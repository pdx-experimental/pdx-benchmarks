"""Naive ReAct Runner for Phase 0 Baseline (Unconstrained Control Group).

Runs LLM in a raw multi-turn conversation loop without PDX plan validation,
without CAS checkpoints, and with accumulating raw chat context.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, List


class NaiveReActRunner:
    def __init__(self, llm_generate_fn: Callable[[str], str]):
        self.generate = llm_generate_fn

    def run_task(self, task: Any, tool_executor: Callable[[str, Dict[str, Any]], str]) -> Dict[str, Any]:
        start_time = time.time()
        tools_desc = json.dumps(task.tools, indent=2)
        
        system_prompt = (
            f"You are an assistant. Answer the user prompt using available tools.\n"
            f"Tools:\n{tools_desc}\n"
            f"When using a tool, output exactly:\n"
            f"Action: <tool_name>\nAction Input: <json_args>\n"
            f"When you have the final answer, output:\nFinal Answer: <answer>\n"
        )
        
        conversation_history = (
            f"{system_prompt}\n"
            f"Context:\n{task.context}\n"
            f"User Prompt: {task.prompt}\n"
        )
        
        step_count = 0
        total_tokens_approx = 0
        history_len_per_step = []
        status = "failed"
        final_answer = ""
        loop_detected = False
        seen_actions = set()

        while step_count < task.max_steps:
            step_count += 1
            prompt_len = len(conversation_history)
            history_len_per_step.append(prompt_len)
            total_tokens_approx += prompt_len // 4

            response = self.generate(conversation_history)
            conversation_history += f"Assistant: {response}\n"

            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:", 1)[1].strip()
                status = "completed"
                break

            if "Action:" in response and "Action Input:" in response:
                try:
                    action_line = [l for l in response.split("\n") if l.startswith("Action:")][0]
                    tool_name = action_line.replace("Action:", "").strip()
                    
                    input_text = response.split("Action Input:", 1)[1].strip().split("\n")[0]
                    tool_args = json.loads(input_text)
                    
                    # Detect simple loop
                    action_key = f"{tool_name}:{input_text}"
                    if action_key in seen_actions:
                        loop_detected = True
                    seen_actions.add(action_key)

                    tool_output = tool_executor(tool_name, tool_args)
                    conversation_history += f"Observation: {tool_output}\n"
                except Exception as e:
                    conversation_history += f"Observation Error: {str(e)}\n"
            else:
                # Model failed to output tool action or final answer
                conversation_history += "Observation: Please output either 'Action: ...' or 'Final Answer: ...'\n"

        elapsed = time.time() - start_time
        success = (task.expected_answer.lower() in final_answer.lower()) if final_answer else False

        return {
            "mode": "naive_react",
            "task_id": task.task_id,
            "suite": task.suite,
            "status": "success" if success else ("loop_stopped" if loop_detected else status),
            "success": success,
            "steps_taken": step_count,
            "loop_detected": loop_detected,
            "final_answer": final_answer,
            "elapsed_seconds": round(elapsed, 3),
            "estimated_tokens_consumed": total_tokens_approx,
            "context_growth": history_len_per_step,
        }
