"""Shared dataset-resolution helpers for empirical comparisons."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from empirical.data_acquisition.source_registry import (
    dataset_spec,
    load_dataset_manifest,
    public_dataset_path_for,
)
from empirical.io import fixture_path


COMPARISON_DATASETS: dict[str, dict[str, str]] = {
    "redshift": {
        "registry_key": "redshift_clock",
        "fixture_filename": "redshift_clock_fixture.csv",
    },
    "galaxy": {
        "registry_key": "galaxy_rotation",
        "fixture_filename": "galaxy_rotation_fixture.csv",
    },
    "eht": {
        "registry_key": "eht_observables",
        "fixture_filename": "eht_observable_fixture.csv",
    },
    "memory": {
        "registry_key": "ligo_waveforms",
        "fixture_filename": "ligo_ringdown_fixture.csv",
    },
    "ringdown": {
        "registry_key": "ligo_waveforms",
        "fixture_filename": "ligo_ringdown_fixture.csv",
    },
}


def resolve_input_dataset(
    comparison_key: str,
    *,
    output_dir: str | Path | None = None,
    use_fixtures: bool = True,
) -> dict[str, Any]:
    config = COMPARISON_DATASETS[comparison_key]
    registry_key = config["registry_key"]
    spec = dataset_spec(registry_key)
    manifest = load_dataset_manifest(registry_key, str(output_dir) if output_dir is not None else None)
    public_path = public_dataset_path_for(registry_key, str(output_dir) if output_dir is not None else None)
    status = manifest.get("status")

    if public_path.exists() and status in {"fetched", "cached"}:
        return {
            "path": public_path,
            "status": status,
            "manifest": manifest,
            "registry_key": registry_key,
            "dataset_name": spec["dataset_name"],
        }

    if use_fixtures:
        return {
            "path": fixture_path(config["fixture_filename"]),
            "status": "fixture_only",
            "manifest": manifest,
            "registry_key": registry_key,
            "dataset_name": spec["dataset_name"],
        }

    return {
        "path": None,
        "status": status or "unavailable",
        "manifest": manifest,
        "registry_key": registry_key,
        "dataset_name": spec["dataset_name"],
    }
