"""Build a deterministic source registry for offline fixture-backed comparisons."""

from __future__ import annotations

from typing import Any

from empirical.io import fixture_path, registry_output_path, repo_relative, write_manifest


def build_source_registry(output_dir: str | None = None) -> dict[str, dict[str, Any]]:
    registry = {
        "redshift_clock": {
            "dataset_name": "redshift_clock",
            "preferred_source": "Published redshift/gravitational-clock literature",
            "source_url": "https://lambda.gsfc.nasa.gov/",
            "access_method": "offline_fixture",
            "expected_file_type": "csv",
            "license_note": "Fixture-only synthetic/curated test data in this run.",
            "citation_note": "Replace with real literature citation in a network-enabled run.",
            "status": "fixture_only",
            "last_attempted": "offline_fixture_run4",
            "output_paths": [repo_relative(fixture_path("redshift_clock_fixture.csv"))],
        },
        "galaxy_rotation": {
            "dataset_name": "galaxy_rotation",
            "preferred_source": "SPARC-style rotation-curve catalog",
            "source_url": "http://astroweb.cwru.edu/SPARC/",
            "access_method": "offline_fixture",
            "expected_file_type": "csv",
            "license_note": "Fixture-only synthetic/curated test data in this run.",
            "citation_note": "Replace with SPARC or equivalent citation in a network-enabled run.",
            "status": "fixture_only",
            "last_attempted": "offline_fixture_run4",
            "output_paths": [repo_relative(fixture_path("galaxy_rotation_fixture.csv"))],
        },
        "eht_observables": {
            "dataset_name": "eht_observables",
            "preferred_source": "Event Horizon Telescope published observables",
            "source_url": "https://eventhorizontelescope.org/",
            "access_method": "offline_fixture",
            "expected_file_type": "csv",
            "license_note": "Fixture-only synthetic/curated test data in this run.",
            "citation_note": "Replace with published EHT summary observables in a network-enabled run.",
            "status": "fixture_only",
            "last_attempted": "offline_fixture_run4",
            "output_paths": [repo_relative(fixture_path("eht_observable_fixture.csv"))],
        },
        "hawking_analogue_or_limits": {
            "dataset_name": "hawking_analogue_or_limits",
            "preferred_source": "Published analogue Hawking or upper-limit literature",
            "source_url": "https://arxiv.org/",
            "access_method": "offline_fixture",
            "expected_file_type": "csv",
            "license_note": "Fixture-only synthetic/curated test data in this run.",
            "citation_note": "Replace with analogue/limit reference in a later run.",
            "status": "fixture_only",
            "last_attempted": "offline_fixture_run4",
            "output_paths": [repo_relative(fixture_path("hawking_flux_fixture.csv"))],
        },
        "ligo_waveforms": {
            "dataset_name": "ligo_waveforms",
            "preferred_source": "GWOSC waveform archive",
            "source_url": "https://www.gwosc.org/",
            "access_method": "offline_fixture",
            "expected_file_type": "csv",
            "license_note": "Fixture-only synthetic/curated test data in this run.",
            "citation_note": "Replace with GWOSC waveform citation in a network-enabled run.",
            "status": "fixture_only",
            "last_attempted": "offline_fixture_run4",
            "output_paths": [repo_relative(fixture_path("ligo_ringdown_fixture.csv"))],
        },
        "ligo_ringdown": {
            "dataset_name": "ligo_ringdown",
            "preferred_source": "GWOSC ringdown-ready event extract",
            "source_url": "https://www.gwosc.org/",
            "access_method": "offline_fixture",
            "expected_file_type": "csv",
            "license_note": "Fixture-only synthetic/curated test data in this run.",
            "citation_note": "Replace with event-specific ringdown extract in a later run.",
            "status": "fixture_only",
            "last_attempted": "offline_fixture_run4",
            "output_paths": [repo_relative(fixture_path("ligo_ringdown_fixture.csv"))],
        },
    }
    write_manifest(registry_output_path(output_dir), {"registry": registry})
    return registry
