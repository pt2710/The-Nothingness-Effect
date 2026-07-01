"""Attempt public Hawking-analogue or PBH-limit acquisition without fabricating data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.data_acquisition.fetch_utils import provenance_manifest, write_dataset_manifest


def run(
    output_dir: str | Path | None = None,
    *,
    offline: bool = False,
    force: bool = False,
    quick: bool = False,
) -> dict[str, object]:
    payload = provenance_manifest(
        dataset_name="hawking_analogue_or_limits",
        source_name="Analogue Hawking or PBH limit literature",
        source_url="https://fermi.gsfc.nasa.gov/ssc/data/",
        script_name=Path(__file__).name,
        status="fixture_only" if offline else "manual_required",
        output_dir=str(output_dir) if output_dir is not None else None,
        access_method="manual_curation_required",
        expected_file_type="csv",
        license_note="No public compact dataset is bundled in this run.",
        citation_note="Use an analogue-Hawking or PBH-limit publication-specific dataset in a later manual pass.",
        preprocessing_steps=[
            "Recorded the public source family.",
            "Did not fabricate or infer a lightweight dataset when a reliable compact public table was not guaranteed.",
        ],
        limitations="Reliable lightweight public tables were not automatically acquired in this run.",
        extra={
            "source_urls": [
                "https://fermi.gsfc.nasa.gov/ssc/data/",
                "https://arxiv.org/",
            ]
        },
    )
    write_dataset_manifest("hawking_analogue_or_limits_manifest.json", payload, str(output_dir) if output_dir is not None else None)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Attempt public Hawking analogue or PBH-limit acquisition.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, offline=args.offline, force=args.force, quick=args.quick)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
