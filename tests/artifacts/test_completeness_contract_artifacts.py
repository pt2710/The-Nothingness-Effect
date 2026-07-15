from __future__ import annotations

import json

from equations.completeness_theorem.contracts import APPENDIX_SHA256
from equations.completeness_theorem.simulation.run_contract_suite import run_suite


def test_completeness_contract_artifacts_write_fifteen_manifests(tmp_path):
    outputs = run_suite(tmp_path, seed=0)

    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 15
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
        assert payload["approximation_metadata"]["formal_proof_substitute"] is False
