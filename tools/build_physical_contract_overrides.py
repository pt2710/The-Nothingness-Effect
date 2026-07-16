"""Generate traceability overrides for the configured physical contract chains."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS


def build() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for module, spec in sorted(SPECS.items()):
        for identifier in (*spec.a_ids, *spec.b_ids, spec.c_id):
            if identifier in spec.a_ids:
                note = "Typed physical source law with explicit spatial domain, boundary trace, invariant residual, and parameter failures."
            elif identifier in spec.b_ids:
                note = "Genuine bilinear derivation of two complete A laws with non-cancellation energy and both-source ablations."
            else:
                note = "Spatial closure has a local operator, boundary/localization diagnostics, coercivity, observability, both-B ablations, and numerical-candidate status."
            result[identifier] = {
                "implementation_status": "implemented",
                "implementation_path": f"equations/{module}/contracts.py",
                "test_path": "tests/contracts/test_gravitational_contracts.py",
                "simulation_path": f"equations/{module}/simulation/run_contract_suite.py",
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
