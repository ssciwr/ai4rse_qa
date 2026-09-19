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

REGRESSION_TEST_REFERENCE_OUTPUTS = {
    "pi": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "regression-test",
                    "type": "function",
                    "function": {
                        "name": "edit",
                        "arguments": json.dumps({"path": "tests/test_lotka.py"}),
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
                    "id": "regression-test",
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "arguments": json.dumps(
                            {
                                "command": "test_cli_passes_delta_argument_to_solver"
                            }
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
                    "id": "regression-test",
                    "type": "function",
                    "function": {
                        "name": "exec",
                        "arguments": json.dumps(
                            {
                                "input": "*** Update File: ./ai4rse_qa/tests/test_lotka.py"
                            }
                        ),
                    },
                }
            ],
        }
    ],
}


@pytest.mark.parametrize("path,harness", CASES)
def test_trajectory_writes_regression_test(path, harness):
    trajectory = TrajectoryParser().parse(path, harness=harness)
    reference = REGRESSION_TEST_REFERENCE_OUTPUTS[harness]
    evaluator = create_trajectory_match_evaluator(
        trajectory_match_mode="superset",
        tool_args_match_overrides={
            "edit": ToolArgsMatcher(
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
