"""Run a fixture-backed elastic-pi ringdown comparison."""

from __future__ import annotations

from pathlib import Path

from empirical.io import comparison_paths, repo_relative, residual_figure_path, save_rows, write_manifest, write_report
from empirical.mappings import ripple_ringdown_mapping as mapping


def run(output_dir: str | Path | None = None, use_fixtures: bool = True, quick: bool = False) -> dict[str, object]:
    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    paths = comparison_paths("elastic_pi_ringdown", output_dir)
    residual_path = residual_figure_path("elastic_pi_ringdown", output_dir)
    rows = []
    for idx, time_value in enumerate(empirical["time"]):
        rows.append(
            {
                "time": float(time_value),
                "observed_strain": float(empirical["strain"][idx]),
                "strain_uncertainty": float(empirical["strain_uncertainty"][idx]),
                "tne_prediction": float(prediction["tne_prediction"][idx]),
                "baseline_prediction": float(prediction["baseline_prediction"][idx]),
                "tne_residual": float(residuals["tne_residual"][idx]),
                "baseline_residual": float(residuals["baseline_residual"][idx]),
                "source_status": empirical["source_status"][idx],
            }
        )
    save_rows(paths["data"], rows)
    save_rows(paths["metrics"], [{**metrics, "model": "elastic_pi_ripples", "empirical_dataset": "ligo_ringdown_fixture", "fixture_status": "fixture_only"}])
    mapping.plot_comparison(empirical, prediction, {"curve": paths["figure"], "residual": residual_path})
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Elastic-pi Ringdown Report",
                "",
                "This is a fixture-backed ringdown comparison only.",
                f"- TNE time scale: {prediction['fitted_parameters']['tne']['time_scale']:.4f}",
                f"- baseline tau: {prediction['fitted_parameters']['baseline']['tau']:.4f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                f"- baseline RMSE: {metrics['baseline_RMSE']:.6f}",
                "",
                "Interpretation: preliminary residual comparison only; not a claim that TNE beats GR.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "elastic_pi_ringdown",
            "data_status": "fixture_only",
            "fitted_parameters": prediction["fitted_parameters"],
            "output_paths": {
                "data": repo_relative(paths["data"]),
                "metrics": repo_relative(paths["metrics"]),
                "figure": repo_relative(paths["figure"]),
                "residual_figure": repo_relative(residual_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "limitations": "Uses offline ringdown fixture only.",
        },
    )
    return {
        "paths": {**paths, "residual_figure": residual_path},
        "metrics": metrics,
        "summary": {
            "model": "elastic_pi_ripples",
            "empirical_dataset": "ligo_ringdown",
            "data_status": "fixture_only",
            "comparison_type": "ringdown residual comparison",
            "fitted_parameters": prediction["fitted_parameters"],
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "damped_sinusoid_baseline",
            "TNE_vs_baseline_note": metrics["TNE_vs_baseline_note"],
            "limitations": "Offline ringdown fixture only",
            "passed_validation": metrics["passed_validation"],
        },
    }
