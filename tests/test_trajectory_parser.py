"""Checks for the recording-format adapters."""

import json
from pathlib import Path

import pytest
from agentevals.trajectory.match import create_trajectory_match_evaluator

from eval.trajectory_parser import TrajectoryParser

RECORDINGS = Path(__file__).parent / "sesssion_recordings"


def parse_records(tmp_path, harness, *records):
    path = tmp_path / "trace.jsonl"
    path.write_text("\n" + "\n".join(json.dumps(r) for r in records), encoding="utf-8")
    return TrajectoryParser().parse(path, harness=harness)


@pytest.mark.parametrize(
    "harness,filename,count",
    [
        ("pi", "trace_inkling.jsonl", 17),
        ("pi", "trace_gptluna.jsonl", 20),
        ("claude", "trace.jsonl", 10),
        ("codex", "trace.jsonl", 10),
    ],
)
def test_recording_tool_calls(harness, filename, count):
    messages = TrajectoryParser().parse(
        RECORDINGS / harness / filename, harness=harness
    )
    calls = [call for message in messages for call in message.get("tool_calls", [])]
    results = [
        message["tool_call_id"] for message in messages if message["role"] == "tool"
    ]
    assert len(calls) == len(results) == count
    assert [call["id"] for call in calls] == results


@pytest.mark.parametrize("harness", ["pi", "claude", "codex"])
def test_agentevals_accepts_recording(harness):
    filename = "trace_inkling.jsonl" if harness == "pi" else "trace.jsonl"
    messages = TrajectoryParser().parse(
        RECORDINGS / harness / filename, harness=harness
    )
    evaluate = create_trajectory_match_evaluator(trajectory_match_mode="strict")
    assert evaluate(outputs=messages, reference_outputs=messages)["score"] is True


def test_pi_multiple_calls(tmp_path):
    messages = parse_records(
        tmp_path,
        "pi",
        {
            "type": "message",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "internal"},
                    {"type": "text", "text": "First"},
                    {"type": "text", "text": "Second"},
                    {
                        "type": "toolCall",
                        "id": "a",
                        "name": "read",
                        "arguments": {"path": "a.py"},
                    },
                    {
                        "type": "toolCall",
                        "id": "b",
                        "name": "bash",
                        "arguments": {"command": "pytest"},
                    },
                ],
            },
        },
    )
    assert messages == [
        {
            "role": "assistant",
            "content": "First\nSecond",
            "tool_calls": [
                {
                    "id": "a",
                    "type": "function",
                    "function": {"name": "read", "arguments": '{"path": "a.py"}'},
                },
                {
                    "id": "b",
                    "type": "function",
                    "function": {"name": "bash", "arguments": '{"command": "pytest"}'},
                },
            ],
        }
    ]


def test_claude_mixed_results_and_text(tmp_path):
    messages = parse_records(
        tmp_path,
        "claude",
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Before"},
                    {"type": "tool_result", "tool_use_id": "a", "content": "Failed"},
                    {"type": "tool_result", "tool_use_id": "b"},
                    {"type": "text", "text": "After"},
                ],
            },
        },
    )
    assert messages == [
        {"role": "user", "content": "Before"},
        {"role": "tool", "tool_call_id": "a", "content": "Failed"},
        {"role": "tool", "tool_call_id": "b", "content": ""},
        {"role": "user", "content": "After"},
    ]


@pytest.mark.parametrize("custom", [False, True])
def test_codex_call_arguments(tmp_path, custom):
    item = {"call_id": "a", "name": "exec"}
    if custom:
        item.update(
            type="custom_tool_call",
            input="text(await tools.exec_command({cmd: 'pytest'}));",
        )
        expected = {"input": item["input"]}
    else:
        item.update(type="function_call", arguments='{"cmd": "pytest"}')
        expected = {"cmd": "pytest"}
    messages = parse_records(
        tmp_path, "codex", {"type": "response_item", "payload": item}
    )
    call = messages[0]["tool_calls"][0]
    assert call["id"] == "a"
    assert json.loads(call["function"]["arguments"]) == expected


def test_codex_function_result(tmp_path):
    messages = parse_records(
        tmp_path,
        "codex",
        {
            "type": "response_item",
            "payload": {
                "type": "function_call_output",
                "call_id": "a",
                "output": "1 failed",
            },
        },
    )
    assert messages == [{"role": "tool", "tool_call_id": "a", "content": "1 failed"}]


@pytest.mark.parametrize(
    "harness,record",
    [
        ("codex", {"type": "response_item", "payload": {"type": "unknown_call"}}),
        (
            "pi",
            {
                "type": "message",
                "message": {"role": "user", "content": [{"type": "image"}]},
            },
        ),
        ("claude", {"type": "assistant"}),
    ],
)
def test_unsupported_records_have_location(tmp_path, harness, record):
    with pytest.raises(ValueError, match=r"trace.jsonl:2:"):
        parse_records(tmp_path, harness, record)


def test_invalid_json_has_location(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match=r"broken.jsonl:1:"):
        TrajectoryParser().parse(path, harness="pi")


def test_unknown_harness(tmp_path):
    with pytest.raises(ValueError, match="Unsupported harness"):
        TrajectoryParser().parse(tmp_path / "unused", harness="other")
