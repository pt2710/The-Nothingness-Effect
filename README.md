# The Nothingness Effect

This repository contains the representative codebase for The Nothingness Effect (TNE), a theoretical framework for exploring flowpoint dynamics, infinity, symmetry, duality, observation/collapse, and related physics-oriented models.

## Repository Structure

- `the_nothingness_effect.py` exposes the central `NothingnessEffect` interface.
- `equations/` contains core TNE equation implementations, tests, simulation scripts, frameworks, and reproducible tabular outputs.
- `fields_of_physics_in_dev/` contains experimental physics-domain applications and simulations.
- `tne_concepts/` contains additional concept prototypes and visualization pipelines.
- `figures/` and `figures_mccrackn/` contain static figures that support the theory and paper.
- `project_documentation/` contains project-level documentation, including the associated TNE paper PDF when present.

## Versioning Policy

The repository tracks source code, tests, framework notes, static figures, and compact reproducible result files. Local caches, IDE state, agent state, secrets, backup archives, frame dumps, videos, animations, and other large generated artifacts are excluded through `.gitignore`.

The root ZIP archives (`equations.zip`, `fields_of_physics_in_dev.zip`, and `tne_concepts.zip`) are intentionally ignored because they duplicate files that are already tracked in their corresponding directories.

Large generated artifacts can be regenerated from the simulation scripts. If future work requires versioning videos, large archives, or datasets over normal GitHub limits, use Git LFS or an external artifact store.

## Environment

The current repository baseline is documented against Python 3.14.3. The `.python-version` file records that local interpreter version for pyenv-compatible tooling.

Install the project dependencies with:

```bash
python -m pip install -r requirements-dev.txt
```

Interactive/OpenGL observation simulations have additional GUI dependencies:

```bash
python -m pip install -r requirements-interactive.txt
```

On Windows with Python 3.14, `pygame` may require either a compatible published wheel or a local C/C++ build toolchain.

## Validation

Tests are organized mostly as `test_*.py` files under each model directory. From the repository root, run:

```bash
python -m pytest
```

The repository-level `conftest.py` sets Matplotlib to the headless `Agg` backend during pytest runs, which avoids GUI/Tk dependencies in figure-generating tests.

## Missing Paper Figure Artifacts

The repository also contains a deterministic pipeline for manuscript-linked
computational support artifacts under `simulations/`, `visualizations/`,
`outputs/`, and `docs/missing_paper_figures.md`. Generate the full set with:

```bash
python -m simulations.run_missing_paper_figures
```

These outputs are finite illustrative simulations and numerical support
figures, not formal proof substitutes.
