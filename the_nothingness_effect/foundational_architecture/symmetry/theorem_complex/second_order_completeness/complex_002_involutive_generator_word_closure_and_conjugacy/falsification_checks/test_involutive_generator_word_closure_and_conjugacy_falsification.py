"""Fail-closed falsification metadata check for involutive_generator_word_closure_and_conjugacy."""

import json
from pathlib import Path


def test_falsification_obligations_are_explicit():
    manifest = json.loads((Path(__file__).resolve().parents[1] / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["complex_id"] == 'involutive_generator_word_closure_and_conjugacy'
    assert manifest["status"] in {"implemented", "partial", "proxy", "blocked", "not_applicable"}
    assert manifest["falsification"]["obligations"]
    if manifest["status"] != "implemented":
        assert manifest["falsification"]["execution_status"] in {"proxy", "not_directly_computable", "blocked"}
