"""Run a fixture-backed EHT horizon/shadow comparison."""

from __future__ import annotations

from pathlib import Path

from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import horizon_eht_mapping as mapping


def run(output_dir: str | Path | None = None, use_fixtures: bool = True, quick: bool = False) -> dict[str, object]:
    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
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
    save_rows(paths["metrics"], [{**metrics, "model": "black_hole_dynamics", "empirical_dataset": "eht_observable_fixture", "fixture_status": "fixture_only"}])
    mapping.plot_comparison(empirical, prediction, paths["figure"])
    write_report(
        paths["report"],
        "\n".join(
            [
                "# EHT Horizon Report",
                "",
                "This is a fixture-backed horizon/shadow comparison only.",
                f"- fitted angular scale alpha: {fitted['alpha']:.4f}",
                f"- ring contrast proxy: {prediction['ring_contrast_proxy']:.4f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: this is not GRMHD, not EHT reconstruction, and not observational validation.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "eht_horizon",
            "data_status": "fixture_only",
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "limitations": "Angular observables are fixture-backed only.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "eht_observables",
            "data_status": "fixture_only",
            "comparison_type": "horizon/shadow proxy comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "none",
            "TNE_vs_baseline_note": "Proxy scaling only",
            "limitations": "No EHT image reconstruction in this run",
            "passed_validation": metrics["passed_validation"],
        },
    }
