from __future__ import annotations

import json

from empirical.data_acquisition.source_registry import build_source_registry
from empirical.io import registry_output_path


def test_source_registry_manifest_is_fixture_only(tmp_path):
    registry = build_source_registry(tmp_path)
    manifest_path = registry_output_path(tmp_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest_path.exists()
    assert "claim_boundary" in payload
    assert set(registry) == {
        "redshift_clock",
        "galaxy_rotation",
        "eht_observables",
        "ligo_waveforms",
        "ligo_ringdown",
    }
    for entry in payload["registry"].values():
        assert entry["status"] == "fixture_only"
        assert entry["access_method"] == "offline_fixture"
        assert entry["output_paths"]
