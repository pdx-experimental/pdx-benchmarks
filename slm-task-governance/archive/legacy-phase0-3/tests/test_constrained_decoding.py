"""Unit tests for Dynamic JSON Schema Constrained Decoding."""

import json
import pytest
from src.constrained_decoding import build_step_action_schema, DynamicSchemaGenerator
from transformers import AutoModelForCausalLM, AutoTokenizer


def test_build_step_action_schema_enums():
    tools = ["calc", "grep"]
    schema = build_step_action_schema(tools)

    assert schema["type"] == "object"
    assert "thought" in schema["required"]
    assert "action" in schema["required"]
    assert "tool_call" in schema["required"]
    assert "answer" in schema["required"]

    name_prop = schema["properties"]["tool_call"]["properties"]["name"]
    assert "calc" in name_prop["enum"]
    assert "grep" in name_prop["enum"]
    assert "" in name_prop["enum"]
    assert len(name_prop["enum"]) == 3


def test_build_step_action_schema_empty_tools():
    schema = build_step_action_schema([])
    name_prop = schema["properties"]["tool_call"]["properties"]["name"]
    assert name_prop["enum"] == [""]


def test_dynamic_schema_generator_execution():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    # Use cached Qwen 1.5B tokenizer with tiny model or test generation
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-1.5B-Instruct")
    model = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2")
    schema_gen = DynamicSchemaGenerator(model, tokenizer)

    tools = ["calc", "grep"]
    prompt = "Task prompt:"

    # Verify generator caching and creation
    gen1 = schema_gen.get_generator(tools)
    gen2 = schema_gen.get_generator(["calc", "grep"])
    assert gen1 is gen2

    schema = build_step_action_schema(tools)
    assert schema["properties"]["tool_call"]["properties"]["name"]["enum"] == ["calc", "grep", ""]

