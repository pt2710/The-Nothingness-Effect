from __future__ import annotations

import json
from pathlib import Path

from tools.build_final_qa_manifest_recertified import classify_simulation_evidence


def test_inventory_fallbacks_are_not_counted_as_simulations():
    manifest=json.loads(
        Path("reports/simulation_execution_manifest.json").read_text(encoding="utf-8")
    )
    report=classify_simulation_evidence(manifest)
    assert report["all_entrypoints_classified"] is True
    assert report["registered_entrypoints"]==37
    assert report["actual_simulation"]["entrypoints"]>0
    assert report["contract_evidence"]["entrypoints"]>0
    assert report["inventory_fallback"]["entrypoints"]>0
    assert report["unknown"]["entrypoints"]==0
    assert (
        report["actual_simulation"]["entrypoints"]
        + report["contract_evidence"]["entrypoints"]
        + report["inventory_fallback"]["entrypoints"]
        == report["registered_entrypoints"]
    )
    assert all(
        "inventory" not in path
        for path in report["actual_simulation"]["paths"]
    )
