# Run 6 Empirical Audit

This report audits the current empirical comparison outputs after the Run 6 mapping-improvement pass. It remains a preliminary observable-mapping audit, not an empirical validation claim.

## Current Comparison Summary

| Dataset | Status | RMSE | MAE | R2 | Baseline |
| --- | --- | ---: | ---: | ---: | --- |
| redshift_clock | cached | 0.009231 | 0.008960 | 0.999659 | published_or_fixture_baseline_shift |
| galaxy_rotation | fetched | 0.137123 | 0.095789 | 0.528809 | multi_galaxy_baseline_family |
| eht_observables | cached | 0.411214 | 0.367623 | 0.998891 | none |
| ligo_waveforms | fetched | 0.420622 | 0.345753 | 0.001465 | none |
| ligo_ringdown | fetched | 0.379599 | 0.306026 | 0.165303 | damped_sinusoid_baseline |

## Diagnosis by Model

### redshift_clock

- classification: empirical_comparison
- current limitation: Small benchmark comparison only
- diagnosis: Small-sample benchmark with strong residual fit, but unit/sign interpretation and baseline provenance remain the main risks.
- implemented in Run 6: Explicit sign-convention metadata, bounded fit metadata, residual diagnostics, and report-level formula documentation.
- deferred: Additional holdout analysis is not meaningful with only two benchmark rows.

### galaxy_rotation

- classification: empirical_comparison
- current limitation: Not a full astrophysical interpretation
- diagnosis: The main weakness is observable mapping and parameter regime selection, not raw data availability. Rotation-curve proxy quality depends strongly on radial binning and bounded parameter sweeps.
- implemented in Run 6: Tangential-velocity extraction, bounded deterministic parameter sweep, simple baseline family, and morphology diagnostics.
- deferred: Full multi-galaxy catalog support and stronger astrophysical calibration remain future work.

### eht_observables

- classification: empirical_comparison
- current limitation: Published summary observables only
- diagnosis: The limiting factor is summary-observable mapping and angular scaling rather than missing raw imaging products. Shared-scale fits remain coarse; per-source scaling is diagnostic only.
- implemented in Run 6: Threshold-crossing proxy audit, weighted residuals, shared-scale vs per-source diagnostics, and residual plots.
- deferred: No GRMHD image reconstruction or instrument forward model is included.

### ligo_waveforms

- classification: empirical_comparison
- current limitation: Memory proxy uses waveform-style comparison data
- diagnosis: Observer-memory proxy alignment remains weak. The main issue is model sufficiency relative to waveform morphology, not dataset access.
- implemented in Run 6: Residual-envelope diagnostics and clearer weak-fit documentation.
- deferred: A richer waveform-adapter family would be needed for stronger proxy alignment.

### ligo_ringdown

- classification: empirical_comparison
- current limitation: Finite toy-model ringdown comparison only
- diagnosis: Ringdown alignment is limited by proxy projection quality and short noisy segment selection. The baseline remains competitive or better under the same window.
- implemented in Run 6: Window alignment, raw/normalized strain columns, bounded TNE projection search, holdout diagnostics, and residual-envelope outputs.
- deferred: A stronger reduced-order TNE waveform family would be required to outperform the damped-sinusoid baseline consistently.

## Classification Split

- empirical comparisons: redshift, galaxy rotation, EHT horizon, observer memory, elastic-pi ringdown
- theoretical benchmarks: Hawking temperature/power/evaporation/spectrum comparison
- internal consistency diagnostics: Noether/fp-Gauss remain outside the empirical summary

## Claim Boundary

Improved fit metrics, if any, are preliminary model-to-observable comparison results under explicit proxy mappings. Residual diagnostics here do not establish empirical validation of TNE.