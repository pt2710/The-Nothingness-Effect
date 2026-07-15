from __future__ import annotations

import json

import pytest

from the_nothingness_effect.fluctuation_and_elastic_dynamics.artifacts import run_suite


@pytest.mark.parametrize(
    ("category", "count"),
    (("dfi", 6), ("pdfi", 10), ("elastic_pi", 7), ("elastic_pi_norm", 8)),
)
def test_fluctuation_elastic_artifacts_have_theorem_manifests(tmp_path, category, count):
    outputs = run_suite(category, tmp_path / category, seed=0)

    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == count
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["seed"] == 0
        assert payload["appendix_source_sha256"] == "3277f0ffffcc27dc37ed17f7ecf721ba32234706544ceb5cfbeb5538846f2ba2"
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
