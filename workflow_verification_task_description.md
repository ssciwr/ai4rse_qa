# Workflow verification - Example task

## Setup
- The definition of the differential equations to be solved is already there, see `src/qa/lotka.py`

- You need a working python installation.
    - make a virtual environment:
        - raw Python: `python3 -m venv ./.venv`
        - uv: `uv venv ./.venv`
        - PowerShell: `py -m venv .venv`
        - conda: `conda create -n venv`

    - activate the venv
        - raw Python: `source .venv/bin/activate`
        - uv: `source .venv/bin/activate`
        - PowerShell: `.\.venv\Scripts\Activate.ps1`
        - conda: `conda activate venv`

    - install the current project in 'editable' mode, together with its dependencies:
        - raw Python: `python -m pip install -e ".[tests]"`
        - uv: `uv sync --extra tests`
        - PowerShell: `python -m pip install -e ".[tests]"`
        - conda: `python -m pip install -e ".[tests]"`

    - how to run tests:
        - raw Python: `python -m pytest`
        - uv: `uv run --extra tests pytest`
        - PowerShell: `python -m pytest`
        - conda: `python -m pytest`

- To select the agent harness used in this example, create a project-root
    `.env` file containing one of these values:

    ```dotenv
    WORKFLOW_VERIFICATION_HARNESS=pi
    # or: codex, claude
    ```

    The `harness` fixture selects a client from `tests/clients/`, using the existing
    CLI installation and login. The `.env` file is ignored by Git; the fixture
    skips if the selected executable is not on `PATH`. It launches nothing until
    `run()` is called.

    ```python
    events = harness.run("Fix the reported bug using the bugfixing skill.")
    # Inspect the plan, regression test, and unchanged production code here.
    follow_up_events = harness.run("Approved; implement the plan.")
    ```

    Each call runs one non-interactive CLI process and returns a list of raw JSON
    events after completion. Subsequent calls on the same client resume its specific
    session, not the most recent session. Sessions remain in the CLI's normal storage;
    a new client starts a fresh session unless given `session_id=...`.
    Clients accept `cwd`, `env`, `command`, and `timeout` (default: 300 seconds).
    Nonzero exits raise `subprocess.CalledProcessError` with stdout/stderr;
    timeouts raise `subprocess.TimeoutExpired`.

    There are no interactive permission/UI callbacks. Configure necessary tool
    permissions through the CLI's settings or `command` argument; a follow-up
    plan approval is an ordinary user message, not a tool-permission response.
    Pi must trust the fixture project to load its project-local skills (for a
    trusted fixture, use `command=("pi", "--mode", "json", "--approve")`).
    Run evaluations in disposable workspaces with appropriate sandboxing.

    Client plumbing tests use fake processes only: they do not launch agents or
    incur token costs. Actual workflow evaluations do.


- We are using a skill that defines a workflow for bugfixing:
    - reproduce bug
    - add regression test
    - plan out fix and write to file
    - hand over for review
    - implement
    - automated review and correction loop
    - return report
- Start your harness from the project root, or it won't find the skill
- See: `.{WORKFLOW_VERIFICATION_HARNESS}/skills/bugfixing` to read what it does in ddtail.


## Goal
- Goal: Build a verifier for a select few steps of single run of the workflow, e.g.:
    - verifies that the agent added a regression test that fails initially
    - verifies that the agent wrote the plan
- Tool: langchain agenteval, already installed. The tool's repository is here: https://github.com/langchain-ai/agentevals
- Task:
    - there's a buggy implementation of the lotka volterra solver, implemented as a text fixture in `test/conftest.py`
    - Decide on two or three of the steps and fill them in at the indicated position
    - Decide on how to extend it: Statistics over multiple prompts?

## Steps
- familiarize yourself with the skill called 'bugfixing'
- familiarize yourself with the lotka.py code and
## Questions
