# Producer-local repository layout

Repository implementation, tests, simulations, and their compact evidence are
colocated by subject. No pre-implementation `framework` directory is part of
the repository.

## Shared infrastructure

- `the_nothingness_effect._runtime/theorem_complex_runtime/`: typed contracts, registries,
  invariants, residuals, validation, provenance, and runners.
- `the_nothingness_effect._runtime/artifacts/`: shared persistence and animation helpers.
- `the_nothingness_effect/fluctuation_and_elastic_dynamics/artifacts.py`: DFI/pDFI/Elastic-pi
  domain artifacts.
- `the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/`: shared physical
  contract runtime and artifacts.
- `tools/run_animation_artifacts.py`: aggregate regeneration command.
- `docs/data/animation_artifacts_*`: aggregate animation reports.

## Requested module standard

`cosmological_spark_dynamics`, `dtqc`, `elastic_dubler_interferometry`,
`elastic_pi_norm`, `mathematical_closure`, and `parity_dfi` each contain:

```text
<module>/
    canonical implementation/contracts
    test/
        test_evidence.py
        data, figures, animation, manifests
    simulation/
        run_evidence.py
        data, figures, animation, manifests
```

DTQC regenerates quasicrystal contour, FFT diffraction, central-row wavelet,
DFI surface, exact Elastic-pi surface, and phase-clock animation evidence.

## Relocated or removed paths

The facade and fields audit now live in `fields_of_physics_in_dev/`. Hawking
theoretical benchmark tests and simulations live below
`the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/hawking/`. The repository no longer contains
`tne_concepts`, `theoretical_benchmarks` at root, `figures`,
`figures_mccrackn`, `equations/mccrackns_prime_law`, or
`equations/numbers_domains`.

All generated evidence is finite computational support and is not a formal
proof substitute or a claim of unrestricted real-world AI perception.
