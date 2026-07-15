from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.pgqenn.contracts import APPENDIX_SHA256
from the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite import run_suite


def test_pgqenn_suite_emits_seven_provenance_manifests(tmp_path):
    outputs = run_suite(tmp_path / "pgqenn", seed=0)
    assert outputs["metrics"].is_file() and outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 7
    for path in outputs["manifests"]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["parameters"]["growth_mode"] == "canonical_prime_parity"
        assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
