# AI4RSE 2026 Quality-Assurance Workshop

This repository contains the exercise project for the AI4RSE 2026 workshop on quality assurance. It uses a small implementation of the Lotka–Volterra predator–prey model as the example application and focuses on building verification machinery with test-driven development (TDD) and behaviour-driven development (BDD).

## The model

The model's right-hand side is

```math
\frac{dx}{dt} = \alpha x - \beta xy
\qquad
\frac{dy}{dt} = \delta xy - \gamma y
```

where $$x$$ and $$y$$ are the two population sizes and $$\alpha$$, $$\beta$$,  $$\gamma$$ and $$\delta$$ are model parameters.

## Workshop branches

- `tdd-bdd` contain the exercise material.
- `tdd-bdd-sol` contains the corresponding solutions.

## Run the tests

Create an environment with Python 3.10 or later, install the test dependencies, then run pytest:

```bash
python -m pip install -e ".[tests]"
python -m pytest
```

## Project layout

- `src/qa/lotka.py` — the Lotka–Volterra implementation to be filled in.
- `tests/` — the exercise test suite to be filled in.
- skills live in `.pi/skills` or the equivalent path on windows


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
