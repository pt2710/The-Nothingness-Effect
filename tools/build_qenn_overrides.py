"""Generate theorem-inventory overrides for the implemented QENN chain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from the_nothingness_effect.artificial_intelligence.qenn.contracts import A_IDS, B_IDS, C_IDS


def build():
    result = {}
    for identifier in (*A_IDS, *B_IDS, *C_IDS):
        if identifier in A_IDS:
            note = "Typed QENN source law with explicit domain, codomain, residual field, failure condition, and finite-input guard."
        elif identifier in B_IDS:
            note = "Positive non-cancelling appendix residual energy uses both complete A sources and two source-removal witnesses."
        else:
            note = "Single spatial defect field reports boundary, localization, reconstruction, coercivity, observability, both-B ablations, and numerical-candidate status."
        result[str(identifier)] = {
            "implementation_status": "implemented",
            "implementation_path": "the_nothingness_effect/artificial_intelligence/qenn/contracts.py",
            "test_path": "tests/contracts/test_qenn_contracts.py",
            "simulation_path": "the_nothingness_effect/artificial_intelligence/qenn/simulation/run_contract_suite.py",
            "artifact_status": "generator_smoke_tested",
            "decision_note": note,
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/data/implementation_status_overrides_qenn.json"))
    args = parser.parse_args()
    args.output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"qenn_overrides={len(build())} output={args.output}")
