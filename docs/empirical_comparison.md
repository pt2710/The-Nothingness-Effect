# Empirical Comparison Pipeline

## Purpose

These empirical comparison scripts are preliminary reproducible comparison tools. They do not establish empirical validation of TNE. They map dimensionless TNE proxy outputs to observable quantities through explicit fitted or calibrated adapters and compare residuals against available empirical or published reference data.

This layer is a repository-linked computational support artifact. It is not a formal proof substitute.

## Claim Boundary

- Public data acquisition and comparison are implemented here, not empirical validation.
- Residual comparison does not prove TNE.
- A fetched public dataset is still only a preliminary comparison input.
- These scripts do not replace formal proof in the manuscript.
- These scripts do not constitute full GR, QFT, GRMHD, or full astrophysical simulation.

Unavailable sources are not silently treated as evidence. They either remain `manual_required`, `unavailable`, or fall back to `fixture_only` when that safe fallback is enabled.

## Supported Targets

- Dubler redshift / clock benchmark comparison
- Spiral galaxy rotation curve comparison
- EHT ring / shadow observable comparison
- Hawking-like analogue or limit-style proxy comparison
- Observer memory waveform-style comparison
- Elastic-pi ringdown comparison

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
  cache/
  tests/
```

## Core Commands

Offline fixture-backed comparison:

```bash
python -m empirical.comparison.run_empirical_comparisons --offline --use-fixtures --dataset all
```

Attempt public data acquisition:

```bash
python -m empirical.data_acquisition.fetch_all_empirical_data --dataset all
```

Run comparisons using fetched/cached data with documented fixture fallback:

```bash
python -m empirical.comparison.run_empirical_comparisons --dataset all
```

Fetch before compare in one command:

```bash
python -m empirical.comparison.run_empirical_comparisons --fetch --dataset all
```

## Data Modes

- `fetched`: a public dataset or raw file was retrieved in the current or a previous run and a lightweight derived dataset is available.
- `cached`: a lightweight derived dataset from a public or curated published source is already present locally.
- `fixture_only`: deterministic fixture fallback data are being used.
- `manual_required`: the source family is known, but safe automated compact acquisition was not completed in this run.
- `unavailable`: acquisition was attempted but no usable derived dataset was produced.

Default tests do not require network. Fixture mode remains available even when public acquisition fails.

## Public Data Acquisition Modules

- `fetch_redshift_clock_data.py`
- `fetch_galaxy_rotation_data.py`
- `fetch_eht_observables.py`
- `fetch_hawking_analogue_or_limits.py`
- `fetch_ligo_waveforms.py`
- `fetch_all_empirical_data.py`

Each acquisition script writes a provenance manifest under `empirical/outputs/manifests/` and a lightweight derived dataset under `empirical/outputs/data/` when feasible.

## Dataset-Specific Provenance

- Redshift / clock:
  curated benchmark table from published Pound-Rebka and Gravity Probe A values when a structured raw public table is not readily available.
- Galaxy rotation:
  derived compact CSV from the public SPARC `Rotmod_LTG.zip` archive.
- EHT:
  compact published summary observables for M87* and Sgr A*, not raw imaging products.
- Hawking analogue or PBH limits:
  source family recorded, but automatic compact dataset generation may remain manual.
- LIGO / GWOSC:
  lightweight GW150914-derived ringdown segment from public strain data when the optional HDF5 reader is available.

## Model-to-Observable Mappings

- `dubler_redshift_mapping.py`: maps Dubler-shift outputs to a redshift benchmark adapter.
- `spiral_galaxy_mapping.py`: maps locality-driven particle dynamics to radial rotation-curve observables.
- `horizon_eht_mapping.py`: maps horizon-radius proxies to ring/shadow observables through a fitted angular scale.
- `hawking_flux_mapping.py`: maps flux proxies to analogue/limit-style comparison curves.
- `observer_memory_mapping.py`: maps black-hole memory-like traces to waveform-style comparison data.
- `ripple_ringdown_mapping.py`: maps elastic-pi ringdown traces against a damped-sinusoid baseline and waveform-style comparison data.

## Baseline Models

- Published or fixture baseline shift for Dubler redshift
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

Aggregate outputs:

- `empirical/outputs/metrics/data_acquisition_summary.csv`
- `empirical/outputs/manifests/data_acquisition_summary.json`
- `empirical/outputs/metrics/empirical_comparison_summary.csv`
- `empirical/outputs/reports/empirical_comparison_summary.md`
- `empirical/outputs/manifests/empirical_comparison_metadata.json`

## Interpretation Guide

- Treat all outputs here as preliminary comparison artifacts.
- A fetched public dataset still does not convert the run into empirical validation.
- Residuals, fits, and scalings are derived comparison metrics, not direct confirmation.
- Fixture fallback remains valid for reproducibility when public data are unavailable.
- These outputs are suitable as repository-linked supplementary computational artifacts for later manuscript references.

## Known Limitations

- Some sources are summary-observable or curated-benchmark inputs rather than raw instrument products.
- Hawking-related public compact datasets may require manual follow-up curation.
- The LIGO-derived ringdown product in this run is a lightweight single-detector proxy, not a full collaboration-grade inference result.
- The galaxy rotation output in this run stores a compact representative curve rather than the full catalog.
- None of these outputs should be described as empirical proof, proof-by-simulation, full-GR/QFT validation, or full astrophysical confirmation.
