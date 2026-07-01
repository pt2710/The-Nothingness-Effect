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

## Sections Covered

- Section 15.4 / Figure 31: Dubler shift as a function of entropy gradient for varying KD.
- Section 16.4 / Figure 6: locality-driven spiral structure toy simulation.
- Section 18.6 and 18.13: Elastic-pi entropic horizon, Hawking-like radiation proxy, observer horizon memory, and feasibility metrics.
- Section 19.4 / Figure 7: Elastic-pi ripple propagation, attenuation, and nonlinear Xi distortion proxy.
- Section 23.4 / Figures 48-49 / Table 19: KD flux under fp phase shift and fp-Gauss identity residual.

## Commands

Generate individual artifacts:

```bash
python -m simulations.run_dubler_effect_figure31
python -m simulations.run_locality_spiral_figure6
python -m simulations.run_black_hole_dynamics_section18
python -m simulations.run_elastic_pi_ripple_figure7
python -m simulations.run_noether_figures48_49
```

Generate the full missing-figure pipeline:

```bash
python -m simulations.run_missing_paper_figures
```

Run the focused tests:

```bash
python -m pytest tests/test_dubler_effect.py tests/test_locality_driven_gravity.py tests/test_black_hole_dynamics.py tests/test_elastic_pi_ripples.py tests/test_noether_tne.py tests/test_missing_figure_outputs.py
```

## Output Paths

Figures:

- `outputs/figures/section15/figure31_dubler_shift_entropy_gradient.png`
- `outputs/figures/section16/figure6_locality_driven_spiral.png`
- `outputs/figures/section18/section18_elastic_pi_entropic_horizon.png`
- `outputs/figures/section18/section18_hawking_like_entropic_radiation.png`
- `outputs/figures/section18/section18_observer_horizon_memory.png`
- `outputs/figures/section18/section18_computational_feasibility.png`
- `outputs/figures/section19/figure7_elastic_pi_ripple_ringdown.png`
- `outputs/figures/section23/figure48_kd_flux_phase_shift.png`
- `outputs/figures/section23/figure49_fp_gauss_identity_128x128.png`

Data:

- `outputs/data/dubler_effect/figure31_dubler_grid.npz`
- `outputs/data/locality_driven_gravity/figure6_spiral_particles.npz`
- `outputs/data/black_hole_dynamics/section18_black_hole_trace.npz`
- `outputs/data/elastic_pi_ripples/figure7_ripple_history.npz`
- `outputs/data/noether_tne/figure48_kd_flux_trace.npz`
- `outputs/data/noether_tne/figure49_fp_gauss_grid.npz`

Metrics:

- `outputs/metrics/section15/figure31_dubler_metrics.csv`
- `outputs/metrics/section16/figure6_spiral_metrics.csv`
- `outputs/metrics/section18/section18_black_hole_metrics.csv`
- `outputs/metrics/section18/section18_feasibility_metrics.csv`
- `outputs/metrics/section19/figure7_ripple_metrics.csv`
- `outputs/metrics/section23/table19_noether_validation_metrics.csv`
- `outputs/metrics/missing_paper_figures_summary.csv`
