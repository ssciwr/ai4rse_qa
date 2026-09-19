"""Verify required calls in recorded bugfix workflows."""

import json
from pathlib import Path

import pytest
from agentevals.trajectory.match import create_trajectory_match_evaluator

from eval.trajectory_parser import TrajectoryParser

RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]


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


@pytest.fixture(scope="class", params=CASES)
def read_trajectory(request):
    path, harness = request.param
    return TrajectoryParser().parse(path, harness=harness)


class TestBugfixesWorkflow:
    def test_trajectory_reads_bugfixes_skill(self, read_trajectory):

        for line in read_trajectory:
            print(line)
        assert 3 == 5

    def test_trajectory_reads_sourcecode(self, read_trajectory):
        assert 3 == 5

    def test_trajectory_writes_plan(self, read_trajectory):
        assert 3 == 5

    def test_trajectory_writes_regression_test(self, read_trajectory):
        assert 3 == 5

    # test invariants
    def test_trajectory_adheres_to_human_gate(self, read_trajectory):
        assert 3 == 5

    def test_trajectory_does_not_change_lib_code_before_approval(self, read_trajectory):
        assert 3 == 5
