"""Honest Benchmark Tool Environment for Fair SLM Evaluation.

Strictly follows Section 4 of FAIR_COMPARISON_PLAN.md:
- No gold fallbacks.
- Operates only on explicit model-provided arguments.
- Rejects missing or invalid parameters with TOOL_ERROR.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import re
from typing import Any, Dict, Optional


FIXTURE_DB: Dict[str, str] = {
    "user_819": json.dumps({"encrypted_token": "UERYX0FVVEhfOTkyMQ==", "cipher": "base64"}),
    "cl_alpha": json.dumps({"latencies_ms": [120, 150, 135, 160, 145]}),
    "SKU_9021": json.dumps({"stock": 45, "target": 100, "batch_size": 20}),
    "pkg_linux_x64": json.dumps({"cas_hash": "a8f9c1e0992", "status": "verified", "merkle_root": "ROOT_MERKLE_OK"}),
    "PRODOCUX_SPEC_V2": json.dumps({"author": "Ada Lovelace", "status": "approved"}),
    "asset_list": json.dumps(["asset_1012", "asset_4402", "asset_9918", "asset_3301", "asset_9918"]),
    "telemetry_services": json.dumps({"auth": 45, "db": 120, "image_embedder": 890, "cache": 5}),
    "endpoint_export": json.dumps({"required_role": "admin"}),
    "pkg_c": json.dumps({"prerequisite": "pkg_b", "root_prerequisite": "pkg_a"}),
    "server_port": json.dumps({"host": "0.0.0.0", "port": 8080}),
}


def tool_calc(args: Dict[str, Any]) -> str:
    expr = args.get("expression") or args.get("expr")
    if not expr or not isinstance(expr, str) or not expr.strip():
        return "TOOL_ERROR: missing expression"
    
    expr = expr.strip()
    # Check for safe characters: digits, basic operators, parens, decimal, sqrt, whitespace, comma
    safe_pattern = re.compile(r"^[0-9\+\-\*\/\%\(\)\.\,\s]|sqrt$")
    cleaned = expr.replace("sqrt", "").replace("math.", "")
    if not all(c in "0123456789+-*/%()., \t\n" for c in cleaned):
        return "TOOL_ERROR: unsafe expression"
    
    try:
        # Evaluate in restricted environment with math.sqrt and ceil
        safe_env = {
            "__builtins__": None,
            "sqrt": math.sqrt,
            "ceil": math.ceil,
            "floor": math.floor,
        }
        res = eval(expr, safe_env)
        return str(res)
    except Exception as exc:
        return f"TOOL_ERROR: eval failed: {exc}"


def tool_grep(args: Dict[str, Any], context: str) -> str:
    query = args.get("query")
    if not query or not isinstance(query, str) or not query.strip():
        return "TOOL_ERROR: missing query"
    
    q = query.strip()
    lines = context.splitlines()
    matches = [line for line in lines if q in line]
    if not matches:
        return "NO_MATCH"
    return "\n".join(matches[:5])


def tool_db_lookup(args: Dict[str, Any]) -> str:
    key = args.get("key") or args.get("query") or args.get("id") or args.get("name")
    if not key or not isinstance(key, str) or not key.strip():
        return "TOOL_ERROR: missing key"
    
    k = key.strip()
    # Exact key match only - no author heuristic fallback
    if k in FIXTURE_DB:
        return FIXTURE_DB[k]
    return "NOT_FOUND"


def tool_crypto_transform(args: Dict[str, Any]) -> str:
    op = args.get("op")
    data = args.get("data")
    if not op:
        return "TOOL_ERROR: missing op"
    if data is None:
        return "TOOL_ERROR: missing data"
    
    data_str = str(data).strip()
    if op == "b64decode":
        try:
            # Handle potential padding issues
            pad = len(data_str) % 4
            if pad != 0:
                data_str += "=" * (4 - pad)
            decoded = base64.b64decode(data_str.encode("utf-8")).decode("utf-8", errors="replace")
            return decoded
        except Exception as exc:
            return f"TOOL_ERROR: decode failed: {exc}"
    elif op == "sha256_prefix":
        digest = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        return digest[:8]
    else:
        return f"TOOL_ERROR: unsupported op '{op}'"


def tool_json_filter(args: Dict[str, Any]) -> str:
    json_input = args.get("json") or args.get("data")
    predicate = args.get("predicate") or args.get("query") or args.get("key")
    if not json_input:
        return "TOOL_ERROR: missing json"
    
    try:
        parsed = json.loads(json_input) if isinstance(json_input, str) else json_input
    except Exception as exc:
        return f"TOOL_ERROR: invalid json: {exc}"
    
    if not predicate:
        return json.dumps(parsed)
    
    pred = str(predicate).strip()
    if isinstance(parsed, dict):
        if pred in parsed:
            return str(parsed[pred])
        return "NOT_FOUND"
    elif isinstance(parsed, list):
        filtered = [item for item in parsed if pred in str(item)]
        return json.dumps(filtered)
    return str(parsed)


def execute_benchmark_tool(tool_name: str, args: Dict[str, Any], context: str = "") -> str:
    """Entrypoint for tool execution. Never falls back to gold answers."""
    if not isinstance(args, dict):
        return "TOOL_ERROR: args must be a dictionary"
    
    if tool_name == "calc":
        return tool_calc(args)
    elif tool_name == "grep":
        return tool_grep(args, context)
    elif tool_name == "db_lookup":
        return tool_db_lookup(args)
    elif tool_name == "crypto_transform":
        return tool_crypto_transform(args)
    elif tool_name == "json_filter":
        return tool_json_filter(args)
    elif tool_name == "run_python":
        return "TOOL_ERROR: run_python is not available"
    else:
        return f"TOOL_ERROR: unknown tool '{tool_name}'"
