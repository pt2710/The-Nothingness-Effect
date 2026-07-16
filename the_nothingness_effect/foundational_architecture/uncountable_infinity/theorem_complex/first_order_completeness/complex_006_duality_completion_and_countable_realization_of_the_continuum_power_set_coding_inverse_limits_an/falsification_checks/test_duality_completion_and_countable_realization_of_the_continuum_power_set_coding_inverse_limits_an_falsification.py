"""Fail-closed falsification metadata check for duality_completion_and_countable_realization_of_the_continuum_power_set_coding_inverse_limits_and_de."""

import json
from pathlib import Path


def test_falsification_obligations_are_explicit():
    manifest = json.loads((Path(__file__).resolve().parents[1] / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["complex_id"] == 'duality_completion_and_countable_realization_of_the_continuum_power_set_coding_inverse_limits_and_de'
    assert manifest["status"] in {"implemented", "partial", "proxy", "blocked", "not_applicable"}
    assert manifest["falsification"]["obligations"]
    if manifest["status"] != "implemented":
        assert manifest["falsification"]["execution_status"] in {"proxy", "not_directly_computable", "blocked"}
