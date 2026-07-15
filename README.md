# The Nothingness Effect

This repository contains the typed computational runtime for The Nothingness
Effect (TNE). Seven externally maintained mathematical appendices define the
source authority. The repository stores theorem IDs, checksums, contracts,
tests, simulations, and bounded provenance—but never the authoritative LaTeX
sources themselves.

## Theorem-complex architecture

The verified inventory contains 351 theorem complexes: 204 A source laws, 98 B
additive derivations, and 49 C spatial closures. Current certified coverage and
the deliberately retained proxy/open rows are listed in
`docs/tne_theorem_complex_implementation_status.md`.

```text
appendix theorem ID -> typed contract -> invariant/residual -> tests
                    -> deterministic simulation -> artifact manifest
```

- `the_nothingness_effect._runtime/theorem_complex_runtime/` provides typed IDs, domains, codomains,
  statuses, residuals, registries, evaluation, and provenance.
- `the_nothingness_effect/artificial_intelligence/` contains canonical CPU-testable QENN,
  deterministic prime/parity PGQENN, and multi-network SOInets.
- Its six producer-local output modules demonstrate color and sound
  classification, bidirectional color and sound classification, and color and
  sound cloning. See `docs/tne_ai_output_capabilities.md` for commands and
  claim boundaries.
- `fields_of_physics_in_dev/the_nothingness_effect.py` is the argument-correct central facade; explicit
  compatibility wrappers retain bounded legacy behavior.
- `tests/contracts`, `tests/invariants`, `tests/boundaries`,
  `tests/source_removal`, `tests/numerical`, and `tests/artifacts` separate the
  contract gates.
- `docs/data/` contains the 351-row status matrix, source registry, AI mapping,
  revision-plan review, aggregate provenance, and final QA data.

## Versioning Policy

The repository tracks source code, tests, static figures, and compact reproducible result files. Pre-implementation `framework` directories are intentionally excluded. Local caches, IDE state, agent state, secrets, backup archives, frame dumps, videos, animations, and other large generated artifacts are excluded through `.gitignore`.

The authoritative appendix filenames and content hashes are guarded by CI.
Appendix `.tex` files must remain outside every repository Git root. Reference
filenames, theorem IDs, labels, and SHA-256 values are permitted metadata;
source text and checksum sidecar copies are not repository data.

Local ZIP archives are intentionally ignored because they duplicate or externally reference repository inputs.

Large generated artifacts can be regenerated from the simulation scripts. If future work requires versioning videos, large archives, or datasets over normal GitHub limits, use Git LFS or an external artifact store.

## Environment

The current repository baseline is documented against Python 3.14.3. The `.python-version` file records that local interpreter version for pyenv-compatible tooling.

Install the project dependencies with:

```bash
python -m pip install -r requirements-dev.txt
```

Install the optional differentiable CPU backend with:

```bash
python -m pip install -r requirements-ai.txt
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

Focused validation and security commands are:

```bash
python -m pytest -q tests/contracts tests/invariants tests/boundaries tests/source_removal
python -m pytest -q tests/artifacts
python -m pytest -q tests/numerical/test_qenn_model.py tests/numerical/test_pgqenn_model.py tests/numerical/test_soinets_model.py
python tools/check_no_authoritative_appendices.py
python -m tools.qa_guards
```

## Regeneration and provenance

Each certified theorem complex has a deterministic runner and a manifest with
the appendix checksum, start/result commits, parameters, seed, tolerances,
residual vector, closure status, generated files, regeneration command, and the
claim boundary `finite computational support; not a formal proof substitute`.

```bash
python -m the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.simulation --output artifacts/generated/flowpoint
python -m the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite --output artifacts/generated/qenn
python -m the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite --output artifacts/generated/pgqenn
python -m the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite --output artifacts/generated/soinets
```

The aggregate regeneration catalog is
`docs/data/artifact_provenance_manifest.json`. Large tables, frame dumps,
animations, and datasets remain local; only compact manifests and selected
representative static figures are tracked.

## Exact, numerical, and compatibility boundaries

Canonical DFI and pDFI fail closed on singular/non-finite inputs. Elastic-π
keeps exact exponent semantics, numerical evaluation, optional clipping, and
diagnostic metadata separate. A reduced residual is evidence only: C-level
finite results remain `numerical_candidate` unless the declared mathematical
closure obligations are actually established.

Legacy toy/proxy modules remain available for reproduction and ablation. They
do not become theorem implementations merely because they return finite
numbers. The historical `tne_concepts` tree and all pre-implementation
`framework` directories have been removed; canonical AI code composes the
shared QENN, PGQENN, and SOInet primitives directly.

The repository-level `conftest.py` sets Matplotlib to the headless `Agg` backend during pytest runs, which avoids GUI/Tk dependencies in figure-generating tests.

## Missing Paper Figure Artifacts

The repository also contains deterministic manuscript-linked computational
support artifacts under the relevant `equations/<component>/test` and
`equations/<component>/simulation` folders. See
`docs/missing_paper_figures.md` for exact commands and generated paths.

These outputs are finite illustrative simulations and numerical support
figures, not formal proof substitutes.
