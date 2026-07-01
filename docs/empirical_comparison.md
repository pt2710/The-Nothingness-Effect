# Empirical Comparison Pipeline

## Purpose

These empirical comparison scripts are preliminary reproducible comparison tools. They do not establish empirical validation of TNE. They map dimensionless TNE proxy outputs to observable quantities through explicit fitted or calibrated adapters and compare residuals against available empirical or published reference data.

This layer is a repository-linked computational support artifact. It is not a formal proof substitute.

## Claim Boundary

- Offline fixture-backed comparisons only in this run.
- Not an empirical validation claim.
- Not a claim that improved residual fit proves TNE.
- Not a claim that finite simulations replace the manuscript's mathematical arguments.
- Not a full GR, QFT, GRMHD, or astrophysical simulation stack.

All fixture datasets are explicitly labelled `fixture_only`.

## Supported Targets

- Dubler redshift / clock proxy
- Spiral galaxy rotation proxy
- EHT horizon / shadow proxy
- Hawking-like flux proxy
- Observer memory proxy
- Elastic-pi ringdown proxy

Noether and fp-Gauss outputs remain internal consistency diagnostics rather than direct empirical comparisons.

## Directory Layout

```text
empirical/
  data_acquisition/
  mappings/
  comparison/
  visualization/
  fixtures/
  outputs/
  tests/
```

## Offline / Fixture Mode

Run 4 is intentionally offline and fixture-backed. It does not fetch large external datasets or silently upgrade fixture comparisons into observational claims.

Default command:

```bash
python -m empirical.comparison.run_empirical_comparisons --offline --use-fixtures --dataset all
```

## Model-to-Observable Mappings

- `dubler_redshift_mapping.py`: maps dimensionless Dubler-shift outputs to a finite redshift-style fixture through fitted `beta` and `K_D`.
- `spiral_galaxy_mapping.py`: maps locality-driven particle dynamics to radial rotation-curve observables through radius and velocity scaling.
- `horizon_eht_mapping.py`: maps horizon-radius proxies to ring/shadow observables through a fitted angular scale.
- `hawking_flux_mapping.py`: maps flux proxies to a normalized fixture flux curve with an exponential baseline.
- `observer_memory_mapping.py`: maps black-hole memory-like traces to a ringdown-style fixture proxy after time alignment and amplitude normalization.
- `ripple_ringdown_mapping.py`: maps elastic-pi ringdown traces against a damped-sinusoid baseline and a fixture waveform.

## Baseline Models

- Fixture baseline shift for Dubler redshift
- Linear rotation baseline for spiral rotation
- Exponential decay baseline for Hawking-like flux
- Damped sinusoid baseline for elastic-pi ringdown
- No explicit baseline for EHT horizon and observer-memory proxy runs

## Output Paths

- `empirical/outputs/data/`
- `empirical/outputs/metrics/`
- `empirical/outputs/figures/`
- `empirical/outputs/reports/`
- `empirical/outputs/manifests/`

The aggregate runner also writes:

- `empirical/outputs/metrics/empirical_comparison_summary.csv`
- `empirical/outputs/reports/empirical_comparison_summary.md`
- `empirical/outputs/manifests/empirical_comparison_metadata.json`

## Interpretation Guide

- Treat all results here as fixture-backed comparison diagnostics.
- Residuals and fitted parameters are derived comparison metrics, not observational confirmation.
- A lower residual against a fixture baseline is still not an empirical validation claim.
- These outputs are suitable as repository-linked supplementary computational artifacts for later manuscript references.

## Limitations

- Synthetic or curated test fixtures only in this run
- No network acquisition
- No direct claims about real-world astrophysical truth conditions
- No substitute for manuscript proofs or formal derivations
