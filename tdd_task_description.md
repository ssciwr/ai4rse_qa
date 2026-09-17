# Agentic test driven development - Example task

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
part A):
- naively prompt your coding agent to built each feature one after the other or however you see fit
- review the resulting code.
- try out the resulting code.

part B):
- Restart the exercise by deleting the code that just has been created
- Let the agent plan out the **unit tests first** for the first feature. You have to come up with some function names for the different features perhaps.
- The Lotka-volterra equations have 2 equillibrium points: (x,y) = (0, 0) and (x,y) = (gamma/delta, alpha/beta). We can use these invariants of the target system to built property tests that acertain that we actually implemented the right equation. Consider this when instructing the agent to plan the tests.
- Review the plan, refine and iterate until you are happy with the plan
- Let the agent implement the test plan for the given feature
- The code that these tests are for doesn't exist yet, and hence they fail. Let's make sure this is so
- Once the test plan for a given feature is complete and reviewed, task the agent with implementing the code that fulfills these tests.
- Review the result. Make sure the respective tests function now
- Proceed through each feature in that manner.

## Questions
- What is your confidence level in the produce product?
- What is your understanding of the produced code?
