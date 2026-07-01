"""Run a fixture-backed Hawking-like flux comparison."""

from __future__ import annotations

from pathlib import Path

from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import hawking_flux_mapping as mapping


def run(output_dir: str | Path | None = None, use_fixtures: bool = True, quick: bool = False) -> dict[str, object]:
    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    paths = comparison_paths("hawking_like_flux", output_dir)
    rows = []
    for idx, x_value in enumerate(empirical["x"]):
        rows.append(
            {
                "x": float(x_value),
                "observed_flux": float(empirical["flux"][idx]),
                "flux_uncertainty": float(empirical["flux_uncertainty"][idx]),
                "tne_prediction": float(prediction["tne_prediction"][idx]),
                "baseline_prediction": float(prediction["baseline_prediction"][idx]),
                "tne_residual": float(residuals["tne_residual"][idx]),
                "baseline_residual": float(residuals["baseline_residual"][idx]),
                "source_status": empirical["source_status"][idx],
            }
        )
    save_rows(paths["data"], rows)
    save_rows(paths["metrics"], [{**metrics, "model": "black_hole_dynamics", "empirical_dataset": "hawking_flux_fixture", "fixture_status": "fixture_only"}])
    mapping.plot_comparison(empirical, prediction, paths["figure"])
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Hawking-like Flux Report",
                "",
                "This is a fixture-backed proxy/limit-style comparison only.",
                f"- amplitude scale: {fitted['amplitude_scale']:.4f}",
                f"- exponential baseline decay: {fitted['baseline_decay']:.4f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: no observed astrophysical Hawking radiation claim is made here.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "hawking_like_flux",
            "data_status": "fixture_only",
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "limitations": "Synthetic proxy fixture only.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "hawking_analogue_or_limits",
            "data_status": "fixture_only",
            "comparison_type": "flux proxy comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "exponential_decay_baseline",
            "TNE_vs_baseline_note": "Fixture-backed only",
            "limitations": "No astrophysical Hawking detection data in this run",
            "passed_validation": metrics["passed_validation"],
        },
    }
