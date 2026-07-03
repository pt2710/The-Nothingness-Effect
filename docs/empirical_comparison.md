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
- Observer memory waveform-style comparison
- Elastic-pi ringdown comparison

Noether and fp-Gauss outputs remain internal consistency diagnostics rather than direct empirical comparisons.

Hawking-radiation is not treated as a direct empirical fetched-data target in this layer. It is handled separately under `theoretical_benchmarks/hawking/`.

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
- `theoretical_benchmark`: used outside this empirical layer for Hawking benchmark artifacts.

Default tests do not require network. Fixture mode remains available even when public acquisition fails.

## Public Data Acquisition Modules

- `fetch_redshift_clock_data.py`
- `fetch_galaxy_rotation_data.py`
- `fetch_eht_observables.py`
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
- LIGO / GWOSC:
  lightweight GW150914-derived ringdown segment from public strain data when the optional HDF5 reader is available.

## Model-to-Observable Mappings

- `dubler_redshift_mapping.py`: maps Dubler-shift outputs to a redshift benchmark adapter.
- `spiral_galaxy_mapping.py`: maps locality-driven particle dynamics plus entropic-elastic morphology diagnostics to radial rotation-curve observables.
- `horizon_eht_mapping.py`: maps horizon-radius proxies to ring/shadow observables through a fitted angular scale.
- `observer_memory_mapping.py`: maps black-hole memory-like traces to waveform-style comparison data.
- `ripple_ringdown_mapping.py`: maps elastic-pi ringdown traces against a damped-sinusoid baseline and waveform-style comparison data.

## Baseline Models

- Published or fixture baseline shift for Dubler redshift
- Flat or linear simple baselines for spiral rotation
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
- `empirical/outputs/reports/empirical_audit_run6.md`
- `empirical/outputs/metrics/empirical_audit_run6.csv`
- `empirical/outputs/manifests/empirical_audit_run6.json`

## Run 6 Empirical Audit and Mapping Improvements

Run 6 audits the empirical outputs and improves observable mappings and residual diagnostics while preserving fixture/offline/fetched/cached support.

What was audited:

- aggregate empirical summary, per-comparison manifests, and per-comparison reports
- redshift, galaxy, EHT, observer-memory, and ringdown mapping modules
- source-registry and fetch-all behavior
- `fields_of_physics_in_dev/` reuse candidates

What was improved:

- Dubler redshift:
  explicit sign convention, bounded fit metadata, residual diagnostics
- Spiral rotation:
  tangential-velocity extraction, bounded deterministic parameter sweep, simple baseline family, morphology diagnostics, and multi-galaxy SPARC fitting
- EHT horizon:
  threshold-crossing proxy audit, uncertainty-aware residuals, shared-scale vs per-source diagnostics
- Observer memory:
  time-shift and residual-envelope diagnostics with explicit weak-fit reporting
- Elastic-pi ringdown:
  aligned ringdown window, raw and normalized strain columns, explicit TNE projection, residual-envelope plots, and holdout diagnostics

Current best empirical candidate:

- Dubler redshift remains the strongest small-benchmark residual fit, but it is a tiny curated/cached benchmark and must not be overstated.

Current weakest empirical comparisons:

- observer memory remains weak
- ringdown remains difficult and the damped-sinusoid baseline may still be stronger
- spiral rotation remains a finite toy rotation-curve proxy rather than a full astrophysical model
- improved morphology does not convert the result into empirical validation

## Locality-Driven Spiral Rework

The spiral-galaxy side now uses an explicit body-and-field feedback model:

- mass-bearing bodies deform a density-derived locality field
- the locality field produces an entropic-elastic tension proxy
- gravity plus elastic-tension gradients feed back into body motion
- differential rotation and seeded asymmetry wind the disk into stronger arm-like structure

The empirical SPARC comparison still remains preliminary. It is a repository-linked computational support artifact, not a dark-matter-replacement claim, not a full astrophysical simulation, and not an empirical validation claim.

Additional spiral diagnostics now exposed to the empirical layer include:

- `mode_1_amplitude`
- `mode_2_amplitude`
- `mode_3_amplitude`
- `mode_4_amplitude`
- `dominant_mode`
- `dominant_mode_amplitude`
- `target_mode_amplitude`
- `target_mode_ratio`
- `density_arm_contrast`
- `angular_momentum_drift`
- `elastic_tension_max`
- `arm_asymmetry_index`

The spiral mapping can now run a bounded arm-mode sweep over `2`, `3`, `4`, and `mixed`. If one mode fits better under the implemented proxy mapping, it should be described only as the best preliminary residual fit under that mapping. It is not a morphology validation claim.

The spiral comparison now also records:

- per-galaxy RMSE / MAE / R2 diagnostics
- per-galaxy baseline winner and TNE winner flag
- bounded galaxy holdout diagnostics when feasible with the current dataset size
- initialization-vs-evolution and field-feedback diagnostics from the locality-driven toy model

The ringdown comparison now also records:

- window sensitivity over multiple fixed aligned ringdown windows
- basis stability under leave-one-component-out ablations
- explicit train/test diagnostics under the same normalization and split for both TNE and the damped-sinusoid baseline

These additions strengthen transparency and generalization diagnostics, but they still do not convert the outputs into empirical validation.

Metric interpretation:

- RMSE / MAE measure residual size under the implemented proxy mapping
- R2 is descriptive only and can be weak even when a qualitative trend is visible
- weighted RMSE and chi-square use the available uncertainty columns when present
- AIC / BIC remain lightweight model-comparison diagnostics, not validation criteria

Residual comparison is not validation:

- improved residuals do not prove TNE
- fetched public data remain preliminary comparison inputs
- these outputs are not full GR, QFT, GRMHD, or full astrophysical simulation

How to run the Run 6 audit mode:

```bash
python -m empirical.comparison.run_empirical_comparisons --offline --use-fixtures --dataset all --audit
python -m empirical.comparison.run_empirical_comparisons --dataset all --audit
python -m empirical.audit.run_fields_of_physics_in_dev_audit
```

## Interpretation Guide

- Treat all outputs here as preliminary comparison artifacts.
- A fetched public dataset still does not convert the run into empirical validation.
- Residuals, fits, and scalings are derived comparison metrics, not direct confirmation.
- Fixture fallback remains valid for reproducibility when public data are unavailable.
- These outputs are suitable as repository-linked supplementary computational artifacts for later manuscript references.
- Hawking benchmark outputs belong under `theoretical_benchmarks/hawking/` and should be cited as theoretical consistency artifacts rather than empirical comparisons.

## Known Limitations

- Some sources are summary-observable or curated-benchmark inputs rather than raw instrument products.
- The LIGO-derived ringdown product in this run is a lightweight single-detector proxy, not a full collaboration-grade inference result.
- The galaxy rotation output in this run stores a compact representative curve rather than the full catalog.
- None of these outputs should be described as empirical proof, proof-by-simulation, full-GR/QFT validation, or full astrophysical confirmation.
