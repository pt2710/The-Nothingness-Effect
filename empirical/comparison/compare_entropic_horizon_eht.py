"""Run an EHT horizon/shadow comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import horizon_eht_mapping as mapping


def run(
    output_dir: str | Path | None = None,
    use_fixtures: bool = True,
    quick: bool = False,
    dataset_path: str | Path | None = None,
) -> dict[str, object]:
    selection = (
        {
            "path": Path(dataset_path),
            "status": "cached",
            "manifest": {},
            "dataset_name": "eht_observables",
        }
        if dataset_path is not None
        else resolve_input_dataset("eht", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
    paths = comparison_paths("eht_horizon", output_dir)

    rows = []
    for idx, source in enumerate(empirical["source"]):
        rows.append(
            {
                "source": source,
                "ring_diameter_observed": float(empirical["ring_diameter"][idx]),
                "ring_diameter_predicted": float(prediction["ring_prediction"][idx]),
                "shadow_radius_observed": float(empirical["shadow_radius"][idx]),
                "shadow_radius_predicted": float(prediction["shadow_prediction"][idx]),
                "ring_residual": float(residuals["ring_residual"][idx]),
                "shadow_residual": float(residuals["shadow_residual"][idx]),
                "source_status": empirical["source_status"][idx],
            }
        )

    save_rows(paths["data"], rows)
    save_rows(
        paths["metrics"],
        [
            {
                **metrics,
                "model": "black_hole_dynamics",
                "empirical_dataset": selection["dataset_name"],
                "data_status": selection["status"],
            }
        ],
    )
    mapping.plot_comparison(empirical, prediction, paths["figure"])
    write_report(
        paths["report"],
        "\n".join(
            [
                "# EHT Horizon Report",
                "",
                f"- data status: {selection['status']}",
                f"- fitted angular scale alpha: {fitted['alpha']:.6f}",
                f"- ring contrast proxy: {prediction['ring_contrast_proxy']:.6f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: published summary observables only; not GRMHD reconstruction and not an empirical validation claim.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "eht_horizon",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "source_manifest": selection["manifest"],
            "limitations": "Published summary observables only; not raw EHT imaging products.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "eht_observables",
            "data_status": selection["status"],
            "comparison_type": "horizon/shadow proxy comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "none",
            "TNE_vs_baseline_note": "Preliminary proxy scaling only",
            "limitations": "No EHT image reconstruction in this run",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the EHT horizon/shadow comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, use_fixtures=True, quick=args.quick, dataset_path=args.dataset_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
