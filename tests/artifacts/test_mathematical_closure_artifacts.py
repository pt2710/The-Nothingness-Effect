from __future__ import annotations

import json

from the_nothingness_effect.mathematical_architecture.simulation import run_suite


def test_mathematical_closure_artifacts_are_deterministic_and_bounded(tmp_path):
    first = run_suite(tmp_path / "first", seed=0)
    second = run_suite(tmp_path / "second", seed=0)
    assert first["metrics"].read_bytes() == second["metrics"].read_bytes()
    assert first["figure"].is_file()
    assert len(first["manifests"]) == 7
    for path in first["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
        assert payload["seed"] == 0
        assert len(payload["appendix_source_sha256"]) == 64
