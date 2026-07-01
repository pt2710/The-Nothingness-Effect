"""Source-registry helpers for fetched, cached, and fixture-backed empirical data."""

from __future__ import annotations

from typing import Any

from empirical.io import (
    fixture_path,
    manifest_output_path,
    public_data_path,
    read_json,
    registry_output_path,
    repo_relative,
    write_manifest,
)


SOURCE_SPECS: dict[str, dict[str, Any]] = {
    "redshift_clock": {
        "dataset_name": "redshift_clock",
        "preferred_source": "Published gravitational redshift and clock benchmark literature",
        "source_url": "https://ntrs.nasa.gov/citations/19800011717",
        "expected_file_type": "csv",
        "fixture_filename": "redshift_clock_fixture.csv",
        "derived_filename": "redshift_clock_public_or_curated.csv",
        "manifest_filename": "redshift_clock_manifest.json",
        "citation_note": "Uses curated published benchmark values when structured raw files are unavailable.",
        "license_note": "Derived benchmark table for repository-linked comparison use.",
    },
    "galaxy_rotation": {
        "dataset_name": "galaxy_rotation",
        "preferred_source": "SPARC rotation-curve catalog",
        "source_url": "https://astroweb.case.edu/SPARC/Rotmod_LTG.zip",
        "expected_file_type": "csv",
        "fixture_filename": "galaxy_rotation_fixture.csv",
        "derived_filename": "galaxy_rotation_public.csv",
        "manifest_filename": "galaxy_rotation_manifest.json",
        "citation_note": "Derived from public SPARC rotation-curve tables.",
        "license_note": "Retain SPARC citation and usage notice in downstream manuscript references.",
    },
    "eht_observables": {
        "dataset_name": "eht_observables",
        "preferred_source": "Published Event Horizon Telescope summary observables",
        "source_url": "https://arxiv.org/abs/1906.11241",
        "expected_file_type": "csv",
        "fixture_filename": "eht_observable_fixture.csv",
        "derived_filename": "eht_public_observables.csv",
        "manifest_filename": "eht_observables_manifest.json",
        "citation_note": "Compact derived observables from published EHT summary results.",
        "license_note": "Derived summary values only; no raw image products are stored here.",
    },
    "ligo_waveforms": {
        "dataset_name": "ligo_waveforms",
        "preferred_source": "GWOSC public strain archive",
        "source_url": "https://gwosc.org/api/v2/strain-files/H1-1126259446-4kHz",
        "expected_file_type": "csv",
        "fixture_filename": "ligo_ringdown_fixture.csv",
        "derived_filename": "ligo_gw150914_ringdown.csv",
        "manifest_filename": "ligo_waveforms_manifest.json",
        "citation_note": "Derived ringdown segment from GWOSC public strain data.",
        "license_note": "Retain GWOSC/LIGO citation guidance when linking from the manuscript.",
    },
    "ligo_ringdown": {
        "dataset_name": "ligo_ringdown",
        "preferred_source": "GWOSC public strain archive",
        "source_url": "https://gwosc.org/api/v2/strain-files/H1-1126259446-4kHz",
        "expected_file_type": "csv",
        "fixture_filename": "ligo_ringdown_fixture.csv",
        "derived_filename": "ligo_gw150914_ringdown.csv",
        "manifest_filename": "ligo_waveforms_manifest.json",
        "citation_note": "Derived ringdown segment from GWOSC public strain data.",
        "license_note": "Retain GWOSC/LIGO citation guidance when linking from the manuscript.",
    },
}


def dataset_spec(key: str) -> dict[str, Any]:
    return SOURCE_SPECS[key]


def dataset_manifest_path(key: str, output_dir: str | None = None):
    spec = dataset_spec(key)
    return manifest_output_path(spec["manifest_filename"], output_dir)


def load_dataset_manifest(key: str, output_dir: str | None = None) -> dict[str, Any]:
    payload = read_json(dataset_manifest_path(key, output_dir), default={})
    return payload if isinstance(payload, dict) else {}


def default_registry_entry(key: str, output_dir: str | None = None) -> dict[str, Any]:
    spec = dataset_spec(key)
    return {
        "dataset_name": spec["dataset_name"],
        "preferred_source": spec["preferred_source"],
        "source_url": spec["source_url"],
        "access_method": "offline_fixture",
        "expected_file_type": spec["expected_file_type"],
        "license_note": "Fixture-only synthetic or curated test data available as fallback.",
        "citation_note": spec["citation_note"],
        "status": "fixture_only",
        "last_attempted": "offline_fixture_fallback",
        "output_paths": [repo_relative(fixture_path(spec["fixture_filename"]))],
        "limitations": "No fetched or cached public dataset recorded yet.",
    }


def public_dataset_path_for(key: str, output_dir: str | None = None):
    spec = dataset_spec(key)
    return public_data_path(spec["derived_filename"], output_dir)


def build_registry_entry(key: str, output_dir: str | None = None) -> dict[str, Any]:
    default_entry = default_registry_entry(key, output_dir)
    manifest = load_dataset_manifest(key, output_dir)
    if not manifest:
        return default_entry

    derived_file = public_dataset_path_for(key, output_dir)
    output_paths = []
    raw_file = manifest.get("raw_file_path")
    derived_file_path = manifest.get("derived_file_path")
    fixture_file = manifest.get("fixture_fallback_path")

    for candidate in (raw_file, derived_file_path, fixture_file):
        if candidate:
            output_paths.append(candidate)
    if not output_paths and derived_file.exists():
        output_paths.append(repo_relative(derived_file))

    return {
        "dataset_name": manifest.get("dataset_name", default_entry["dataset_name"]),
        "preferred_source": manifest.get("source_name", default_entry["preferred_source"]),
        "source_url": manifest.get("source_url", default_entry["source_url"]),
        "access_method": manifest.get("access_method", "public_fetch_or_curated"),
        "expected_file_type": manifest.get("expected_file_type", default_entry["expected_file_type"]),
        "license_note": manifest.get("license_note", default_entry["license_note"]),
        "citation_note": manifest.get("citation_note", default_entry["citation_note"]),
        "status": manifest.get("status", default_entry["status"]),
        "last_attempted": manifest.get("access_date", manifest.get("last_attempted", default_entry["last_attempted"])),
        "output_paths": output_paths or default_entry["output_paths"],
        "limitations": manifest.get("limitations", default_entry["limitations"]),
    }


def build_source_registry(output_dir: str | None = None) -> dict[str, dict[str, Any]]:
    registry = {
        key: build_registry_entry(key, output_dir)
        for key in SOURCE_SPECS
    }
    write_manifest(registry_output_path(output_dir), {"registry": registry})
    return registry
