"""Verify required calls in recorded bugfix workflows."""

import json
from pathlib import Path

import pytest
from agentevals.trajectory.match import create_trajectory_match_evaluator

from eval.trajectory_parser import TrajectoryParser

RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"


# little helper to build the reference trajectory steps.
# openai's message format expects tool call args to be represented as strings
def _call(call_id, name, arguments):
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


# This is intentionally a partial reference. Superset matching permits all of
# the investigation and other incidental calls in the recorded trajectory.
BUGFIX_REFERENCE_OUTPUTS = [
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            _call("skill", "Skill", {"skill": "bugfixing"}),
            # _call("red", "Bash", {"workflow_step": "regression_test_red"}),
            # _call("plan", "Bash", {"workflow_step": "plan_written"}),
            # _call("implementation", "Edit", {"workflow_step": "implementation"}),
            # _call("verification", "Bash", {"workflow_step": "verification"}),
        ],
    }
]


# TODO: this is dogshit crap!
def _matches_bash_step(actual, reference):
    command = actual.get("command", "")

    # this is far too specific! not useful!
    required_fragments = {
        "regression_test_red": ("tests/test_lotka.py", "open(p,'w').write", "pytest"),
        "plan_written": ("cat > bugfix-plan.md",),
        "verification": ("uv run --extra tests pytest", "--cov-branch"),
    }.get(reference.get("workflow_step"))
    return required_fragments is not None and all(
        fragment in command for fragment in required_fragments
    )


def _matches_implementation(actual, reference):
    return (
        reference.get("workflow_step") == "implementation"
        and actual.get("file_path", "").endswith("src/qa/lotka.py")
        and actual.get("new_string") == "delta=args.delta,"
    )


@pytest.mark.parametrize(
    "trajectory,harness",
    [
        (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
        (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
        (RECORDINGS / "claude" / "trace.jsonl", "claude"),
        (RECORDINGS / "codex" / "trace.jsonl", "codex"),
    ],
)
def test_trajectory_contains_required_bugfix_calls(trajectory, harness):
    trajectory = TrajectoryParser().parse(trajectory, harness=harness)
    evaluate = create_trajectory_match_evaluator(
        trajectory_match_mode="superset",
        tool_args_match_overrides={
            "Bash": _matches_bash_step,
            "Edit": _matches_implementation,
        },
    )

    result = evaluate(
        outputs=trajectory,
        reference_outputs=BUGFIX_REFERENCE_OUTPUTS,
    )

    assert result["score"] is True


# TODO: add test for invariants of the workflow
# TODO:
