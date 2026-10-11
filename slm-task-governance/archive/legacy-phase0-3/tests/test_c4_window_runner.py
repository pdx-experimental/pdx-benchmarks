"""Unit tests for C4 Leaf-Worker Context Window Runner and Windowing Algorithms."""

import pytest
from src.runners.c4_window_runner import (
    extract_instruction_keywords,
    build_head_window,
    build_keyword_window,
    C4WindowRunner,
)
from src.benchmark_loader import load_benchmark_suite
from src.tools import execute_benchmark_tool
from src.scoring import score_answer


def test_extract_instruction_keywords():
    instr = "Search for token assigned to node-melbourne-4 in context"
    kws = extract_instruction_keywords(instr)
    assert "node-melbourne-4" in kws
    assert "token" in kws
    assert "search" not in kws
    assert "for" not in kws

    # Multi-hop parent artifact incorporation
    instr2 = "Search for decryption key matching session_id"
    kws2 = extract_instruction_keywords(instr2, parent_artifacts=["SESSION_OMEGA_882"])
    assert "SESSION_OMEGA_882" in kws2
    assert "decryption" in kws2


def test_build_head_window():
    text = "A" * 5000
    w = build_head_window(text, max_chars=2000)
    assert len(w) == 2000
    assert w == "A" * 2000

    short_text = "Hello world"
    assert build_head_window(short_text, max_chars=2000) == "Hello world"


def test_build_keyword_window_length_invariant():
    tasks = load_benchmark_suite()
    ruler_tasks = [t for t in tasks if "ruler" in t.suite]
    assert len(ruler_tasks) == 21

    for t in ruler_tasks:
        for s in t.pdx_steps:
            kws = extract_instruction_keywords(s.get("instruction", ""), task_prompt=t.prompt)
            w = build_keyword_window(t.context, kws, max_chars=2000)
            assert len(w) <= 2000, f"Task {t.task_id} step {s['id']} window exceeded 2000 chars: {len(w)}"


def test_ruler_head_vs_keyword_separation():
    """Verify that head_2k does NOT contain needles, but keyword_2k captures them on Level 1 tasks."""
    tasks = load_benchmark_suite()
    ruler_l1 = [t for t in tasks if t.suite == "ruler_l1" and "needle" in t.task_id]

    head_hits = 0
    kw_hits = 0
    for t in ruler_l1:
        exp = t.expected_answer.lower()
        head_w = build_head_window(t.context, 2000).lower()
        if exp in head_w:
            head_hits += 1

        kws = extract_instruction_keywords(t.pdx_steps[0].get("instruction", ""), task_prompt=t.prompt)
        kw_w = build_keyword_window(t.context, kws, 2000).lower()
        if exp in kw_w:
            kw_hits += 1

    # In 100% of needle tasks, needle is not in head 2k
    assert head_hits == 0
    # In keyword window, needle should be successfully captured
    assert kw_hits >= 6


def test_c4_window_runner_mock_execution():
    tasks = load_benchmark_suite()
    task = [t for t in tasks if t.task_id == "ruler_01_needle_4k"][0]

    # Mock generator that emits grep call on step 1, final_answer on step 2
    def mock_generate(messages, max_tokens=256):
        prompt_text = messages[-1]["content"]
        if "Current Step: step_1_grep" in prompt_text:
            return '{"thought": "search", "action": "execute_tool", "tool_call": {"name": "grep", "args": {"query": "node-melbourne-4"}}, "answer": ""}'
        else:
            return '{"thought": "answer", "action": "final_answer", "tool_call": null, "answer": "TRN2-SECRET-MEL-9921"}'

    runner = C4WindowRunner(generate_free_fn=mock_generate)

    # Test under W0_full
    rec_full = runner.run_task(task, "W0_full", execute_benchmark_tool, model_name="mock_model")
    assert rec_full["status"] == "completed"
    assert rec_full["steps_taken"] == 2
    assert rec_full["final_answer"] == "TRN2-SECRET-MEL-9921"
    res_full = score_answer(rec_full["final_answer"], task.expected_answer)
    assert res_full[0] is True

    # Test under W2_keyword_2k
    rec_kw = runner.run_task(task, "W2_keyword_2k", execute_benchmark_tool, model_name="mock_model")
    assert rec_kw["status"] == "completed"
    assert rec_kw["steps_taken"] == 2
    assert rec_kw["final_answer"] == "TRN2-SECRET-MEL-9921"
    res_kw = score_answer(rec_kw["final_answer"], task.expected_answer)
    assert res_kw[0] is True
