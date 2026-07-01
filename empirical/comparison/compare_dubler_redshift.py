"""Run a fixture-backed Dubler redshift comparison."""

from __future__ import annotations

from pathlib import Path

from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import dubler_redshift_mapping as mapping


def run(output_dir: str | Path | None = None, use_fixtures: bool = True, quick: bool = False) -> dict[str, object]:
    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    paths = comparison_paths("dubler_redshift", output_dir)
    rows = []
    for idx, case_id in enumerate(empirical["case_id"]):
        rows.append(
            {
                "case_id": case_id,
                "observable_x": float(empirical["observable_x"][idx]),
                "observed_shift": float(empirical["observed_shift"][idx]),
                "observed_uncertainty": float(empirical["observed_uncertainty"][idx]),
                "baseline_shift": float(prediction["baseline_prediction"][idx]),
                "tne_prediction": float(prediction["tne_prediction"][idx]),
                "tne_residual": float(residuals["tne_residual"][idx]),
                "baseline_residual": float(residuals["baseline_residual"][idx]),
                "source_status": empirical["source_status"][idx],
            }
        )
    save_rows(paths["data"], rows)
    save_rows(paths["metrics"], [{**metrics, "model": "elastic_dubler_effect", "empirical_dataset": "redshift_clock_fixture", "fixture_status": "fixture_only"}])
    mapping.plot_comparison(empirical, prediction, paths["figure"])
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Dubler Redshift Report",
                "",
                "This is a fixture-backed comparison only.",
                f"- fitted beta: {fitted['beta']:.4f}",
                f"- fitted K_D: {fitted['K_D']:.4f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                f"- baseline RMSE: {metrics['baseline_RMSE']:.6f}",
                "",
                "Interpretation: this run provides an offline observable-mapping adapter, not empirical validation.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "dubler_redshift",
            "data_status": "fixture_only",
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "limitations": "Synthetic/curated fixture only; not an empirical validation claim.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "elastic_dubler_effect",
            "empirical_dataset": "redshift_clock",
            "data_status": "fixture_only",
            "comparison_type": "fixture-backed redshift shift comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "fixture_baseline_shift",
            "TNE_vs_baseline_note": metrics["TNE_vs_baseline_note"],
            "limitations": "Offline fixture only",
            "passed_validation": metrics["passed_validation"],
        },
    }
