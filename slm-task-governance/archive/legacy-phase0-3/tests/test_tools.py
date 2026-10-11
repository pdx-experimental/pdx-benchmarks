"""Unit tests for honest benchmark tools (Section 4 & Section 9 of FAIR_COMPARISON_PLAN.md)."""

import pytest
from src.tools import execute_benchmark_tool, tool_calc, tool_grep, tool_db_lookup, tool_crypto_transform, tool_json_filter


def test_calc_valid():
    res = execute_benchmark_tool("calc", {"expression": "2 + 2"})
    assert res == "4"
    res_sqrt = execute_benchmark_tool("calc", {"expression": "sqrt(144)"})
    assert res_sqrt == "12.0"


def test_calc_missing_args():
    res = execute_benchmark_tool("calc", {})
    assert "TOOL_ERROR: missing expression" in res
    res_empty = execute_benchmark_tool("calc", {"expression": ""})
    assert "TOOL_ERROR: missing expression" in res_empty


def test_calc_unsafe_rejected():
    res = execute_benchmark_tool("calc", {"expression": "__import__('os').system('ls')"})
    assert "TOOL_ERROR" in res


def test_grep_with_filler():
    context = "noise line 1\nnoise line 2\nserver node-melbourne-4 token is TRN2-SECRET-MEL-9921.\nnoise line 3"
    res = execute_benchmark_tool("grep", {"query": "node-melbourne-4"}, context=context)
    assert "server node-melbourne-4 token is TRN2-SECRET-MEL-9921." in res

    # Missing query
    res_no_q = execute_benchmark_tool("grep", {}, context=context)
    assert "TOOL_ERROR: missing query" in res_no_q

    # No match
    res_nomatch = execute_benchmark_tool("grep", {"query": "non_existent_key"}, context=context)
    assert res_nomatch == "NO_MATCH"


def test_db_lookup_exact_and_not_found():
    # Case 7 requirement: db_lookup("author") is NOT_FOUND
    res_author = execute_benchmark_tool("db_lookup", {"key": "author"})
    assert res_author == "NOT_FOUND"

    # Known key
    res_vault = execute_benchmark_tool("db_lookup", {"key": "user_819"})
    assert "UERYX0FVVEhfOTkyMQ==" in res_vault

    # Unknown key
    res_unknown = execute_benchmark_tool("db_lookup", {"key": "unknown_entity_999"})
    assert res_unknown == "NOT_FOUND"


def test_crypto_transform():
    # Base64 decode
    res_b64 = execute_benchmark_tool("crypto_transform", {"op": "b64decode", "data": "UERYX0FVVEhfOTkyMQ=="})
    assert res_b64 == "PDX_AUTH_9921"

    # SHA256 prefix
    res_sha = execute_benchmark_tool("crypto_transform", {"op": "sha256_prefix", "data": "test_string"})
    assert len(res_sha) == 8

    # Missing data
    res_err = execute_benchmark_tool("crypto_transform", {"op": "b64decode"})
    assert "TOOL_ERROR" in res_err


def test_run_python_unavailable():
    res = execute_benchmark_tool("run_python", {"code": "print(1)"})
    assert "TOOL_ERROR" in res
