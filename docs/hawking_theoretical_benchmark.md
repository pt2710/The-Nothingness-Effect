# Hawking Theoretical Benchmark

Hawking-radiation is treated here as a theoretical benchmark, not as an empirical fetched-data target. The TNE Hawking-like radiation proxy is compared against standard Hawking temperature, power, evaporation and spectral scaling relations. This is a theoretical consistency comparison, not empirical validation.

## Purpose

These files provide repository-linked computational support artifacts for the manuscript's Hawking-like discussion. They do not claim direct astrophysical Hawking-radiation observation, and they do not replace mathematical proofs in the paper.

## Scope Boundary

- not an empirical validation claim
- not a direct astrophysical observation
- not full GR/QFT
- not a formal proof substitute

## Main Commands

```bash
python -m equations.black_hole_dynamics.hawking.simulation.theoretical_benchmarks.simulate_hawking_theoretical_benchmark
python -m equations.black_hole_dynamics.hawking.simulation.theoretical_benchmarks.compare_tne_hawking_like_flux
```

## Generated Outputs

Simulation outputs:

- `equations/black_hole_dynamics/hawking/simulation/hawking_temperature_vs_mass.png`
- `equations/black_hole_dynamics/hawking/simulation/hawking_power_vs_mass.png`
- `equations/black_hole_dynamics/hawking/simulation/hawking_evaporation_timescale_vs_mass.png`
- `equations/black_hole_dynamics/hawking/simulation/hawking_normalized_spectrum.png`
- `equations/black_hole_dynamics/hawking/simulation/hawking_theoretical_benchmark_data.csv`
- `equations/black_hole_dynamics/hawking/simulation/hawking_theoretical_benchmark_metrics.csv`
- `equations/black_hole_dynamics/hawking/simulation/hawking_theoretical_benchmark_metadata.json`

Comparison outputs:

- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_temperature.csv`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_power.csv`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_spectrum.csv`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_metrics.csv`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_temperature.png`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_power.png`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_spectrum.png`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_residuals.png`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_report.md`
- `equations/black_hole_dynamics/hawking/simulation/tne_vs_hawking_manifest.json`

Summary outputs:

- `equations/black_hole_dynamics/hawking/simulation/benchmark_summary.csv`
- `equations/black_hole_dynamics/hawking/simulation/benchmark_summary.md`
- `equations/black_hole_dynamics/hawking/simulation/benchmark_summary_metadata.json`

## Interpretation Guide

- Hawking formulas are the benchmark reference layer.
- TNE outputs are finite toy proxies.
- RMSE, MAE, R2, and log-log slopes describe benchmark consistency under the implemented proxy mapping only.
- Better slope or residual agreement does not establish empirical validation of TNE.
