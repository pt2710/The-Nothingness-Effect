"""Run a fixture-backed spiral rotation comparison."""

from __future__ import annotations

from pathlib import Path

from empirical.io import comparison_paths, morphology_figure_path, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import spiral_galaxy_mapping as mapping


def run(output_dir: str | Path | None = None, use_fixtures: bool = True, quick: bool = False) -> dict[str, object]:
    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
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
    save_rows(paths["metrics"], [{**metrics, "model": "locality_driven_gravity", "empirical_dataset": "galaxy_rotation_fixture", "fixture_status": "fixture_only"}])
    mapping.plot_comparison(empirical, prediction, {"curve": paths["figure"], "morphology": morphology_path})
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Spiral Rotation Report",
                "",
                "This is a fixture-backed rotation-curve comparison.",
                f"- radius scale: {prediction['fitted_parameters']['radius_scale']:.4f}",
                f"- velocity scale: {prediction['fitted_parameters']['velocity_scale']:.4f}",
                f"- spiral order parameter: {prediction['spiral_order_parameter']:.4f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: locality-driven spiral formation remains a toy model, not a full astrophysical simulation.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "spiral_rotation",
            "data_status": "fixture_only",
            "fitted_parameters": prediction["fitted_parameters"],
            "output_paths": {
                "data": repo_relative(paths["data"]),
                "metrics": repo_relative(paths["metrics"]),
                "figure": repo_relative(paths["figure"]),
                "morphology_figure": repo_relative(morphology_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "limitations": "Fixture rotation curve only; no direct morphology observable in this run.",
        },
    )
    return {
        "paths": {**paths, "morphology_figure": morphology_path},
        "metrics": metrics,
        "summary": {
            "model": "locality_driven_gravity",
            "empirical_dataset": "galaxy_rotation",
            "data_status": "fixture_only",
            "comparison_type": "rotation-curve comparison",
            "fitted_parameters": prediction["fitted_parameters"],
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "linear_rotation_baseline",
            "TNE_vs_baseline_note": "Fixture-backed only",
            "limitations": "No full astrophysical interpretation",
            "passed_validation": metrics["passed_validation"],
        },
    }
