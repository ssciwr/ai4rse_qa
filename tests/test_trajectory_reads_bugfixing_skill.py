import json
from pathlib import Path

import pytest
from openevals import create_trajectory_match_evaluator

from eval_harness.tools_args_matcher import ToolArgsMatcher
from eval_harness.trajectory_parser import TrajectoryParser

# get the recorded traces. here we don't use a reader function
# because we only have those few.
RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]

# build reference outputs. We define harness specific step
# definitions that show how a successful 'skill has been loaded'
# step can look like.
# This is written in the specific trace format (openAI messages) that the langchain
# openevals library wants
BUGFIX_REFERENCE_OUTPUTS = {
    "claude": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "skill",
                    "type": "function",
                    "function": {
                        "name": "Skill",
                        "arguments": json.dumps({"skill": "bugfixing"}),
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
                    "id": "skill",
                    "type": "function",
                    "function": {
                        "name": "exec",
                        "arguments": json.dumps(
                            {"input": ".codex/skills/bugfixing/SKILL.md"}
                        ),
                    },
                }
            ],
        }
    ],
    "pi": [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "skill",
                    "type": "function",
                    "function": {
                        "name": "read",
                        "arguments": json.dumps(
                            {"path": "./ai4rse_qa/.pi/skills/bugfixing/SKILL.md"}
                        ),
                    },
                }
            ],
        }
    ],
}


@pytest.mark.parametrize("path,harness", CASES)
def test_trajectory_reads_bugfixing_skill(path, harness):
    trajectory = TrajectoryParser().parse(path, harness=harness)
    reference = BUGFIX_REFERENCE_OUTPUTS[harness]
    evaluator = create_trajectory_match_evaluator(
        trajectory_match_mode="superset",
        tool_args_match_mode="superset",
        tool_args_match_overrides={
            "exec": ToolArgsMatcher(
                lambda out, ref: ref["input"] in out.get("input", "")
            )
        },
    )

    result = evaluator(outputs=trajectory, reference_outputs=reference)
    if not isinstance(result, dict):
        pytest.fail(
            f"Expected evaluator result to be a dict, got {type(result).__name__}"
        )

    assert result["score"]
