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

Large generated artifacts can be regenerated from the simulation scripts. If future work requires versioning videos, large archives, or datasets over normal GitHub limits, use Git LFS or an external artifact store.

## Validation

Tests are organized mostly as `test_*.py` files under each model directory. From the repository root, run:

```powershell
$env:MPLBACKEND = "Agg"
python -m pytest
```

```bash
MPLBACKEND=Agg python -m pytest
```

Some simulations may require scientific Python packages such as NumPy, pandas, matplotlib, SciPy, Plotly, and tqdm. Feather export tests require `pyarrow`; the experimental gravitational-curvature test path requires `numba`.
