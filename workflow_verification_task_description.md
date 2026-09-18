# Workflow trajectory verification - Example task

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

- We are using a skill that defines a workflow for bugfixing:
    - reproduce bug
    - add regression test
    - plan out fix and write to file
    - hand over for review
    - implement
    - automated review and correction loop
    - return report
- See: `skills/bugfixing` to read what it does in detail.
- You can install the skill 'bugfixes' for your agent harness (e.g., for project-local skills, copy it to .agents/skills, .claude/skills, .codex/skills), and run it yourself to find get a feel for how it works.

## Remark
This branch bundles the buggy app and the workflow in one project for the purposes of this workshop, which of course normally is not the case.
- Since the `agentevals` library needs OpenAI-style messages, we need a small parser to parse the trajectories into the right format. This is implemented in `src/eval/trajectory_parser.py`.
## Goal
Extend a verifier for a select few steps of single run of the workflow, e.g.:
    - verifies that the agent added a regression test that fails initially
    - verifies that the agent wrote the plan
- Tool: langchain agenteval, already installed. The tool's repository is here: https://github.com/langchain-ai/agentevals

## Steps
- read through the issue in `bug_ticket` and familiarize yourself with the code in lotka.py.
- familiarize yourself with the example tests for test_bugfix_workflow.py.
- OPTIONAL: install the skill and run it to observer how it works
- We are using the agentevals library here, and the test provides a simple example for a saved trajectory of applying the `bugfixing` skill to the bug ticket for claude, codex and pi, with claude sonnet 5 (claude), gpt5.6-Luna (codex, pi) and
 with medium thinking level. There is an additional trace for pi with the thinkingmachines/inkling-free model. The example traces have been obtained with the following initial prompt:
"I have a bug ticket in ./bug_ticket. apparently something with the lotka app is wrong. Please use the project local 'bugfixing' skill to fix this problem."
Each trace contains one json object representing one interaction step per line.
- familiarize yourself with the code in the `eval` directory.
- think about the relevant steps in the workflow. which ones are important to verify, which ones could be left out?
- fill in an additional step check with one step from the workflow that you think makes sense

## Questions
- think about the characteristics of AI agents. Considering those, could the trajectory workflow verification be improved?
- if you are familiar with other testing/verification techniques, which ones would be suitable to augment workflow verification?