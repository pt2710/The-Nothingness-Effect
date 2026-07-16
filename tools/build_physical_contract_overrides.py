"""Generate traceability overrides for the configured physical contract chains."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS


MODULE_PATHS = {
    "elastic_dubler_effect": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect",
    "elastic_dubler_interferometry": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature",
    "locality_driven_gravity": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity",
    "black_hole_dynamics": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons",
    "elastic_pi_ripples": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts",
    "cosmological_spark_dynamics": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/emergent_cosmological_spark_dynamics",
    "dtqc": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint",
}


def build() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for module, spec in sorted(SPECS.items()):
        path = MODULE_PATHS[module]
        for identifier in (*spec.a_ids, *spec.b_ids, spec.c_id):
            if identifier in spec.a_ids:
                note = "Typed physical source law with explicit spatial domain, boundary trace, invariant residual, and parameter failures."
            elif identifier in spec.b_ids:
                note = "Genuine bilinear derivation of two complete A laws with non-cancellation energy and both-source ablations."
            else:
                note = "Spatial closure has a local operator, boundary/localization diagnostics, coercivity, observability, both-B ablations, and numerical-candidate status."
            result[identifier] = {
                "implementation_status": "implemented",
                "implementation_path": f"{path}/contracts.py",
                "test_path": "tests/contracts/test_gravitational_contracts.py",
                "simulation_path": f"{path}/simulation/run_contract_suite.py",
                "artifact_status": "generator_smoke_tested",
                "decision_note": note,
            }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/data/implementation_status_overrides_physical.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"physical_contract_overrides={len(build())} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
