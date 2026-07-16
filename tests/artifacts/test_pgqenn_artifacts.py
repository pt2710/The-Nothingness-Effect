from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.pgqenn.contracts import (
    APPENDIX_SHA256,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.mpl_tc_dependency import (
    MPL_TC_MODULE_SHA256,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite import (
    run_suite,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.source_contracts import (
    SOURCE_IDS,
)


def test_pgqenn_suite_emits_full_native_provenance(tmp_path):
    outputs = run_suite(tmp_path / "pgqenn", seed=0)
    assert outputs["metrics"].is_file() and outputs["figure"].is_file()
    assert len(outputs["manifests"]) == 13

    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in outputs["manifests"]
    ]
    manifested = {payload["theorem_complex_id"] for payload in payloads}
    assert set(map(str, SOURCE_IDS)).issubset(manifested)
    for payload in payloads:
        assert payload["appendix_source_sha256"] == APPENDIX_SHA256
        assert payload["parameters"]["growth_mode"] == "mpl_tc_prime_motif"
        assert payload["parameters"]["mpl_tc_commit"] == (
            "056e346824e9ec9785ab45b642b3b842c88f6e56"
        )
        assert payload["parameters"]["mpl_tc_module_sha256"] == (
            MPL_TC_MODULE_SHA256
        )
        assert payload["claim_boundary"] == (
            "finite computational support; not a formal proof substitute"
        )
        assert payload["approximation_metadata"]["authority_bound"] is True
