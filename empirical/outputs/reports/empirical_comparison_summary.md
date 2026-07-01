# Empirical Comparison Summary

These empirical comparison scripts are preliminary reproducible comparison tools. They do not establish empirical validation of TNE. They map dimensionless TNE proxy outputs to observable quantities through explicit fitted or calibrated adapters and compare residuals against available empirical or published reference data.

Run mode:
- offline: True
- use_fixtures: True
- selected_datasets: redshift, galaxy, eht, hawking, memory, ringdown

Claim boundary:
- fixture-backed comparison only
- not an empirical validation claim
- not a formal proof substitute

Summary rows:
- redshift_clock: RMSE=0.003286, MAE=0.002606, status=fixture_only, passed_validation=True
- galaxy_rotation: RMSE=0.115122, MAE=0.081257, status=fixture_only, passed_validation=True
- eht_observables: RMSE=9.505718, MAE=8.235119, status=fixture_only, passed_validation=True
- hawking_analogue_or_limits: RMSE=0.254395, MAE=0.222045, status=fixture_only, passed_validation=True
- ligo_ringdown_memory_proxy: RMSE=0.340718, MAE=0.268745, status=fixture_only, passed_validation=True
- ligo_ringdown: RMSE=0.353514, MAE=0.265606, status=fixture_only, passed_validation=True