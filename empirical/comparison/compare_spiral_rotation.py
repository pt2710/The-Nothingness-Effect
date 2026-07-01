"""Run a spiral rotation comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import comparison_paths, morphology_figure_path, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import spiral_galaxy_mapping as mapping


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
            "dataset_name": "galaxy_rotation",
        }
        if dataset_path is not None
        else resolve_input_dataset("galaxy", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
    paths = comparison_paths("spiral_rotation", output_dir)
    morphology_path = morphology_figure_path("spiral", output_dir)

    rows = []
    for idx, radius in enumerate(empirical["radius"]):
        rows.append(
            {
                "radius": float(radius),
                "observed_velocity": float(empirical["velocity"][idx]),
                "velocity_uncertainty": float(empirical["velocity_uncertainty"][idx]),
                "tne_prediction": float(prediction["tne_prediction"][idx]),
                "baseline_prediction": float(prediction["baseline_prediction"][idx]),
                "tne_residual": float(residuals["tne_residual"][idx]),
                "baseline_residual": float(residuals["baseline_residual"][idx]),
                "galaxy_id": empirical["galaxy_id"][idx],
                "source_status": empirical["source_status"][idx],
            }
        )

    save_rows(paths["data"], rows)
    save_rows(
        paths["metrics"],
        [
            {
                **metrics,
                "model": "locality_driven_gravity",
                "empirical_dataset": selection["dataset_name"],
                "data_status": selection["status"],
            }
        ],
    )
    mapping.plot_comparison(empirical, prediction, {"curve": paths["figure"], "morphology": morphology_path})
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Spiral Rotation Report",
                "",
                f"- data status: {selection['status']}",
                f"- radius scale: {prediction['fitted_parameters']['radius_scale']:.6f}",
                f"- velocity scale: {prediction['fitted_parameters']['velocity_scale']:.6f}",
                f"- spiral order parameter: {prediction['spiral_order_parameter']:.6f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: preliminary comparison only; not a full astrophysical validation claim.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "spiral_rotation",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "fitted_parameters": prediction["fitted_parameters"],
            "output_paths": {
                "data": repo_relative(paths["data"]),
                "metrics": repo_relative(paths["metrics"]),
                "figure": repo_relative(paths["figure"]),
                "morphology_figure": repo_relative(morphology_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "source_manifest": selection["manifest"],
            "limitations": "Finite toy-model mapping only; not a full galaxy simulation.",
        },
    )
    return {
        "paths": {**paths, "morphology_figure": morphology_path},
        "metrics": metrics,
        "summary": {
            "model": "locality_driven_gravity",
            "empirical_dataset": "galaxy_rotation",
            "data_status": selection["status"],
            "comparison_type": "rotation-curve comparison",
            "fitted_parameters": prediction["fitted_parameters"],
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "linear_rotation_baseline",
            "TNE_vs_baseline_note": "Preliminary comparison only",
            "limitations": "Not a full astrophysical interpretation",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the spiral rotation comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    args = parser.parse_args(argv)
    run(
        output_dir=args.output_dir,
        use_fixtures=True,
        quick=args.quick,
        dataset_path=args.dataset_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
