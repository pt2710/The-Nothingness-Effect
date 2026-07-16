from __future__ import annotations

import json

from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.simulation.run_contract_suite import (
    run_suite,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.source_contracts import (
    SOURCE_IDS,
)


def test_dfi_suite_emits_base_derived_and_recertified_source_provenance(tmp_path):
    outputs = run_suite(tmp_path / "dfi", seed=0)

    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert outputs["extended_metrics"].is_file()
    assert len(outputs["manifests"]) == 11

    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in outputs["manifests"]
    ]
    identifiers = [payload["theorem_complex_id"] for payload in payloads]
    assert len(identifiers) == len(set(identifiers))
    assert set(SOURCE_IDS).issubset(identifiers)
    for payload in payloads:
        assert payload["claim_boundary"] == (
            "finite computational support; not a formal proof substitute"
        )
