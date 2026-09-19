from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ToolCorrectnessMetric
from deepeval import evaluate
import pytest
from pathlib import Path
import json
from eval_harness.trajectory_parser import TrajectoryParser


# GET TRACES.
# in reality, these might come from a reader function, or from an
# on-the-fly eval
RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]

# HARNESS SPECIFIC REFERENCES
# We need to define per-harness references because their tool names and semantics
# are a bit different.
# This is intentionally a partial reference. Superset matching (see below) permits all of
# the investigation and other incidental calls in the recorded trajectory.
BUGFIX_REFERENCE_OUTPUTS = {}

BUGFIX_REFERENCE_OUTPUTS["claude"] = [
    # skill reading
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
            },
        ],
    },
    # skill content is actually used
    {
        "role": "tool",
        "tool_call_id": "skill",
        "content": "Launching skill: bugfixing",
    },
]

BUGFIX_REFERENCE_OUTPUTS["codex"] = [
    # skill reading
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
            },
        ],
    },
    # skill content is actually in context
    {
        "role": "tool",
        "tool_call_id": "skill",
        "content": (
            "Bugfix workflow. Use when the user asks to fix a defect with "
            "evidence, tests, a plan approval gate, and reviewer critique "
            "before handoff."
        ),
    },
]

BUGFIX_REFERENCE_OUTPUTS["pi"] = [
    # skill reading
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
            },
        ],
    },
    # skill content is actually in context
    {
        "role": "tool",
        "tool_call_id": "skill",
        "content": (
            "Bugfix workflow. Use when the user asks to fix a defect with "
            "evidence, tests, a plan approval gate, and reviewer critique "
            "before handoff."
        ),
    },
]


@pytest.mark.parametrize("path, harness", CASES)
class TestBugfixesWorkflow:
    # Our first test case checks that the 'bugfixes' skill is read.
    # We check this by:
    # - checking that the bugfixes skill is accessed
    # - checking that the bugfixes skill's description is appearing in the context,
    #   or, in the case of claude, that 'Launching skill: bugfixing' appears in the context.
    def test_trajectory_reads_bugfixes_skill(self, path, harness):

        # get trajectory and reference
        trajectory = TrajectoryParser().parse(path, harness=harness)

        reference = BUGFIX_REFERENCE_OUTPUTS[harness]

    def test_trajectory_reads_sourcecode(self, path, harness):
        # get the actual trajectory, and the reference trajectory we need
        trajectory = TrajectoryParser().parse(path, harness=harness)

        reference = BUGFIX_REFERENCE_OUTPUTS[harness]

    def test_trajectory_writes_plan(self, path, harness):
        # get the actual trajectory, and the reference trajectory we need
        trajectory = TrajectoryParser().parse(path, harness=harness)

        reference = BUGFIX_REFERENCE_OUTPUTS[harness]

    def test_trajectory_writes_regression_test(self, path, harness):
        # get the actual trajectory, and the reference trajectory we need
        trajectory = TrajectoryParser().parse(path, harness=harness)

        reference = BUGFIX_REFERENCE_OUTPUTS[harness]

    # test invariants
    def test_trajectory_adheres_to_human_gate(self, path, harness):
        # get the actual trajectory, and the reference trajectory we need
        trajectory = TrajectoryParser().parse(path, harness=harness)

        reference = BUGFIX_REFERENCE_OUTPUTS[harness]

    def test_trajectory_does_not_change_lib_code_before_approval(self, path, harness):
        # get the actual trajectory, and the reference trajectory we need
        trajectory = TrajectoryParser().parse(path, harness=harness)

        reference = BUGFIX_REFERENCE_OUTPUTS[harness]
