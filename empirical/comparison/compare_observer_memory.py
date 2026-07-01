"""Run a fixture-backed observer-memory comparison."""

from __future__ import annotations

from pathlib import Path

from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import observer_memory_mapping as mapping


def run(output_dir: str | Path | None = None, use_fixtures: bool = True, quick: bool = False) -> dict[str, object]:
    empirical = mapping.prepare_empirical_observable()
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    paths = comparison_paths("observer_memory", output_dir)
    rows = []
    for idx, time_value in enumerate(empirical["time"]):
        rows.append(
            {
                "time": float(time_value),
                "observed_strain": float(empirical["strain"][idx]),
                "strain_uncertainty": float(empirical["strain_uncertainty"][idx]),
                "tne_prediction": float(prediction["tne_prediction"][idx]),
                "tne_residual": float(residuals["tne_residual"][idx]),
                "memory_derivative_proxy": float(prediction["memory_derivative_proxy"][idx]),
                "cumulative_memory_proxy": float(prediction["cumulative_memory_proxy"][idx]),
                "source_status": empirical["source_status"][idx],
            }
        )
    save_rows(paths["data"], rows)
    save_rows(paths["metrics"], [{**metrics, "model": "black_hole_dynamics", "empirical_dataset": "observer_memory_fixture", "fixture_status": "fixture_only"}])
    mapping.plot_comparison(empirical, prediction, paths["figure"])
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Observer Memory Report",
                "",
                "This is a fixture-backed comparison only.",
                f"- amplitude scale: {fitted['amplitude_scale']:.4f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: memory-like proxy alignment remains preliminary and is not an empirical validation claim.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "observer_memory",
            "data_status": "fixture_only",
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "limitations": "Uses a ringdown-style fixture as a memory-like proxy.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "ligo_ringdown_memory_proxy",
            "data_status": "fixture_only",
            "comparison_type": "memory-trace comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "none",
            "TNE_vs_baseline_note": "Fixture-backed only",
            "limitations": "Memory proxy uses offline ringdown-style fixture",
            "passed_validation": metrics["passed_validation"],
        },
    }
