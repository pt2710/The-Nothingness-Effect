from __future__ import annotations

import json

from equations.duality.simulation import run_suite


def test_duality_artifacts_write_six_manifests(tmp_path):
    outputs = run_suite(tmp_path, seed=0)
    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 6
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["seed"] == 0
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
