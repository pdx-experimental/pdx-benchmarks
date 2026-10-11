"""Dynamic JSON Schema Constrained Decoding for PDX SLM Benchmarks.

Provides schema-guided logits generation ensuring that:
1. The model output is strictly valid JSON conforming to the step-action contract.
2. The tool_call.name property is dynamically constrained to only the allowed tools of the current task.
3. No external natural language markdown prefixes or preambles are permitted.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

# Disable torch inductor C++ compile warnings on systems without cl.exe
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import outlines


def build_step_action_schema(allowed_tools: List[str]) -> Dict[str, Any]:
    """Build dynamic JSON schema enum-constraining tool_call.name to allowed_tools."""
    # Standardize and sort tool names
    clean_tools = sorted(list(set(str(t).strip() for t in allowed_tools if str(t).strip())))
    # Empty string is allowed when action is 'final_answer'
    tool_enum = clean_tools + [""] if clean_tools else [""]

    return {
        "type": "object",
        "properties": {
            "thought": {
                "type": "string",
                "description": "One short sentence explaining the rationale.",
            },
            "action": {
                "type": "string",
                "enum": ["execute_tool", "final_answer"],
                "description": "Action decision for this step.",
            },
            "tool_call": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "enum": tool_enum,
                        "description": "Name of tool to execute. Must be in allowed tools or empty for final_answer.",
                    },
                    "args": {
                        "type": "object",
                        "description": "Dictionary of keyword arguments for the tool.",
                    },
                },
                "required": ["name", "args"],
            },
            "answer": {
                "type": "string",
                "description": "Terminal answer string when action is final_answer.",
            },
        },
        "required": ["thought", "action", "tool_call", "answer"],
    }


class DynamicSchemaGenerator:
    """Caches and manages Outlines Generators keyed by the task's allowed tools."""

    def __init__(self, model: Any, tokenizer: Any):
        self.model = model
        self.tokenizer = tokenizer
        self.outlines_model = outlines.from_transformers(model, tokenizer)
        self._cache: Dict[str, Any] = {}

    def get_generator(self, allowed_tools: List[str]) -> Any:
        """Retrieve or compile an Outlines generator for the given toolset."""
        cache_key = json.dumps(sorted(list(set(str(t).strip() for t in allowed_tools if str(t).strip()))))
        if cache_key in self._cache:
            return self._cache[cache_key]

        schema = build_step_action_schema(allowed_tools)
        schema_spec = outlines.json_schema(schema)
        generator = outlines.Generator(self.outlines_model, output_type=schema_spec)
        self._cache[cache_key] = generator
        return generator

    def generate(
        self,
        prompt: str,
        allowed_tools: List[str],
        max_new_tokens: int = 256,
    ) -> str:
        """Generate schema-constrained text using the tool-specific generator."""
        generator = self.get_generator(allowed_tools)
        try:
            raw_output = generator(prompt, max_new_tokens=max_new_tokens)
            return str(raw_output).strip()
        except Exception as ex:
            raise RuntimeError(f"constrained_decoding_failure: {ex}") from ex
