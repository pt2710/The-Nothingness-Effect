# Empirical Comparison Summary

These empirical comparison scripts are preliminary reproducible comparison tools. They do not establish empirical validation of TNE. They map dimensionless TNE proxy outputs to observable quantities through explicit fitted or calibrated adapters and compare residuals against available empirical or published reference data.

Run mode:
- fetch attempted: False
- offline: False
- fixture fallback enabled: True
- selected_datasets: redshift, galaxy, eht, memory, ringdown
- audit enabled: True
- improve flag: False
- parameter_sweep_level: standard

Claim boundary:
- preliminary comparison only
- not an empirical validation claim
- not a formal proof substitute
- Hawking is handled separately as a theoretical benchmark

Summary rows:
- redshift_clock: RMSE=0.009231, MAE=0.008960, status=cached, passed_validation=True
- galaxy_rotation: RMSE=0.133384, MAE=0.094393, status=fetched, passed_validation=True
- eht_observables: RMSE=0.411214, MAE=0.367623, status=cached, passed_validation=True
- ligo_waveforms: RMSE=0.420622, MAE=0.345753, status=fetched, passed_validation=True
- ligo_ringdown: RMSE=0.379599, MAE=0.306026, status=fetched, passed_validation=True