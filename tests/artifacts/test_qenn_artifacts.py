from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.qenn.contracts import (
    APPENDIX_SHA256,
)
from the_nothingness_effect.artificial_intelligence.qenn.authoritative_contracts import (
    contracts as authoritative_contracts,
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
    expected = {str(contract.complex_id) for contract in authoritative_contracts()}
    assert len(outputs["manifests"]) == len(expected) == 21

    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in outputs["manifests"]]
    manifested = {payload["theorem_complex_id"] for payload in payloads}
    assert set(map(str, SOURCE_IDS)).issubset(manifested)
    assert manifested == expected
    for payload in payloads:
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["claim_boundary"] == ("finite computational support; not a formal proof substitute")
        assert payload["approximation_metadata"]["authority_bound"] is True
        assert payload["approximation_metadata"]["exact_semantics"] is True
        assert payload["approximation_metadata"]["formal_proof_verified"] is False
