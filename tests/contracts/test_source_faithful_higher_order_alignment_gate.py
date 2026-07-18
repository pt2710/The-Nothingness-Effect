"""Fail closed if any of the 23 audited formula corrections regresses."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

# Resolving the complete active registry imports the optional QENN backend.
# This gate therefore runs in the theorem/security partitions, which install
# the AI requirements, and is skipped only in the dev-only core partition.
pytest.importorskip("torch")

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import active_contracts
from tools.build_equation_implementation_alignment import SPECIALIZED_EVIDENCE_PATHS


MANIFEST = Path("docs/data/authority_overrides/source_faithful_higher_order.json")


def _declared_evidence(identifier: str, record: dict[str, object]) -> str:
    return SPECIALIZED_EVIDENCE_PATHS.get(identifier) or str(record["evidence_path"])


def test_all_23_formula_corrections_resolve_to_declared_source_faithful_evidence():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    overrides = payload["implementation_status_overrides"]
    assert len(overrides) == 23
    registry = {str(contract.complex_id): contract for contract in active_contracts()}
    assert set(overrides) <= set(registry)
    assert set(SPECIALIZED_EVIDENCE_PATHS) <= set(overrides)

    for identifier, record in overrides.items():
        evidence = _declared_evidence(identifier, record)
        assert evidence.endswith(".py")
        assert Path(evidence).is_file()
        contract = registry[identifier]
        assert contract.implementation_path == evidence
        assert "canonical_contracts.py" not in contract.implementation_path
        assert contract.source_removal_checks
        assert len(contract.source_removal_checks) == len(contract.source_ids)


def test_shared_source_faithful_modules_declare_operator_recomputation():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = {
        Path(record["evidence_path"])
        for identifier, record in payload["implementation_status_overrides"].items()
        if identifier not in SPECIALIZED_EVIDENCE_PATHS
    }
    assert len(paths) == 4
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "source_removal_result" in text
        assert "removed=_" in text or "removed = _" in text
        assert "np.zeros_like(complete" not in text
        assert "ablation_mode" in text


def test_specialized_formula_evidence_has_exact_recomputation_and_negative_tests():
    for identifier, evidence in SPECIALIZED_EVIDENCE_PATHS.items():
        implementation = Path(evidence)
        text = implementation.read_text(encoding="utf-8")
        assert "source_removal_result" in text
        assert "exact_semantics=True" in text
        assert "canonical_contracts.py" not in evidence
        test_path = Path("tests/contracts/test_parity_elastic_spectral_exact_closure.py")
        assert identifier == "parity_elastic_spectral_spatial_closure"
        assert test_path.is_file()
        test_text = test_path.read_text(encoding="utf-8")
        assert "remains_open" in test_text
        assert "source_removal_checks" in test_text
