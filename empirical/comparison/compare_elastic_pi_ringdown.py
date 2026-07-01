"""Run an elastic-pi ringdown comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import (
    comparison_paths,
    named_figure_path,
    repo_relative,
    save_rows,
    write_manifest,
    write_report,
)
from empirical.mappings import ripple_ringdown_mapping as mapping


def run(
    output_dir: str | Path | None = None,
    use_fixtures: bool = True,
    quick: bool = False,
    dataset_path: str | Path | None = None,
    parameter_sweep_level: str = "standard",
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
    sweep_level = "quick" if quick else parameter_sweep_level
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical, parameter_sweep_level=sweep_level)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
    paths = comparison_paths("elastic_pi_ringdown", output_dir)
    residual_path = named_figure_path("elastic_pi_ringdown", "residuals", output_dir)
    envelope_path = named_figure_path("elastic_pi_ringdown", "envelope", output_dir)

    rows = []
    full_length = len(empirical["time_raw"])
    aligned_start = empirical["window_start_index"]
    aligned_stop = empirical["window_stop_index"]
    for idx in range(full_length):
        in_window = aligned_start <= idx < aligned_stop
        row = {
            "time_raw": float(empirical["time_raw"][idx]),
            "window_selected": bool(in_window),
            "observed_strain_raw": float(empirical["strain_raw_full"][idx]),
            "event_id": empirical["event_id"][idx],
            "source_status": empirical["source_status"][idx],
        }
        if in_window:
            window_idx = idx - aligned_start
            row.update(
                {
                    "time_aligned": float(empirical["time"][window_idx]),
                    "observed_strain_normalized": float(empirical["strain"][window_idx]),
                    "strain_uncertainty_raw": float(empirical["strain_uncertainty_raw"][window_idx]),
                    "strain_uncertainty_normalized": float(empirical["strain_uncertainty"][window_idx]),
                    "tne_prediction_raw": float(prediction["tne_prediction_raw"][window_idx]),
                    "baseline_prediction_raw": float(prediction["baseline_prediction_raw"][window_idx]),
                    "tne_prediction_normalized": float(prediction["tne_prediction"][window_idx]),
                    "baseline_prediction_normalized": float(prediction["baseline_prediction"][window_idx]),
                    "tne_residual": float(residuals["tne_residual"][window_idx]),
                    "baseline_residual": float(residuals["baseline_residual"][window_idx]),
                    "tne_residual_envelope": float(residuals["tne_residual_envelope"][window_idx]),
                    "baseline_residual_envelope": float(residuals["baseline_residual_envelope"][window_idx]),
                }
            )
        rows.append(row)

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
    mapping.plot_comparison(
        empirical,
        prediction,
        {"curve": paths["figure"], "residual": residual_path, "envelope": envelope_path},
    )
    report_lines = [
        "# Elastic-pi Ringdown Report",
        "",
        f"- data status: {selection['status']}",
        f"- parameter sweep level: {sweep_level}",
        f"- aligned window start (raw time): {empirical['window_start_time_raw']:.6f}",
        f"- TNE time scale: {prediction['fitted_parameters']['tne']['time_scale']:.6f}",
        f"- TNE time shift: {prediction['fitted_parameters']['tne']['time_shift']:.6f}",
        f"- TNE envelope weight: {prediction['fitted_parameters']['tne']['envelope_weight']:.6f}",
        f"- baseline tau: {prediction['fitted_parameters']['baseline']['tau']:.6f}",
        f"- RMSE: {metrics['RMSE']:.6f}",
        f"- baseline RMSE: {metrics['baseline_RMSE']:.6f}",
        f"- train/test RMSE: {metrics['train_RMSE']:.6f} / {metrics['test_RMSE']:.6f}",
        f"- baseline train/test RMSE: {metrics['baseline_train_RMSE']:.6f} / {metrics['baseline_test_RMSE']:.6f}",
        "",
        "Interpretation: finite illustrative ringdown comparison only. This is an improved preliminary residual fit under the implemented proxy mapping when the metrics say so; otherwise the damped-sinusoid baseline remains the stronger fit under the same window.",
    ]
    write_report(paths["report"], "\n".join(report_lines))
    write_manifest(
        paths["manifest"],
        {
            "comparison": "elastic_pi_ringdown",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "selected_ringdown_window": {
                "start_index": empirical["window_start_index"],
                "stop_index": empirical["window_stop_index"],
                "start_time_raw": empirical["window_start_time_raw"],
            },
            "fitted_parameters": prediction["fitted_parameters"],
            "output_paths": {
                "data": repo_relative(paths["data"]),
                "metrics": repo_relative(paths["metrics"]),
                "figure": repo_relative(paths["figure"]),
                "residual_figure": repo_relative(residual_path),
                "envelope_figure": repo_relative(envelope_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "source_manifest": selection["manifest"],
            "limitations": "Finite illustrative dual-proxy ringdown comparison only; not a full waveform model and not an empirical validation claim.",
        },
    )
    return {
        "paths": {**paths, "residual_figure": residual_path, "envelope_figure": envelope_path},
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
            "limitations": "Finite toy-model ringdown comparison only",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the elastic-pi ringdown comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    parser.add_argument("--parameter-sweep-level", default="standard", choices=["quick", "standard", "extended"])
    args = parser.parse_args(argv)
    run(
        output_dir=args.output_dir,
        use_fixtures=True,
        quick=args.quick,
        dataset_path=args.dataset_path,
        parameter_sweep_level="quick" if args.quick else args.parameter_sweep_level,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
