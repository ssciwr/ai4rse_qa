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
                        "name": """TODO: WHAT SHOULD GO HERE?""",
                        "arguments": json.dumps(
                            {"path": """TODO: WHAT SHOULD GO HERE?"""}
                        ),
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
                        "arguments": json.dumps(
                            {"command": """TODO: WHAT SHOULD GO HERE?"""}
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
                    "id": "source",
                    "type": "function",
                    "function": {
                        "name": "exec",
                        "arguments": json.dumps(
                            {"input": """TODO: WHAT SHOULD GO HERE?"""}
                        ),
                    },
                }
            ],
        }
    ],
}


@pytest.mark.parametrize("path,harness", CASES)
def test_trajectory_reads_sourcecode(path, harness):
    trajectory = TrajectoryParser().parse(path, harness=harness)
    reference = SOURCECODE_REFERENCE_OUTPUTS[harness]
    evaluator = create_trajectory_match_evaluator("""TODO: WHAT SHOULD GO HERE?""")

    result = evaluator(outputs=trajectory, reference_outputs=reference)
    print(result)
    assert result["score"]
