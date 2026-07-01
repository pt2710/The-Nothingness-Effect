"""Run an elastic-pi ringdown comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import comparison_paths, repo_relative, residual_figure_path, save_rows, write_manifest, write_report
from empirical.mappings import ripple_ringdown_mapping as mapping


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
            "dataset_name": "ligo_waveforms",
        }
        if dataset_path is not None
        else resolve_input_dataset("ringdown", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
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
    save_rows(
        paths["metrics"],
        [
            {
                **metrics,
                "model": "elastic_pi_ripples",
                "empirical_dataset": selection["dataset_name"],
                "data_status": selection["status"],
            }
        ],
    )
    mapping.plot_comparison(empirical, prediction, {"curve": paths["figure"], "residual": residual_path})
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Elastic-pi Ringdown Report",
                "",
                f"- data status: {selection['status']}",
                f"- TNE time scale: {prediction['fitted_parameters']['tne']['time_scale']:.6f}",
                f"- baseline tau: {prediction['fitted_parameters']['baseline']['tau']:.6f}",
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
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "fitted_parameters": prediction["fitted_parameters"],
            "output_paths": {
                "data": repo_relative(paths["data"]),
                "metrics": repo_relative(paths["metrics"]),
                "figure": repo_relative(paths["figure"]),
                "residual_figure": repo_relative(residual_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "source_manifest": selection["manifest"],
            "limitations": "Preliminary ringdown comparison only; not a formal proof substitute.",
        },
    )
    return {
        "paths": {**paths, "residual_figure": residual_path},
        "metrics": metrics,
        "summary": {
            "model": "elastic_pi_ripples",
            "empirical_dataset": "ligo_ringdown",
            "data_status": selection["status"],
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
            "limitations": "Preliminary ringdown comparison only",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the elastic-pi ringdown comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, use_fixtures=True, quick=args.quick, dataset_path=args.dataset_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
