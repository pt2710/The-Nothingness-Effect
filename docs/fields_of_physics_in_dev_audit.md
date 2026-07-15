# fields_of_physics_in_dev Audit

This audit reviews the development-only physics folders for Run 6 reuse opportunities. Recommendations are conservative and focus on tested, directly useful integration only.

## Summary

| Path | Status | Tests | Simulation Output | Recommended Action | Risk |
| --- | --- | --- | --- | --- | --- |
| fields_of_physics_in_dev/general_relativity/gravitational_curvature | prototype | True | True | integrate_later | high |
| fields_of_physics_in_dev/general_relativity/three_body_problem | module_present | True | True | keep_experimental | medium |
| fields_of_physics_in_dev/quantum_mechanics/entanglement | prototype | True | True | keep_experimental | high |
| fields_of_physics_in_dev/quantum_mechanics/fp_particle_models | prototype | True | True | keep_experimental | medium |
| fields_of_physics_in_dev/quantum_mechanics/quantum_uncertainty | support_only | True | True | no_action | low |
| fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_pi_wave | prototype | True | True | integrate_now | medium |
| fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_sine_wave | prototype | True | True | integrate_now | medium |
| fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_wave_Interference | prototype | True | True | integrate_now | medium |
| fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_waves | prototype | True | True | integrate_later | medium |
| fields_of_physics_in_dev/thermodynamics | prototype | True | True | keep_experimental | medium |

## Integrated Now

- `fp_pi_wave`, `fp_sine_wave`, and `fp_wave_Interference` concepts were selectively integrated into `equations/elastic_pi_ripples/wave_adapters.py` for ringdown/spectral proxy helpers.

## Deferred / Experimental

- `gravitational_curvature` remains deferred because of legacy root imports, heavy ad hoc simulation assumptions, and missing isolation from side effects.
- entanglement, fp-particle, and thermodynamics modules remain experimental until a direct dependency or dedicated physics task requires them.

## Run 6 Note

Run 6 improves observable mappings and residual diagnostics. It does not establish empirical validation of TNE. Improved fit metrics, if any, are preliminary model-to-observable comparison results under explicit proxy mappings.