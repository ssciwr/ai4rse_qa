import json
from pathlib import Path

import pytest
from openevals import create_trajectory_match_evaluator

from eval_harness.tools_args_matcher import ToolArgsMatcher
from eval_harness.trajectory_parser import TrajectoryParser


RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]

PLAN_REFERENCE_OUTPUTS = {
    "pi": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "plan",
                    "type": "function",
                    "function": {
                        "name": "write",
                        "arguments": json.dumps({"path": "bugfix-plan.md"}),
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
                    "id": "plan",
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "arguments": json.dumps(
                            {"command": "cat > bugfix-plan.md"}
                        ),
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
                    "id": "plan",
                    "type": "function",
                    "function": {
                        "name": "exec",
                        "arguments": json.dumps(
                            {
                                "input": "*** Add File: ./ai4rse_qa/bugfix-plan.md"
                            }
                        ),
                    },
                }
            ],
        }
    ],
}


@pytest.mark.parametrize("path,harness", CASES)
def test_trajectory_writes_plan(path, harness):
    trajectory = TrajectoryParser().parse(path, harness=harness)
    reference = PLAN_REFERENCE_OUTPUTS[harness]
    evaluator = create_trajectory_match_evaluator(
        trajectory_match_mode="superset",
        tool_args_match_overrides={
            "write": ToolArgsMatcher(
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
