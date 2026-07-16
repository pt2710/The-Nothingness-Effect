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

- Section 15.4 / Figure 31: `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect/`
- Section 16.4 / Figure 6: `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity/`
- Section 18.6 and 18.13: `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/`
- Section 19.4 / Figure 7: `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts/`
- Section 23.4 / Figures 48-49 / Table 19: `the_nothingness_effect/the_completeness_theorem/noether_structure/`

## Commands

Generate simulation artifacts:

```bash
python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.simulate_elastic_dubler_effect
python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.simulation.simulate_locality_driven_gravity
python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.simulation.simulate_black_hole_dynamics
python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.simulation.simulate_elastic_pi_ripples
python -m the_nothingness_effect.the_completeness_theorem.noether_structure.simulation.simulate_noether_tne
```

Run focused tests:

```bash
python -m pytest the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect/test the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity/test the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/test the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts/test the_nothingness_effect/the_completeness_theorem/noether_structure/test
```

## Simulation Output Paths

- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect/simulation/figure31_dubler_shift_entropy_gradient.png`
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity/simulation/figure6_locality_driven_spiral.png`
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/simulation/section18_elastic_pi_entropic_horizon.png`
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/simulation/section18_hawking_like_entropic_radiation.png`
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/simulation/section18_observer_horizon_memory.png`
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/simulation/section18_computational_feasibility.png`
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts/simulation/figure7_elastic_pi_ripple_ringdown.png`
- `the_nothingness_effect/the_completeness_theorem/noether_structure/simulation/figure48_kd_flux_phase_shift.png`
- `the_nothingness_effect/the_completeness_theorem/noether_structure/simulation/figure49_fp_gauss_identity_128x128.png`
- `the_nothingness_effect/the_completeness_theorem/noether_structure/simulation/table19_noether_validation_metrics.csv`

Each simulation directory also stores its local `.npz`, `.csv`, and `.json`
metadata outputs.

## Test Output Paths

Each test script writes a compact local visualization, result CSV, and NPZ
fixture into its own `test/` directory. These files document the test-time
artifact path and are deterministic.
