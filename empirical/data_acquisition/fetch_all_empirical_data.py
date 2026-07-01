"""Run public empirical data acquisition with graceful fallback handling."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from empirical.data_acquisition import (
    fetch_eht_observables,
    fetch_galaxy_rotation_data,
    fetch_ligo_waveforms,
    fetch_redshift_clock_data,
)
from empirical.data_acquisition.source_registry import build_source_registry
from empirical.io import acquisition_summary_paths, repo_relative, save_rows, write_manifest


FetchRunner = Callable[..., dict[str, object]]

FETCH_RUNNERS: dict[str, FetchRunner] = {
    "redshift": fetch_redshift_clock_data.run,
    "galaxy": fetch_galaxy_rotation_data.run,
    "eht": fetch_eht_observables.run,
    "ligo": fetch_ligo_waveforms.run,
}


def _selected(dataset: str) -> list[str]:
    return list(FETCH_RUNNERS) if dataset == "all" else [dataset]


def run_fetch_all(
    *,
    dataset: str = "all",
    output_dir: str | Path | None = None,
    offline: bool = False,
    force: bool = False,
    quick: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    manifests: dict[str, Any] = {}
    for key in _selected(dataset):
        runner = FETCH_RUNNERS[key]
        try:
            payload = runner(output_dir=output_dir, offline=offline, force=force, quick=quick)
        except Exception as exc:
            if strict:
                raise
            payload = {
                "dataset_name": key,
                "status": "unavailable",
                "source_url": "",
                "raw_file_path": "",
                "derived_file_path": "",
                "limitations": f"Fetch failed without strict mode: {type(exc).__name__}: {exc}",
            }
        manifests[key] = payload
        rows.append(
            {
                "dataset_name": payload.get("dataset_name", key),
                "status": payload.get("status", "unavailable"),
                "source_url": payload.get("source_url", ""),
                "raw_file_path": payload.get("raw_file_path", ""),
                "derived_file_path": payload.get("derived_file_path", ""),
                "limitations": payload.get("limitations", ""),
            }
        )

    build_source_registry(str(output_dir) if output_dir is not None else None)
    summary_paths = acquisition_summary_paths(output_dir)
    save_rows(summary_paths["metrics"], rows)
    write_manifest(
        summary_paths["manifest"],
        {
            "dataset": dataset,
            "offline": offline,
            "force": force,
            "quick": quick,
            "strict": strict,
            "manifests": manifests,
            "summary_csv": repo_relative(summary_paths["metrics"]),
        },
    )
    return {
        "rows": rows,
        "manifests": manifests,
        "summary_paths": summary_paths,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch public empirical datasets with fixture-safe fallback handling.")
    parser.add_argument("--dataset", default="all", choices=["redshift", "galaxy", "eht", "ligo", "all"])
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    run_fetch_all(
        dataset=args.dataset,
        output_dir=args.output_dir,
        offline=args.offline,
        force=args.force,
        quick=args.quick,
        strict=args.strict,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
