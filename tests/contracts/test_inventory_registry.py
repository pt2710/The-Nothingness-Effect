from __future__ import annotations

import json
from pathlib import Path

from tne_runtime.theorem_complex_runtime.registry import TheoremComplexRegistry


ROOT = Path(__file__).resolve().parents[2]


def test_inventory_has_exact_a_b_c_counts_and_unique_ids():
    registry = TheoremComplexRegistry.from_csv(
        ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    )
    assert registry.counts() == {
        "total": 351,
        "A": 204,
        "B": 98,
        "C": 49,
        "inventory_implemented": 136,
        "registered_contracts": 0,
    }
    assert len({str(record.complex_id) for record in registry.inventory()}) == 351


def test_external_label_verification_is_complete():
    payload = json.loads(
        (ROOT / "docs/data/appendix_source_verification.json").read_text(encoding="utf-8")
    )
    assert payload["appendix_checksum_verified"] is True
    assert payload["verified_appendix_files"] == 7
    assert payload["verified_first_labels"] == 351
    assert payload["missing_first_labels"] == 0
    assert payload["missing_equation_labels"] == 0
