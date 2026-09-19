from collections.abc import Callable
from pathlib import Path

import pytest
from openevals import create_trajectory_match_evaluator

from eval_harness.trajectory_parser import TrajectoryParser
from tests.test_trajectory_reads_bugfixing_skill import BUGFIX_REFERENCE_OUTPUTS
from tests.test_trajectory_reads_sourcecode import SOURCECODE_REFERENCE_OUTPUTS
from tests.test_trajectory_writes_plan import PLAN_REFERENCE_OUTPUTS
from tests.test_trajectory_writes_regression_test import (
    REGRESSION_TEST_REFERENCE_OUTPUTS,
)


RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]


class ToolArgsMatcher:
    def __init__(self, function: Callable[[dict, dict], bool]):
        self.function = function

    def __call__(self, output, reference_pattern):
        return self.function(output, reference_pattern)


@pytest.mark.parametrize("path,harness", CASES)
def test_trajectory_all_tool_calls(path, harness):
    trajectory = TrajectoryParser().parse(path, harness=harness)
    if path.name == "trace_inkling.jsonl":
        reference = (
            BUGFIX_REFERENCE_OUTPUTS[harness]
            + SOURCECODE_REFERENCE_OUTPUTS[harness]
            + PLAN_REFERENCE_OUTPUTS[harness]
            + REGRESSION_TEST_REFERENCE_OUTPUTS[harness]
        )
    else:
        reference = (
            BUGFIX_REFERENCE_OUTPUTS[harness]
            + SOURCECODE_REFERENCE_OUTPUTS[harness]
            + REGRESSION_TEST_REFERENCE_OUTPUTS[harness]
            + PLAN_REFERENCE_OUTPUTS[harness]
        )

    evaluator = create_trajectory_match_evaluator(
        trajectory_match_mode="superset",
        tool_args_match_overrides={
            "read": ToolArgsMatcher(
                lambda out, ref: ref["path"] in out.get("path", "")
            ),
            "write": ToolArgsMatcher(
                lambda out, ref: ref["path"] in out.get("path", "")
            ),
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
