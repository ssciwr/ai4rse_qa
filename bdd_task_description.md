# Agentic behavior driven development - Example task

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

## Goal
We want to built a tiny little app with the foollowing features:
- the actual solver code that solves the lotka-volterra equations. We want to input parameters and initial conditions and get out 2 arrays, one for x and one for y, with n timepoints each
- A small CLI that lets us put in these parameters and initial conditions via a terminal
- A plotting functionality that visualizes the solution:
    - trajectory plots: x(t), y(t)
    - phase plot: y(x)

## Steps
- Identify user roles, e.g., 'researcher'.
- You can use an auxilliary file to save the following two steps
- For each feature, write one or more user stories, using the following scheme.
```As a <role>, I want to <capability> so I can <purpose/benefit>.```
These define a feature-level narrative for why the capability matters and for whom.
- Clearly formulate each user story for the current feature as an observable acceptance criterion in a scenario
```
Scenario: <short descriptive title>
    Given <precondition / initial state>
    When  <action / event>
    Then  <expected observable outcome>
```
- Ask your agent to convert your draft to a pytest-bdd compatible scenario saved in tests/feature_name.feature
- Validate the result. Review for faithfulness and accuracy, or simplify if neccessary.
- Ask your agent to create a pytest-bdd tests from this and run it. The goal is to tie our formulated requirements to representative code that makes them executable and machine checkable.
We now have formulated part of our requirements in executable form. They currently fail because there is no code to fulfill them.
- Next build ask the agent to write the code to fulfill these tests. Consider whether using a new session is appropriate and why.
- Review the resulting code. Do the tests work? does the code work? What went wrong? If anything did, for what reason?
- Work your way through the features of the app until it is complete.

## Questions
- What are advantages and disadvantages of this approach?
- What is your understanding of the system that emerged?
- How do you judge overview over the whole system vs detailed understanding?