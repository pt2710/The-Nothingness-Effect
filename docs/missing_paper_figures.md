# Missing Paper Figure Artifacts

These scripts generate finite, deterministic computational support artifacts
for TNE manuscript sections that reference simulation figures. They are
repository-linked numerical illustrations and validation checks, not
substitutes for the formal arguments in the paper.

## Scope Boundary

The outputs do not prove TNE as a complete theory. They do not replace formal
proofs, and the black-hole and ripple models are not full GR/QFT simulations.
Use them as finite illustrative simulations, numerical support figures, and
deterministic reproduction artifacts for manuscript-linked paths.

## Repository Convention

The figure pipelines follow the existing `equations/<component>/` convention.
Each component has:

- an implementation module,
- a `test/` directory with a pytest-compatible test script,
- a `simulation/` directory with a dedicated simulation runner,
- generated test artifacts written beside the test script,
- generated simulation artifacts written beside the simulation script.

## Sections Covered

- Section 15.4 / Figure 31: `equations/elastic_dubler_effect/`
- Section 16.4 / Figure 6: `equations/locality_driven_gravity/`
- Section 18.6 and 18.13: `equations/black_hole_dynamics/`
- Section 19.4 / Figure 7: `equations/elastic_pi_ripples/`
- Section 23.4 / Figures 48-49 / Table 19: `equations/noether_tne/`

## Commands

Generate simulation artifacts:

```bash
python -m equations.elastic_dubler_effect.simulation.simulate_elastic_dubler_effect
python -m equations.locality_driven_gravity.simulation.simulate_locality_driven_gravity
python -m equations.black_hole_dynamics.simulation.simulate_black_hole_dynamics
python -m equations.elastic_pi_ripples.simulation.simulate_elastic_pi_ripples
python -m equations.noether_tne.simulation.simulate_noether_tne
```

Run focused tests:

```bash
python -m pytest equations/elastic_dubler_effect/test equations/locality_driven_gravity/test equations/black_hole_dynamics/test equations/elastic_pi_ripples/test equations/noether_tne/test
```

## Simulation Output Paths

- `equations/elastic_dubler_effect/simulation/figure31_dubler_shift_entropy_gradient.png`
- `equations/locality_driven_gravity/simulation/figure6_locality_driven_spiral.png`
- `equations/black_hole_dynamics/simulation/section18_elastic_pi_entropic_horizon.png`
- `equations/black_hole_dynamics/simulation/section18_hawking_like_entropic_radiation.png`
- `equations/black_hole_dynamics/simulation/section18_observer_horizon_memory.png`
- `equations/black_hole_dynamics/simulation/section18_computational_feasibility.png`
- `equations/elastic_pi_ripples/simulation/figure7_elastic_pi_ripple_ringdown.png`
- `equations/noether_tne/simulation/figure48_kd_flux_phase_shift.png`
- `equations/noether_tne/simulation/figure49_fp_gauss_identity_128x128.png`
- `equations/noether_tne/simulation/table19_noether_validation_metrics.csv`

Each simulation directory also stores its local `.npz`, `.csv`, and `.json`
metadata outputs.

## Test Output Paths

Each test script writes a compact local visualization, result CSV, and NPZ
fixture into its own `test/` directory. These files document the test-time
artifact path and are deterministic.
