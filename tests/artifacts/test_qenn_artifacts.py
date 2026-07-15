from __future__ import annotations

import json

from equations.artificial_intelligence.qenn.contracts import APPENDIX_SHA256
from equations.artificial_intelligence.qenn.simulation.run_contract_suite import run_suite


def test_qenn_suite_emits_seven_provenance_manifests(tmp_path):
    outputs = run_suite(tmp_path / "qenn", seed=0)
    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 7
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
        assert payload["approximation_metadata"]["device"] == "cpu"
