# ai4rse_qa
This repository contains a small app to solve the 2d Lotka-Volterra equations with
positive parameters and populations.

# Layout
We have a simple library in src/qa/lotka.py which contains
- a solver function to solve the ODE
- two plotting functions for phase- and trajectory plots
- a small CLI definition

# Setup
Use the user's prefered python package manager or python installation to set up the package, e.g., uv, conda or normal python.

Always use a virtual environment ot install the package into, and use editable mode, e.g.,

```bash
python3 -m pip install -e .[tests]
```

Dependencies and project metadata are defined in `pyproject.toml`.

# Entry points
You can run `python3 ./src/qa/lotka.py --alpha a --beta b --gamma c --delta d --x0 x --y0 y --t T --n N with a,b,c,d,x,y,T,N positive real numbers for the parameters, initial conditions, time window and time resolution of the solution, respectively.  This creates solution plots saved to the root dir of the project. Numerical tranjectories are not saved.
You can also use lotka --alpha 1.0 --beta 0.1 --gamma 1.5 --delta 0.075 --x0 10 --y0 5 --t 40 --n 100  from the command line directly.
# Testing
We are using pytest to test this project. Tests live in {project_root_dir}/tests and the library tests are in test_lotka.py.
test_bugfix_workflow.py is a test file that inspects agent trajectories for some skill usage. This is not relevant for the library, but for the bugfixing skill. Ignore it when dealing with library development.
LLM-as-judge tests are marked `judge` and are run by the user only. Do not run `pytest -m judge`, set or search for `WORKFLOW_JUDGE_ENV_FILE`, or try to locate the external judge `.env` file.
Report line and branch coverage whenever you are testing the project.

# Coding guidelines
- Keep code minimal and simple. Do not add code that is not necessary for a given functionality.
- Use minimal google style docstrings that describe the purpose and parameters of a function, not its implementation internals
- Keep tests small, clean and consice, do not test multiple functions or functionality classes within a single test