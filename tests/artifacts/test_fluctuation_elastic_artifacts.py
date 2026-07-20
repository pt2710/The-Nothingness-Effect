from __future__ import annotations

import json

import pytest
from the_nothingness_effect.fluctuation_and_elastic_dynamics.artifacts import run_suite


@pytest.mark.parametrize(
    ("category", "count"),
    (("dfi", 8), ("pdfi", 10), ("elastic_pi", 7), ("elastic_pi_norm", 8)),
)
def test_fluctuation_elastic_artifacts_have_theorem_manifests(tmp_path, category, count):
    outputs = run_suite(category, tmp_path / category, seed=0)

    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == count
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["seed"] == 0
        assert payload["appendix_source_sha256"] == "63e5684e4c4bb016a2cc62d46574c2174fbe14eb5f50c16db825ca33b0836389"
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
