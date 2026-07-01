# Empirical Comparison Summary

These empirical comparison scripts are preliminary reproducible comparison tools. They do not establish empirical validation of TNE. They map dimensionless TNE proxy outputs to observable quantities through explicit fitted or calibrated adapters and compare residuals against available empirical or published reference data.

Run mode:
- fetch attempted: False
- offline: False
- fixture fallback enabled: True
- selected_datasets: redshift, galaxy, eht, hawking, memory, ringdown

Claim boundary:
- preliminary comparison only
- not an empirical validation claim
- not a formal proof substitute

Summary rows:
- redshift_clock: RMSE=0.095749, MAE=0.069910, status=cached, passed_validation=True
- galaxy_rotation: RMSE=0.189057, MAE=0.153404, status=fetched, passed_validation=True
- eht_observables: RMSE=9.505718, MAE=8.235119, status=cached, passed_validation=True
- hawking_analogue_or_limits: RMSE=0.254395, MAE=0.222045, status=fixture_only, passed_validation=True
- ligo_waveforms: RMSE=0.420862, MAE=0.346418, status=fetched, passed_validation=True
- ligo_ringdown: RMSE=0.420912, MAE=0.346635, status=fetched, passed_validation=True