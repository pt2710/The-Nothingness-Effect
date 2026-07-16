from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.soinets.contracts import (
    APPENDIX_SHA256,
)
from the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite import (
    run_suite,
)
from the_nothingness_effect.artificial_intelligence.soinets.source_contracts import (
    SOURCE_IDS,
)


def test_soinets_suite_emits_full_native_provenance(tmp_path):
    outputs = run_suite(tmp_path / "soinets", seed=0)
    assert outputs["metrics"].is_file() and outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 21

    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in outputs["manifests"]
    ]
    manifested = {payload["theorem_complex_id"] for payload in payloads}
    assert set(map(str, SOURCE_IDS)).issubset(manifested)
    for payload in payloads:
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["parameters"]["modality_count"] == 3
        assert payload["claim_boundary"] == (
            "finite computational support; not a formal proof substitute"
        )
        assert payload["approximation_metadata"]["authority_bound"] is True
