# Completeness-Theorem Supplementary Simulations

## Purpose

These simulations are finite illustrative models of dual-closure state
classification. They provide repository-linked computational support artifacts,
trace data, metrics, and figures for the manuscript's completeness and
dual-closure discussion.

## Scope Boundary

These files do not prove Godel wrong, do not replace mathematical proofs in the
manuscript, and do not claim that a finite graph simulation establishes the
paper's full mathematical theory. They are finite toy systems and visual
computational companions to the manuscript.

The intended interpretation is conservative:

- finite illustrative model
- computational support artifact
- dual-closure trace visualization
- repository-linked supplementary simulation
- not a formal proof substitute

## Directory Structure

```text
the_nothingness_effect/the_completeness_theorem/
  README.md
  models.py
  simulation/
    __init__.py
    artifacts.py
    dual_closure.py
    godel_boundary.py
    run_godel_boundary_figures.py
    run_completeness_supplementary.py
    visualization.py
  simulation/artifacts/supplementary/
    traces/
    metrics/
    figures/
  tests/
    test_dual_closure_invariants.py
    test_fixed_point_detection.py
    test_outputs.py
```

## How To Run

From the repository root:

```bash
python -m the_nothingness_effect.the_completeness_theorem.simulation.run_godel_boundary_figures
python -m the_nothingness_effect.the_completeness_theorem.simulation.run_completeness_supplementary
```

Run the focused tests with:

```bash
python -m pytest the_nothingness_effect/the_completeness_theorem/tests
```

## Expected Outputs

All generated files are written under:

```text
the_nothingness_effect/the_completeness_theorem/simulation/artifacts/supplementary/
```

The runners create missing output directories automatically. The outputs are
deterministic and do not require network calls or local absolute paths.

## Figure List

Godel/completeness illustrative figures:

- `simulation/artifacts/supplementary/figures/godel_boundary_graph.png`
- `simulation/artifacts/supplementary/figures/dual_closure_lattice.png`
- `simulation/artifacts/supplementary/figures/closure_iteration_trace.png`
- `simulation/artifacts/supplementary/figures/incompleteness_vs_dual_closure_phase.png`

Completeness-theorem supplementary figures:

- `simulation/artifacts/supplementary/figures/closure_fixed_point_trace.png`
- `simulation/artifacts/supplementary/figures/duality_pair_coverage.png`
- `simulation/artifacts/supplementary/figures/closure_failure_modes.png`
- `simulation/artifacts/supplementary/figures/completeness_operator_convergence.png`
- `simulation/artifacts/supplementary/figures/closure_state_space_projection.png`

## Trace And Metrics List

JSON traces:

- `simulation/artifacts/supplementary/traces/godel_boundary_trace.json`
- `simulation/artifacts/supplementary/traces/fully_pairable_system_trace.json`
- `simulation/artifacts/supplementary/traces/missing_dual_system_trace.json`
- `simulation/artifacts/supplementary/traces/circular_dependency_system_trace.json`
- `simulation/artifacts/supplementary/traces/contradiction_system_trace.json`
- `simulation/artifacts/supplementary/traces/unpaired_boundary_system_trace.json`

CSV metrics:

- `simulation/artifacts/supplementary/metrics/closure_iteration_metrics.csv`
- `simulation/artifacts/supplementary/metrics/duality_pair_coverage.csv`
- `simulation/artifacts/supplementary/metrics/closure_failure_modes.csv`
- `simulation/artifacts/supplementary/metrics/fixed_point_summary.csv`

## Interpretation Guide

The simulations classify finite toy nodes as open, unresolved, provable,
unprovable within the toy system, represented dual complements, closure
candidates, closed represented pairs, paradox boundaries, or contradictions.

`unprovable_within_system` is not treated as false. `paradox_boundary` is not
automatically closed. A pair can enter `closed` only when both represented dual
counterparts are present and no explicit obstruction blocks the closure
criteria. Contradiction, missing-dual, circular-dependency, and unpaired-boundary
cases are flagged as limitations of the finite toy system.

## Citation And Linking Note

The TNE paper may link to this directory as a supplementary computational
artifact path for "Godel/completeness simulation figures" and
"Completeness-theorem supplementary simulation files." Link text should preserve
the scope boundary: these are finite illustrative dual-closure simulations and
not formal proof substitutes.

