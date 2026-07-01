"""Fetch or derive a lightweight redshift/clock benchmark dataset."""

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


RED_SHIFT_BENCHMARKS = [
    {
        "case_id": "pound_rebka_1960",
        "reference_label": "Pound-Rebka 22.5 m tower benchmark",
        "baseline_shift_raw": -2.46e-15,
        "observed_shift_raw": -2.56e-15,
        "observed_uncertainty_raw": 0.25e-15,
        "observable_reference": 22.5,
        "citation_note": "Uses the published Pound-Rebka redshift benchmark reported at the 10% level.",
    },
    {
        "case_id": "gravity_probe_a_1976",
        "reference_label": "Gravity Probe A 10,000 km benchmark",
        "baseline_shift_raw": -4.50e-10,
        "observed_shift_raw": -4.500315e-10,
        "observed_uncertainty_raw": 3.15e-14,
        "observable_reference": 10000.0,
        "citation_note": "Uses the published Gravity Probe A benchmark with approximately 70 ppm agreement.",
    },
]


def _derived_rows() -> list[dict[str, float | str]]:
    scale = max(abs(item["observed_shift_raw"]) for item in RED_SHIFT_BENCHMARKS)
    observable_scale = max(item["observable_reference"] for item in RED_SHIFT_BENCHMARKS)
    rows: list[dict[str, float | str]] = []
    for item in RED_SHIFT_BENCHMARKS:
        rows.append(
            {
                "case_id": item["case_id"],
                "observable_x": item["observable_reference"] / observable_scale,
                "observed_shift": item["observed_shift_raw"] / scale,
                "observed_uncertainty": item["observed_uncertainty_raw"] / scale,
                "baseline_shift": item["baseline_shift_raw"] / scale,
                "raw_observed_shift": item["observed_shift_raw"],
                "raw_baseline_shift": item["baseline_shift_raw"],
                "reference_label": item["reference_label"],
                "source_status": "cached",
            }
        )
    return rows


def run(
    output_dir: str | Path | None = None,
    *,
    offline: bool = False,
    force: bool = False,
    quick: bool = False,
) -> dict[str, object]:
    derived_path = public_data_path("redshift_clock_public_or_curated.csv", output_dir)
    manifest_name = "redshift_clock_manifest.json"
    source_urls = [
        "https://physics.aps.org/story/v16/st1",
        "https://ntrs.nasa.gov/api/citations/19800011717/downloads/19800011717.pdf",
    ]

    if offline and derived_path.exists():
        payload = provenance_manifest(
            dataset_name="redshift_clock",
            source_name="Published redshift benchmark literature",
            source_url=source_urls[0],
            script_name=Path(__file__).name,
            status="cached",
            output_dir=str(output_dir) if output_dir is not None else None,
            derived_file_path=derived_path,
            access_method="curated_published_summary",
            expected_file_type="csv",
            license_note="Compact derived benchmark table for repository-linked comparison use.",
            citation_note="Published benchmark values remain the provenance source.",
            preprocessing_steps=["Loaded previously generated compact benchmark CSV."],
            limitations="Offline mode does not attempt live network retrieval.",
            extra={"source_urls": source_urls},
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    if offline and not derived_path.exists():
        payload = provenance_manifest(
            dataset_name="redshift_clock",
            source_name="Published redshift benchmark literature",
            source_url=source_urls[0],
            script_name=Path(__file__).name,
            status="fixture_only",
            output_dir=str(output_dir) if output_dir is not None else None,
            access_method="offline_fixture_fallback",
            expected_file_type="csv",
            license_note="Fixture fallback remains available when offline.",
            citation_note="Curated benchmark generation skipped in offline mode.",
            preprocessing_steps=["Offline mode selected; no public source retrieval attempted."],
            limitations="No cached public benchmark file was available.",
            extra={"source_urls": source_urls},
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    raw_files: list[str] = []
    for index, url in enumerate(source_urls, start=1):
        try:
            text = http_get_text(url, timeout=30)
            raw_path = write_cached_text(
                "redshift_clock",
                f"source_{index}.html" if not url.endswith(".pdf") else f"source_{index}.pdf.txt",
                text[:250000],
                str(output_dir) if output_dir is not None else None,
            )
            raw_files.append(repo_relative(raw_path))
        except Exception:
            continue

    rows = _derived_rows()
    save_rows(derived_path, rows)
    payload = provenance_manifest(
        dataset_name="redshift_clock",
        source_name="Published redshift benchmark literature",
        source_url=source_urls[0],
        script_name=Path(__file__).name,
        status="cached",
        output_dir=str(output_dir) if output_dir is not None else None,
        derived_file_path=derived_path,
        access_method="curated_published_summary",
        expected_file_type="csv",
        license_note="Compact derived benchmark table for repository-linked comparison use.",
        citation_note="Includes Pound-Rebka and Gravity Probe A published benchmark values.",
        preprocessing_steps=[
            "Collected lightweight public provenance pages where accessible.",
            "Constructed a compact derived benchmark table from published benchmark values.",
            "Normalized observable_x and shift columns for the repository comparison adapter.",
        ],
        limitations="Structured raw public benchmark tables are not guaranteed for these experiments.",
        extra={
            "raw_supporting_files": raw_files,
            "source_urls": source_urls,
        },
    )
    write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch or derive a lightweight redshift benchmark dataset.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, offline=args.offline, force=args.force, quick=args.quick)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
