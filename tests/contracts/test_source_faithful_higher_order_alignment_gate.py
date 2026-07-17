"""Fail closed if any of the 23 audited formula corrections regresses."""
from __future__ import annotations

import json
from pathlib import Path

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import active_contracts


MANIFEST=Path("docs/data/authority_overrides/source_faithful_higher_order.json")


def test_all_23_formula_corrections_resolve_to_source_faithful_evidence():
    payload=json.loads(MANIFEST.read_text(encoding="utf-8"))
    overrides=payload["implementation_status_overrides"]
    assert len(overrides)==23
    registry={str(contract.complex_id):contract for contract in active_contracts()}
    assert set(overrides)<=set(registry)

    for identifier,record in overrides.items():
        evidence=record["evidence_path"]
        assert evidence.endswith("/source_faithful_contracts.py")
        assert Path(evidence).is_file()
        contract=registry[identifier]
        assert contract.implementation_path==evidence
        assert "canonical_contracts.py" not in contract.implementation_path
        assert contract.source_removal_checks
        assert len(contract.source_removal_checks)==len(contract.source_ids)


def test_source_faithful_modules_declare_operator_recomputation():
    payload=json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths={
        Path(record["evidence_path"])
        for record in payload["implementation_status_overrides"].values()
    }
    assert len(paths)==4
    for path in paths:
        text=path.read_text(encoding="utf-8")
        assert "source_removal_result" in text
        assert "removed=_" in text or "removed = _" in text
        assert "np.zeros_like(complete" not in text
        assert "ablation_mode" in text
