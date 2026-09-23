
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# AI4RSE 2026 Quality-Assurance Workshop

This repository contains the exercise project for the AI4RSE 2026 workshop on quality assurance. It uses a small app that solves and visualizes the Lotka–Volterra predator–prey model as the example application.

It is planned that this repository will be updated from time to time as the examples are used more and get improved.

## The model

The Lotka-Volterra model is:

$$
\frac{dx}{dt} = \alpha x - \beta xy
\qquad
\frac{dy}{dt} = \delta xy - \gamma y
$$

where $x$ and $y$ are the two population sizes and $\alpha$, $\beta$,  $\gamma$ and $\delta$ are model parameters.

- $x$: Prey population size
- $y$: Predator population size
- $\alpha$: Prey population growth rate.
- $\beta$: Predation parameter of prey
- $\delta$: Predator population growth parameter. Growth rate is $\delta$ x, i.e. is proportional to the current prey population.
- $\gamma$: Death rate of predator

Starting parameters and initial conditions to get started could be:
- $x$: 0.1
- $y$: 0.2
- $\alpha$: 1.0
- $\beta$: 0.1
- $\delta$: 0.075
- $\gamma$: 1.5

## Workshop branches

- `tdd` contains the exercise material for the test driven development task
- `bdd` contains the exercise material for the behavior driven development task
- `skill-verification` contains the exercise material for the workflow verification task

Every branch has a corresponding *name*_sol branch that contains possible solutions for each task.

## Run the tests

Create an environment with Python 3.10 or later, install the test dependencies, then run pytest:

```bash
python -m pip install -e ".[tests]"
python -m pytest
```

## Project layout

- `src/qa/lotka.py` — the Lotka–Volterra implementation to be filled in.
- `src/eval_harness.py` - code used for skill evaluation example.
- `bug_ticket` - a fictional bug report about a defect in the `lotka` app including solutions and plots
- `skills` - contains the skill that defines the workflow we want to verify.

