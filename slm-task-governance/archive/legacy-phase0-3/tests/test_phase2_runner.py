"""Unit tests for Phase2FactorialRunner."""

import pytest
from src.runners.phase2_runner import Phase2FactorialRunner, EXEMPLAR_MESSAGES
from src.benchmark_loader import BenchmarkTask
from src.tools import execute_benchmark_tool


class MockDynamicGenerator:
    def __init__(self):
        self.called_tools = []

    def generate(self, prompt, allowed_tools, max_new_tokens=256):
        self.called_tools.append(allowed_tools)
        return '{"thought": "test", "action": "final_answer", "tool_call": {"name": "", "args": {}}, "answer": "14"}'


def test_phase2_runner_c0_anchor():
    def mock_free_fn(messages, max_tokens=256):
        assert len(messages) == 2  # system + user (Zero-shot)
        return '{"thought": "test", "action": "final_answer", "tool_call": {"name": "", "args": {}}, "answer": "14"}'

    runner = Phase2FactorialRunner(mock_free_fn, MockDynamicGenerator())
    task = BenchmarkTask(
        task_id="test_task",
        suite="gaia_l1",
        tier="level_1",
        prompt="Find 14",
        context="Data with 14",
        expected_answer="14",
        tools=[],
        pdx_steps=[{"id": "step_1", "instruction": "return 14", "depends_on": []}]
    )

    res = runner.run_task(task, "C0_anchor", execute_benchmark_tool)
    assert res["mode"] == "C0_anchor"
    assert res["final_answer"] == "14"
    assert res["invalid_outputs"] == 0
    assert res["status"] == "completed"


def test_phase2_runner_c2_oneshot_exemplar():
    step_call_messages = []

    def mock_free_fn(messages, max_tokens=256):
        assert len(messages) == 4  # system + 2 exemplar + user
        assert messages[1] == EXEMPLAR_MESSAGES[0]
        assert messages[2] == EXEMPLAR_MESSAGES[1]
        step_call_messages.append(messages)
        return '{"thought": "test", "action": "final_answer", "tool_call": {"name": "", "args": {}}, "answer": "14"}'

    runner = Phase2FactorialRunner(mock_free_fn, MockDynamicGenerator())
    task = BenchmarkTask(
        task_id="test_task",
        suite="gaia_l1",
        tier="level_1",
        prompt="Find 14",
        context="Data with 14",
        expected_answer="14",
        tools=[],
        pdx_steps=[{"id": "step_1", "instruction": "return 14", "depends_on": []}]
    )

    res = runner.run_task(task, "C2_oneshot", execute_benchmark_tool)
    assert res["mode"] == "C2_oneshot"
    assert len(step_call_messages) == 2  # step_1 + step_final



def test_phase2_runner_c1_grammar():
    mock_dyn = MockDynamicGenerator()

    def mock_free_fn(messages, max_tokens=256):
        raise RuntimeError("Should not call free_fn in grammar mode")

    runner = Phase2FactorialRunner(mock_free_fn, mock_dyn)
    task = BenchmarkTask(
        task_id="test_task",
        suite="gaia_l1",
        tier="level_1",
        prompt="Find 14",
        context="Data with 14",
        expected_answer="14",
        tools=[{"name": "calc", "description": "", "parameters": {}}],
        pdx_steps=[{"id": "step_1", "instruction": "return 14", "depends_on": []}]
    )

    res = runner.run_task(task, "C1_grammar", execute_benchmark_tool)
    assert res["mode"] == "C1_grammar"
    assert res["final_answer"] == "14"
    assert ["calc"] in mock_dyn.called_tools
