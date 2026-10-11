"""Unit tests for runner fallback, execution invariants, and prompt isolation.

Strictly verifies Section 9 of FAIR_COMPARISON_PLAN.md:
1. Mock LLM returns "" -> executor.call_count == 0 in both runners.
2. Mock LLM returns valid execute_tool with calc / expression=2+2 -> observation 4.
3. Mock LLM returns execute_tool with empty args -> executor.call_count == 0 (no calc of gold instruction).
4. Isolated runner prompt for step 2 contains parent artifact and DOES NOT contain step 1 assistant JSON.
5. React runner prompt for step 2 DOES contain step 1 assistant JSON.
"""

from unittest.mock import MagicMock
import json
import pytest

from src.benchmark_loader import BenchmarkTask
from src.runners.goldplan_react import GoldPlanReActRunner
from src.runners.goldplan_isolated import GoldPlanIsolatedRunner


@pytest.fixture
def sample_task():
    return BenchmarkTask(
        task_id="test_calc_task",
        suite="gaia_l1",
        tier="level_1",
        prompt="Calculate 2 + 2.",
        context="Sample test context.",
        tools=[{"name": "calc"}],
        expected_answer="4",
        pdx_steps=[
            {"id": "step_1_calc", "kind": "tool", "tool": "calc", "instruction": "Compute 2 + 2", "depends_on": []},
        ],
        max_steps=3,
    )


@pytest.fixture
def two_step_task():
    return BenchmarkTask(
        task_id="test_two_step_task",
        suite="dag_chain",
        tier="level_2",
        prompt="Step 1 and Step 2.",
        context="Two step context.",
        tools=[{"name": "calc"}],
        expected_answer="42",
        pdx_steps=[
            {"id": "step_1", "kind": "tool", "tool": "calc", "instruction": "Compute 40 + 2", "depends_on": []},
            {"id": "step_2", "kind": "tool", "tool": "calc", "instruction": "Verify result", "depends_on": ["step_1"]},
        ],
        max_steps=4,
    )


def test_empty_generation_never_calls_executor(sample_task):
    """Case 1: Mock LLM returns '' -> executor.call_count == 0 in both runners."""
    mock_llm = MagicMock(return_value="")
    mock_executor = MagicMock()

    # ReAct runner
    react_runner = GoldPlanReActRunner(generate_chat_fn=mock_llm)
    res_react = react_runner.run_task(sample_task, mock_executor, max_steps=2)
    assert mock_executor.call_count == 0
    assert res_react["empty_generations"] > 0

    # Isolated runner
    mock_llm.reset_mock()
    mock_executor.reset_mock()
    isolated_runner = GoldPlanIsolatedRunner(generate_chat_fn=mock_llm)
    res_iso = isolated_runner.run_task(sample_task, mock_executor, max_steps=2)
    assert mock_executor.call_count == 0
    assert res_iso["empty_generations"] > 0


def test_valid_execute_tool_calls_executor(sample_task):
    """Case 2: Mock LLM returns valid execute_tool with calc / expression=2+2 -> observation 4."""
    valid_tool_response = json.dumps({
        "thought": "Calculating 2+2",
        "action": "execute_tool",
        "tool_call": {"name": "calc", "args": {"expression": "2 + 2"}},
        "answer": ""
    })
    final_answer_response = json.dumps({
        "thought": "Finished calculation",
        "action": "final_answer",
        "tool_call": {"name": "", "args": {}},
        "answer": "4"
    })

    mock_llm = MagicMock(side_effect=[valid_tool_response, final_answer_response])
    mock_executor = MagicMock(return_value="4")

    react_runner = GoldPlanReActRunner(generate_chat_fn=mock_llm)
    res = react_runner.run_task(sample_task, mock_executor)
    
    assert mock_executor.call_count == 1
    mock_executor.assert_called_with("calc", {"expression": "2 + 2"}, sample_task.context)
    assert res["final_answer"] == "4"


def test_empty_tool_args_never_calls_executor(sample_task):
    """Case 3: Mock LLM returns execute_tool with empty args -> no calc of gold instruction."""
    bad_tool_response = json.dumps({
        "thought": "Calling calc with empty args",
        "action": "execute_tool",
        "tool_call": {"name": "calc", "args": {}},
        "answer": ""
    })

    mock_llm = MagicMock(return_value=bad_tool_response)
    mock_executor = MagicMock()

    react_runner = GoldPlanReActRunner(generate_chat_fn=mock_llm)
    res_react = react_runner.run_task(sample_task, mock_executor, max_steps=2)
    assert mock_executor.call_count == 0
    assert res_react["invalid_outputs"] > 0

    mock_llm.reset_mock()
    mock_executor.reset_mock()
    isolated_runner = GoldPlanIsolatedRunner(generate_chat_fn=mock_llm)
    res_iso = isolated_runner.run_task(sample_task, mock_executor, max_steps=2)
    assert mock_executor.call_count == 0
    assert res_iso["invalid_outputs"] > 0


def test_isolated_prompt_isolation_vs_react(two_step_task):
    """Cases 4 & 5:
    Isolated runner prompt for step 2 contains parent artifact and DOES NOT contain step 1 assistant JSON.
    React runner prompt for step 2 DOES contain step 1 assistant JSON.
    """
    step1_response = json.dumps({
        "thought": "Step 1 compute",
        "action": "execute_tool",
        "tool_call": {"name": "calc", "args": {"expression": "40 + 2"}},
        "answer": ""
    })
    step2_response = json.dumps({
        "thought": "Step 2 done",
        "action": "final_answer",
        "tool_call": {"name": "", "args": {}},
        "answer": "42"
    })

    # 1. Test Isolated Runner
    captured_isolated_prompts = []
    def capture_iso_llm(messages, max_tokens):
        captured_isolated_prompts.append([m["content"] for m in messages])
        if len(captured_isolated_prompts) == 1:
            return step1_response
        return step2_response

    mock_executor = MagicMock(return_value="42")
    iso_runner = GoldPlanIsolatedRunner(generate_chat_fn=capture_iso_llm)
    iso_runner.run_task(two_step_task, mock_executor)

    # Step 2 messages in isolated runner
    step2_iso_messages = captured_isolated_prompts[1]
    step2_iso_text = " ".join(step2_iso_messages)
    # Must contain parent artifact '42'
    assert "artifact='42'" in step2_iso_text or "42" in step2_iso_text
    # Must NOT contain step 1 assistant JSON!
    assert step1_response not in step2_iso_text

    # 2. Test ReAct Runner
    captured_react_prompts = []
    def capture_react_llm(messages, max_tokens):
        captured_react_prompts.append([m["content"] for m in messages])
        if len(captured_react_prompts) == 1:
            return step1_response
        return step2_response

    react_runner = GoldPlanReActRunner(generate_chat_fn=capture_react_llm)
    react_runner.run_task(two_step_task, mock_executor)

    # Turn 2 messages in react runner
    turn2_react_messages = captured_react_prompts[1]
    turn2_react_text = " ".join(turn2_react_messages)
    # Must contain step 1 assistant JSON!
    assert step1_response in turn2_react_text
