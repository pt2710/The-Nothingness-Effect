"""Fetch a lightweight public galaxy rotation dataset from SPARC."""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

from empirical.data_acquisition.fetch_utils import (
    cache_raw_path,
    download_to_cache,
    provenance_manifest,
    write_dataset_manifest,
)
from empirical.io import public_data_path, save_rows


SELECTED_GALAXIES = ["NGC2403", "NGC3198", "NGC6503"]
MAX_ROWS_PER_GALAXY = 24


def _parse_rotation_rows(raw_text: str, galaxy_id: str) -> list[dict[str, float | str]]:
    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    values = [line.split() for line in lines]
    radius = [float(parts[0]) for parts in values]
    velocity = [float(parts[1]) for parts in values]
    uncertainty = [float(parts[2]) for parts in values]
    r_scale = max(radius)
    v_scale = max(velocity)
    rows: list[dict[str, float | str]] = []
    for r_value, v_value, u_value in zip(radius, velocity, uncertainty, strict=True):
        rows.append(
            {
                "radius": r_value / r_scale,
                "velocity": v_value / v_scale,
                "velocity_uncertainty": u_value / v_scale,
                "radius_kpc": r_value,
                "velocity_kms": v_value,
                "velocity_uncertainty_kms": u_value,
                "galaxy_id": galaxy_id,
                "source_status": "fetched",
            }
        )
    return rows


def _downsample_rows(rows: list[dict[str, float | str]], max_rows: int = MAX_ROWS_PER_GALAXY) -> list[dict[str, float | str]]:
    if len(rows) <= max_rows:
        return rows
    step = (len(rows) - 1) / float(max_rows - 1)
    selected_indices = sorted({int(round(index * step)) for index in range(max_rows)})
    return [rows[index] for index in selected_indices]


def run(
    output_dir: str | Path | None = None,
    *,
    offline: bool = False,
    force: bool = False,
    quick: bool = False,
) -> dict[str, object]:
    derived_path = public_data_path("galaxy_rotation_public.csv", output_dir)
    manifest_name = "galaxy_rotation_manifest.json"
    zip_url = "https://astroweb.case.edu/SPARC/Rotmod_LTG.zip"

    if offline and derived_path.exists():
        payload = provenance_manifest(
            dataset_name="galaxy_rotation",
            source_name="SPARC rotation-curve catalog",
            source_url=zip_url,
            script_name=Path(__file__).name,
            status="cached",
            output_dir=str(output_dir) if output_dir is not None else None,
            derived_file_path=derived_path,
            access_method="cached_public_fetch",
            expected_file_type="csv",
            license_note="Derived compact CSV from SPARC public rotation curves.",
            citation_note="SPARC-derived lightweight galaxy curve.",
            preprocessing_steps=["Loaded previously generated compact rotation-curve CSV."],
            limitations="Offline mode does not refresh public SPARC inputs.",
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    if offline and not derived_path.exists():
        payload = provenance_manifest(
            dataset_name="galaxy_rotation",
            source_name="SPARC rotation-curve catalog",
            source_url=zip_url,
            script_name=Path(__file__).name,
            status="fixture_only",
            output_dir=str(output_dir) if output_dir is not None else None,
            access_method="offline_fixture_fallback",
            expected_file_type="csv",
            license_note="Fixture fallback remains available when offline.",
            citation_note="Public SPARC fetch skipped in offline mode.",
            preprocessing_steps=["Offline mode selected; no SPARC download attempted."],
            limitations="No cached derived SPARC CSV was available.",
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    raw_zip_path = cache_raw_path("galaxy_rotation", "Rotmod_LTG.zip", str(output_dir) if output_dir is not None else None)
    download_to_cache(zip_url, raw_zip_path, force=force)
    with zipfile.ZipFile(raw_zip_path, "r") as archive:
        archive_names = set(archive.namelist())
        filenames = [
            f"{galaxy_id}_rotmod.dat"
            for galaxy_id in SELECTED_GALAXIES
            if f"{galaxy_id}_rotmod.dat" in archive_names
        ]
        if not filenames:
            filenames = sorted(name for name in archive.namelist() if name.endswith("_rotmod.dat"))[:3]
        rows: list[dict[str, float | str]] = []
        for filename in filenames:
            raw_text = archive.read(filename).decode("utf-8", errors="replace")
            rows.extend(_downsample_rows(_parse_rotation_rows(raw_text, filename.replace("_rotmod.dat", ""))))
    save_rows(derived_path, rows)
    payload = provenance_manifest(
        dataset_name="galaxy_rotation",
        source_name="SPARC rotation-curve catalog",
        source_url=zip_url,
        script_name=Path(__file__).name,
        status="fetched",
        output_dir=str(output_dir) if output_dir is not None else None,
        raw_file_path=raw_zip_path,
        derived_file_path=derived_path,
        access_method="public_zip_download",
        expected_file_type="csv",
        license_note="Derived compact CSV from SPARC public rotation curves.",
        citation_note="Compact multi-galaxy SPARC rotation curves derived from the public archive.",
        preprocessing_steps=[
            "Downloaded the public Rotmod_LTG.zip archive.",
            f"Parsed {len(filenames)} deterministic representative galaxy files.",
            "Normalized radius and velocity columns per galaxy for the repository comparison adapter while retaining raw columns.",
            f"Downsampled each galaxy to at most {MAX_ROWS_PER_GALAXY} rows to keep the repository artifact lightweight and reproducible.",
        ],
        limitations="A small deterministic representative subset of SPARC rotation curves is stored in this run.",
        extra={"selected_galaxies": [filename.replace("_rotmod.dat", "") for filename in filenames]},
    )
    write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a lightweight galaxy rotation dataset from SPARC.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, offline=args.offline, force=args.force, quick=args.quick)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
