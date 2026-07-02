"""Run a spiral rotation comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import (
    comparison_paths,
    morphology_figure_path,
    named_figure_path,
    repo_relative,
    save_rows,
    write_manifest,
    write_report,
)
from empirical.mappings import spiral_galaxy_mapping as mapping


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
            "dataset_name": "galaxy_rotation",
        }
        if dataset_path is not None
        else resolve_input_dataset("galaxy", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    sweep_level = "quick" if quick else parameter_sweep_level
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical, parameter_sweep_level=sweep_level)
    fitted["parameter_sweep_level"] = sweep_level
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
    paths = comparison_paths("spiral_rotation", output_dir)
    morphology_path = morphology_figure_path("spiral", output_dir)
    residual_path = named_figure_path("spiral_rotation", "residuals", output_dir)

    rows = []
    for idx, radius in enumerate(empirical["radius"]):
        rows.append(
            {
                "radius": float(radius),
                "radius_kpc": float(empirical["radius_kpc"][idx]),
                "observed_velocity": float(empirical["velocity"][idx]),
                "observed_velocity_kms": float(empirical["velocity_kms"][idx]),
                "velocity_uncertainty": float(empirical["velocity_uncertainty"][idx]),
                "velocity_uncertainty_kms": float(empirical["velocity_uncertainty_kms"][idx]),
                "tne_prediction": float(prediction["tne_prediction"][idx]),
                "baseline_prediction": float(prediction["baseline_prediction"][idx]),
                "flat_baseline_prediction": float(prediction["flat_baseline_prediction"][idx]),
                "linear_baseline_prediction": float(prediction["linear_baseline_prediction"][idx]),
                "smoothed_empirical_reference": float(prediction["smoothed_empirical_reference"][idx]),
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
    mapping.plot_comparison(
        empirical,
        prediction,
        {"curve": paths["figure"], "residual": residual_path, "morphology": morphology_path},
    )
    report_lines = [
        "# Spiral Rotation Report",
        "",
        f"- data status: {selection['status']}",
        f"- parameter sweep level: {sweep_level}",
        f"- radius scale: {prediction['fitted_parameters']['radius_scale']:.6f}",
        f"- velocity scale: {prediction['fitted_parameters']['velocity_scale']:.6f}",
        f"- aggregation mix (mean vs median): {prediction['fitted_parameters']['aggregation_mix']:.6f}",
        f"- galaxy count: {int(metrics['galaxy_count'])}",
        f"- per-galaxy baseline family: {prediction['fitted_parameters']['selected_baselines']}",
        f"- spiral order parameter: {prediction['spiral_order_parameter']:.6f}",
        f"- m=2 / m=3 amplitude: {prediction['mode_2_amplitude']:.6f} / {prediction['mode_3_amplitude']:.6f}",
        f"- pitch-angle proxy: {prediction['pitch_angle_proxy']:.6f}",
        f"- density arm contrast: {prediction['density_arm_contrast']:.6f}",
        f"- angular momentum drift: {prediction['angular_momentum_drift']:.6f}",
        f"- RMSE: {metrics['RMSE']:.6f}",
        f"- selected baseline RMSE: {metrics['baseline_RMSE']:.6f}",
        f"- flat / linear baseline RMSE: {metrics['flat_baseline_RMSE']:.6f} / {metrics['linear_baseline_RMSE']:.6f}",
        "",
        "Interpretation: finite illustrative rotation-curve comparison only. The locality-driven spiral proxy is not a full astrophysical simulation, not a dark-matter-replacement claim, and not an empirical validation claim.",
    ]
    write_report(paths["report"], "\n".join(report_lines))
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
                "residual_figure": repo_relative(residual_path),
                "morphology_figure": repo_relative(morphology_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "source_manifest": selection["manifest"],
            "limitations": "Finite toy-model mapping only; not a dark-matter replacement claim and not a full astrophysical simulation.",
        },
    )
    return {
        "paths": {**paths, "morphology_figure": morphology_path, "residual_figure": residual_path},
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
            "baseline_model": metrics["baseline_model"],
            "TNE_vs_baseline_note": metrics["TNE_vs_baseline_note"],
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
