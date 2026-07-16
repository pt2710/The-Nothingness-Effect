from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.soinets.contracts import APPENDIX_SHA256
from the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite import run_suite


def test_soinets_suite_emits_seven_provenance_manifests(tmp_path):
    outputs = run_suite(tmp_path / "soinets", seed=0)
    assert outputs["metrics"].is_file() and outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 7
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["parameters"]["modality_count"] == 3
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
