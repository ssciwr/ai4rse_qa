import json
from collections.abc import Callable
from pathlib import Path

import pytest
from openevals import create_trajectory_match_evaluator

from eval_harness.trajectory_parser import TrajectoryParser


RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]

SOURCECODE_REFERENCE_OUTPUTS = {
    "pi": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "source",
                    "type": "function",
                    "function": {
                        "name": "read",
                        "arguments": json.dumps({"path": "src/qa/lotka.py"}),
                    },
                }
            ],
        }
    ],
    "claude": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "source",
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "arguments": json.dumps({"command": "src/qa/lotka.py"}),
                    },
                }
            ],
        }
    ],
    "codex": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "source",
                    "type": "function",
                    "function": {
                        "name": "exec",
                        "arguments": json.dumps({"input": "src/qa/lotka.py"}),
                    },
                }
            ],
        }
    ],
}


class ToolArgsMatcher:
    def __init__(self, function: Callable[[dict, dict], bool]):
        self.function = function

    def __call__(self, output, reference_pattern):
        return self.function(output, reference_pattern)


@pytest.mark.parametrize("path,harness", CASES)
def test_trajectory_reads_sourcecode(path, harness):
    trajectory = TrajectoryParser().parse(path, harness=harness)
    reference = SOURCECODE_REFERENCE_OUTPUTS[harness]
    evaluator = create_trajectory_match_evaluator(
        trajectory_match_mode="superset",
        tool_args_match_overrides={
            "read": ToolArgsMatcher(
                lambda out, ref: ref["path"] in out.get("path", "")
            ),
            "Bash": ToolArgsMatcher(
                lambda out, ref: ref["command"] in out.get("command", "")
            ),
            "exec": ToolArgsMatcher(
                lambda out, ref: ref["input"] in out.get("input", "")
            ),
        },
    )

    result = evaluator(outputs=trajectory, reference_outputs=reference)

    assert result["score"]
