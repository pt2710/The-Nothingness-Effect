"""Fetch or derive lightweight public EHT summary observables."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.data_acquisition.fetch_utils import (
    http_get_text,
    provenance_manifest,
    write_cached_text,
    write_dataset_manifest,
)
from empirical.io import public_data_path, repo_relative, save_rows


EHT_ROWS = [
    {
        "source": "M87*",
        "ring_diameter": 42.0,
        "ring_diameter_uncertainty": 3.0,
        "shadow_radius": 21.0,
        "shadow_radius_uncertainty": 1.5,
        "mass_billion_solar": 6.5,
        "distance_mpc": 16.8,
        "angular_scale_note": "published summary mass-distance proxy",
        "published_reference": "arXiv:1906.11241",
        "source_status": "cached",
    },
    {
        "source": "SgrA*",
        "ring_diameter": 51.8,
        "ring_diameter_uncertainty": 2.3,
        "shadow_radius": 25.9,
        "shadow_radius_uncertainty": 1.2,
        "mass_billion_solar": 0.0040,
        "distance_mpc": 0.0082,
        "angular_scale_note": "published summary mass-distance proxy",
        "published_reference": "arXiv:2311.09484",
        "source_status": "cached",
    },
]


def run(
    output_dir: str | Path | None = None,
    *,
    offline: bool = False,
    force: bool = False,
    quick: bool = False,
) -> dict[str, object]:
    derived_path = public_data_path("eht_public_observables.csv", output_dir)
    manifest_name = "eht_observables_manifest.json"
    source_urls = [
        "https://arxiv.org/abs/1906.11241",
        "https://arxiv.org/abs/2311.09484",
    ]

    if offline and derived_path.exists():
        payload = provenance_manifest(
            dataset_name="eht_observables",
            source_name="Published Event Horizon Telescope summary observables",
            source_url=source_urls[0],
            script_name=Path(__file__).name,
            status="cached",
            output_dir=str(output_dir) if output_dir is not None else None,
            derived_file_path=derived_path,
            access_method="cached_published_summary",
            expected_file_type="csv",
            license_note="Compact derived observables only.",
            citation_note="Previously generated EHT summary observables CSV.",
            preprocessing_steps=["Loaded previously generated compact EHT observable CSV."],
            limitations="Offline mode does not refresh public source pages.",
            extra={"source_urls": source_urls},
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    if offline and not derived_path.exists():
        payload = provenance_manifest(
            dataset_name="eht_observables",
            source_name="Published Event Horizon Telescope summary observables",
            source_url=source_urls[0],
            script_name=Path(__file__).name,
            status="fixture_only",
            output_dir=str(output_dir) if output_dir is not None else None,
            access_method="offline_fixture_fallback",
            expected_file_type="csv",
            license_note="Fixture fallback remains available when offline.",
            citation_note="Public EHT fetch skipped in offline mode.",
            preprocessing_steps=["Offline mode selected; no live source page retrieval attempted."],
            limitations="No cached EHT summary CSV was available.",
            extra={"source_urls": source_urls},
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    raw_files: list[str] = []
    for index, url in enumerate(source_urls, start=1):
        try:
            text = http_get_text(url, timeout=30)
            raw_path = write_cached_text("eht_observables", f"source_{index}.html", text[:250000], str(output_dir) if output_dir is not None else None)
            raw_files.append(repo_relative(raw_path))
        except Exception:
            continue

    save_rows(derived_path, EHT_ROWS)
    payload = provenance_manifest(
        dataset_name="eht_observables",
        source_name="Published Event Horizon Telescope summary observables",
        source_url=source_urls[0],
        script_name=Path(__file__).name,
        status="cached",
        output_dir=str(output_dir) if output_dir is not None else None,
        derived_file_path=derived_path,
        access_method="curated_published_summary",
        expected_file_type="csv",
        license_note="Compact derived observables only.",
        citation_note="Derived from published M87* and Sgr A* summary observables.",
        preprocessing_steps=[
            "Retrieved lightweight public abstract pages where accessible.",
            "Stored a compact derived table of published ring and shadow observables.",
            "Added source mass and distance summary metadata for a finite angular-size proxy.",
        ],
        limitations="Published summary observables only; no raw imaging products are stored.",
        extra={"raw_supporting_files": raw_files, "source_urls": source_urls},
    )
    write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch or derive lightweight public EHT summary observables.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, offline=args.offline, force=args.force, quick=args.quick)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
