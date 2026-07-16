from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.qenn.contracts import (
    APPENDIX_SHA256,
)
from the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite import (
    run_suite,
)
from the_nothingness_effect.artificial_intelligence.qenn.source_contracts import (
    SOURCE_IDS,
)


def test_qenn_suite_emits_full_native_provenance(tmp_path):
    outputs = run_suite(tmp_path / "qenn", seed=0)
    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 15

    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in outputs["manifests"]
    ]
    manifested = {payload["theorem_complex_id"] for payload in payloads}
    assert set(map(str, SOURCE_IDS)).issubset(manifested)
    for payload in payloads:
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["claim_boundary"] == (
            "finite computational support; not a formal proof substitute"
        )
        assert payload["approximation_metadata"]["device"] == "cpu"
        assert payload["approximation_metadata"]["authority_bound"] is True
