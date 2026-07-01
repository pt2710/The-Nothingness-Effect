"""Aggregate empirical-comparison runner with public-data fetch and fixture fallback support."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from empirical.comparison import (
    compare_dubler_redshift,
    compare_elastic_pi_ringdown,
    compare_entropic_horizon_eht,
    compare_hawking_like_flux,
    compare_observer_memory,
    compare_spiral_rotation,
)
from empirical.data_acquisition.fetch_all_empirical_data import run_fetch_all
from empirical.data_acquisition.source_registry import build_source_registry
from empirical.io import repo_relative, save_rows, summary_paths, write_manifest, write_report


ComparisonRunner = Callable[[str | Path | None, bool, bool], dict[str, object]]

COMPARISON_RUNNERS: dict[str, tuple[str, ComparisonRunner]] = {
    "redshift": ("dubler_redshift", compare_dubler_redshift.run),
    "galaxy": ("spiral_rotation", compare_spiral_rotation.run),
    "eht": ("eht_horizon", compare_entropic_horizon_eht.run),
    "hawking": ("hawking_like_flux", compare_hawking_like_flux.run),
    "memory": ("observer_memory", compare_observer_memory.run),
    "ringdown": ("elastic_pi_ringdown", compare_elastic_pi_ringdown.run),
}


def _selected_datasets(dataset: str) -> list[str]:
    return list(COMPARISON_RUNNERS) if dataset == "all" else [dataset]


def _fetch_dataset_arg(dataset: str) -> str:
    mapping = {
        "memory": "ligo",
        "ringdown": "ligo",
    }
    if dataset == "all":
        return "all"
    return mapping.get(dataset, dataset)


def run_empirical_comparisons(
    *,
    output_dir: str | Path | None = None,
    dataset: str = "all",
    fetch: bool = False,
    offline: bool = False,
    use_fixtures: bool = True,
    quick: bool = False,
) -> dict[str, Any]:
    if fetch:
        run_fetch_all(
            dataset=_fetch_dataset_arg(dataset),
            output_dir=output_dir,
            offline=offline,
            force=False,
            quick=quick,
            strict=False,
        )

    registry = build_source_registry(str(output_dir) if output_dir is not None else None)
    summaries: list[dict[str, Any]] = []
    outputs: dict[str, Any] = {}

    for dataset_key in _selected_datasets(dataset):
        slug, runner = COMPARISON_RUNNERS[dataset_key]
        result = runner(output_dir=output_dir, use_fixtures=use_fixtures, quick=quick)
        summaries.append(dict(result["summary"]))
        outputs[slug] = {
            "paths": {name: repo_relative(path) for name, path in dict(result["paths"]).items()},
            "metrics": dict(result["metrics"]),
        }

    paths = summary_paths(output_dir)
    save_rows(paths["metrics"], summaries)
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Empirical Comparison Summary",
                "",
                "These empirical comparison scripts are preliminary reproducible comparison tools. They do not establish empirical validation of TNE. They map dimensionless TNE proxy outputs to observable quantities through explicit fitted or calibrated adapters and compare residuals against available empirical or published reference data.",
                "",
                "Run mode:",
                f"- fetch attempted: {fetch}",
                f"- offline: {offline}",
                f"- fixture fallback enabled: {use_fixtures}",
                f"- selected_datasets: {', '.join(_selected_datasets(dataset))}",
                "",
                "Claim boundary:",
                "- preliminary comparison only",
                "- not an empirical validation claim",
                "- not a formal proof substitute",
                "",
                "Summary rows:",
                *[
                    (
                        f"- {row['empirical_dataset']}: "
                        f"RMSE={row['RMSE']:.6f}, "
                        f"MAE={row['MAE']:.6f}, "
                        f"status={row['data_status']}, "
                        f"passed_validation={row['passed_validation']}"
                    )
                    for row in summaries
                ],
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "run_mode": {
                "fetch": fetch,
                "offline": offline,
                "use_fixtures": use_fixtures,
                "quick": quick,
                "dataset": dataset,
            },
            "registry_status": {key: value["status"] for key, value in registry.items()},
            "summary_outputs": {
                "metrics": repo_relative(paths["metrics"]),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "comparison_outputs": outputs,
            "limitations": (
                "Comparisons remain preliminary repository-linked support artifacts. "
                "Residual comparisons do not establish empirical validation."
            ),
        },
    )
    print(
        f"Generated empirical comparison artifacts for {len(summaries)} dataset(s) "
        f"at {repo_relative(Path(output_dir) if output_dir is not None else Path('empirical/outputs'))}."
    )
    return {
        "registry": registry,
        "summaries": summaries,
        "outputs": outputs,
        "summary_paths": paths,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run empirical comparisons with optional public-data fetches and fixture fallback. "
            "This is not an empirical validation claim."
        )
    )
    parser.add_argument("--fetch", action="store_true", help="Attempt public data acquisition before running comparisons.")
    parser.add_argument("--quick", action="store_true", help="Use the lightweight comparison execution path.")
    parser.add_argument("--offline", action="store_true", help="Do not attempt network access; use cached or fixture data.")
    parser.add_argument("--use-fixtures", action="store_true", help="Allow deterministic fixture fallback when public data are unavailable.")
    parser.add_argument("--output-dir", default=None, help="Override the empirical outputs directory.")
    parser.add_argument(
        "--dataset",
        default="all",
        choices=["redshift", "galaxy", "eht", "hawking", "memory", "ringdown", "all"],
        help="Select which comparison to run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_empirical_comparisons(
        output_dir=args.output_dir,
        dataset=args.dataset,
        fetch=args.fetch,
        offline=args.offline,
        use_fixtures=True,
        quick=args.quick,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
