from openevals import create_trajectory_llm_as_judge
from openevals.prompts import TRAJECTORY_ACCURACY_PROMPT
import json
from pathlib import Path
import os
import pytest

RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
CASES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]
