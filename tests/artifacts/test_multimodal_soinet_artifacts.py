from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.soinets.multimodal import (
    MULTIMODAL_REFERENCE_SHA256,
)
from the_nothingness_effect.artificial_intelligence.soinets.multimodal_artifacts import (
    run_multimodal_artifact_suite,
)


def test_multimodal_soinet_artifacts_are_producer_local_and_reproducible(tmp_path):
    outputs = run_multimodal_artifact_suite(
        tmp_path / "soinets" / "simulation" / "artifacts" / "multimodal",
        seed=0,
        simulation=True,
    )

    assert outputs["metrics"].is_file()
    assert outputs["figure"].is_file()
    assert outputs["animation"].is_file()
    payload = json.loads(outputs["manifest"].read_text(encoding="utf-8"))
    assert payload["external_reference_context_sha256"] == MULTIMODAL_REFERENCE_SHA256
    assert payload["dependency_chain"] == [
        "DTQC->QENN",
        "QENN+MPL-TC->PGQENN",
        "QENN+PGQENN->SOInet",
    ]
    assert payload["source_status"] == "synthetic_deterministic_fixture"
    assert "not a formal proof substitute" in payload["claim_boundary"]
