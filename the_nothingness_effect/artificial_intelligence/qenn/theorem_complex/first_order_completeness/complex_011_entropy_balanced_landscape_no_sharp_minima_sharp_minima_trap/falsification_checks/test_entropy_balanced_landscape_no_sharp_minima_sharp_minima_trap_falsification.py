"""Fail-closed falsification metadata check for entropy_balanced_landscape_no_sharp_minima_sharp_minima_trap."""

import json
from pathlib import Path


def test_falsification_obligations_are_explicit():
    manifest = json.loads((Path(__file__).resolve().parents[1] / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["complex_id"] == 'entropy_balanced_landscape_no_sharp_minima_sharp_minima_trap'
    assert manifest["status"] in {"implemented", "partial", "proxy", "blocked", "not_applicable"}
    assert manifest["falsification"]["obligations"]
    if manifest["status"] != "implemented":
        assert manifest["falsification"]["execution_status"] in {"proxy", "not_directly_computable", "blocked"}
