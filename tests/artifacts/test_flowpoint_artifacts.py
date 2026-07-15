from __future__ import annotations

import json

from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.simulation import run_suite


def test_flowpoint_artifacts_have_seven_reproducible_manifests(tmp_path):
    first = run_suite(tmp_path / "first", seed=0)
    second = run_suite(tmp_path / "second", seed=0)
    assert first["metrics"].read_text(encoding="utf-8") == second["metrics"].read_text(
        encoding="utf-8"
    )
    assert first["figure"].is_file()
    assert len(first["manifests"]) == 7
    for path in first["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["seed"] == 0
        assert payload["appendix_source_sha256"]
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
        assert payload["generated_files"] == ["flowpoint_metrics.csv", "flowpoint_trace.png"]
