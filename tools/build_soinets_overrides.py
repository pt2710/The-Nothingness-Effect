"""Generate theorem-inventory overrides for the implemented SOInet chain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from the_nothingness_effect.artificial_intelligence.soinets.contracts import A_IDS, B_IDS, C_IDS


def build():
    result = {}
    for identifier in (*A_IDS, *B_IDS, *C_IDS):
        if identifier in A_IDS:
            note = "Typed SOInet modality source law with explicit domain, residual field, fail-closed boundary, and appendix-faithful B dependency."
        elif identifier in B_IDS:
            note = "Positive non-cancelling appendix residual energy uses both complete A sources with both-source removal witnesses."
        else:
            note = "Single modality-spatial field reports boundary, localization, reconstruction, coercivity, observability, both-B ablations, and numerical-candidate status."
        result[str(identifier)] = {
            "implementation_status": "implemented",
            "implementation_path": "the_nothingness_effect/artificial_intelligence/soinets/contracts.py",
            "test_path": "tests/contracts/test_soinets_contracts.py",
            "simulation_path": "the_nothingness_effect/artificial_intelligence/soinets/simulation/run_contract_suite.py",
            "artifact_status": "generator_smoke_tested",
            "decision_note": note,
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/data/implementation_status_overrides_soinets.json"))
    arguments = parser.parse_args()
    arguments.output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"soinets_overrides={len(build())} output={arguments.output}")
