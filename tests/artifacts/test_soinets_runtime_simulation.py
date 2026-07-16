from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.soinets.simulation.simulate_soinets import run


def test_soinets_simulation_uses_runtime_states_and_architecture_metrics(tmp_path):
    inventory_path = run(tmp_path / "soinets-runtime")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    manifest_path = inventory_path.parent / inventory["runtime_manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert inventory["architecture_coupled_metrics"] is True
    assert manifest["architecture_coupled_metrics"] is True
    assert manifest["source_status"] == "runtime_derived_architecture_coupled_fixture"
    assert 0.0 <= manifest["task_metrics"]["accuracy"] <= 1.0
    assert len(manifest["closure_statuses"]) == 3
    for filename in manifest["generated_files"]:
        assert (inventory_path.parent / filename).is_file()
