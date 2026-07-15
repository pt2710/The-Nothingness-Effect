"""Deprecated compatibility shim for the Hawking empirical-fetch slot.

No direct astrophysical empirical Hawking-radiation dataset is fetched here.
Use the Hawking theoretical benchmark runner instead.
"""

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
        source_name="Hawking theoretical benchmark",
        source_url="the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/hawking",
        script_name=Path(__file__).name,
        status="theoretical_benchmark",
        output_dir=str(output_dir) if output_dir is not None else None,
        access_method="deprecated_empirical_fetch_slot",
        expected_file_type="csv",
        license_note="No empirical Hawking-radiation dataset is bundled because this slot is now theoretical-benchmark only.",
        citation_note="No direct astrophysical empirical Hawking-radiation dataset is fetched. Use the Hawking theoretical benchmark instead.",
        preprocessing_steps=[
            "Deprecated the empirical Hawking fetch slot.",
            "Redirected users to the repository-local Hawking theoretical benchmark artifacts.",
        ],
        limitations="Hawking-radiation is handled as a theoretical benchmark, not a direct empirical fetched-data target.",
        extra={
            "theoretical_benchmark_runner": "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.hawking.simulation.theoretical_benchmarks.compare_tne_hawking_like_flux",
        },
    )
    write_dataset_manifest("hawking_analogue_or_limits_manifest.json", payload, str(output_dir) if output_dir is not None else None)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deprecated Hawking empirical-fetch shim. Use the theoretical benchmark runner instead.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, offline=args.offline, force=args.force, quick=args.quick)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
