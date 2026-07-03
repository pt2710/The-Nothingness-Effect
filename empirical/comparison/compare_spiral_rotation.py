"""Run a spiral rotation comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import (
    comparison_paths,
    ensure_output_tree,
    morphology_figure_path,
    named_figure_path,
    repo_relative,
    save_rows,
    write_manifest,
    write_report,
)
from empirical.mappings import spiral_galaxy_mapping as mapping
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from equations.artifact_io import save_json


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
    output_tree = ensure_output_tree(output_dir)
    arm_mode_rows = []
    arm_mode_summary: dict[str, dict[str, float | str]] = {}
    for arm_mode in (2, 3, 4, "mixed"):
        mode_fit = mapping.fit_parameters(empirical, parameter_sweep_level=sweep_level, arm_modes=(arm_mode,))
        mode_prediction = mapping.prepare_model_prediction(empirical, mode_fit)
        mode_residuals = mapping.compute_residuals(empirical, mode_prediction)
        mode_metrics = mapping.compute_metrics(empirical, mode_prediction, mode_residuals)
        row = {
            "arm_mode": str(arm_mode),
            "RMSE": float(mode_metrics["RMSE"]),
            "R2": float(mode_metrics["R2"]),
            "density_arm_contrast": float(mode_metrics["density_arm_contrast"]),
            "dominant_mode": float(mode_metrics["dominant_mode"]),
            "target_mode_ratio": float(mode_metrics["target_mode_ratio"]),
            "spiral_order_parameter": float(mode_metrics["spiral_order_parameter"]),
            "TNE_vs_baseline_note": mode_metrics["TNE_vs_baseline_note"],
        }
        arm_mode_rows.append(row)
        arm_mode_summary[str(arm_mode)] = row

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
    arm_mode_data_path = output_tree["data"] / "spiral_rotation_arm_mode_comparison.csv"
    arm_mode_metrics_path = output_tree["metrics"] / "spiral_rotation_arm_mode_metrics.csv"
    arm_mode_figure_path = output_tree["figures"] / "spiral_rotation_arm_mode_comparison.png"
    arm_mode_report_path = output_tree["reports"] / "spiral_rotation_arm_mode_report.md"
    arm_mode_manifest_path = output_tree["manifests"] / "spiral_rotation_arm_mode_manifest.json"
    save_rows(arm_mode_data_path, arm_mode_rows)
    save_rows(arm_mode_metrics_path, arm_mode_rows)
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.2), constrained_layout=True)
    labels = [row["arm_mode"] for row in arm_mode_rows]
    axes[0].bar(labels, [float(row["RMSE"]) for row in arm_mode_rows], color="#4c78a8")
    axes[0].set_title("Preliminary residual fit by arm mode")
    axes[0].set_ylabel("RMSE")
    axes[0].grid(True, axis="y", alpha=0.2)
    axes[1].bar(labels, [float(row["density_arm_contrast"]) for row in arm_mode_rows], color="#f58518")
    axes[1].set_title("Density arm contrast")
    axes[1].grid(True, axis="y", alpha=0.2)
    axes[2].bar(labels, [float(row["dominant_mode"]) for row in arm_mode_rows], color="#54a24b")
    axes[2].set_title("Dominant mode")
    axes[2].grid(True, axis="y", alpha=0.2)
    fig.suptitle("Finite spiral arm-mode proxy comparison")
    fig.savefig(arm_mode_figure_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
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
        f"- selected arm mode: {prediction['fitted_parameters']['arm_mode']}",
        f"- spiral order parameter: {prediction['spiral_order_parameter']:.6f}",
        f"- m=1 / m=2 / m=3 / m=4 amplitude: {prediction['mode_1_amplitude']:.6f} / {prediction['mode_2_amplitude']:.6f} / {prediction['mode_3_amplitude']:.6f} / {prediction['mode_4_amplitude']:.6f}",
        f"- dominant mode: m{int(prediction['dominant_mode'])}",
        f"- target mode ratio: {prediction['target_mode_ratio']:.6f}",
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
    write_report(
        arm_mode_report_path,
        "\n".join(
            [
                "# Spiral Rotation Arm-Mode Report",
                "",
                "Finite spiral-mode comparison under the implemented proxy mapping. This is not morphology validation, not a dark-matter replacement claim, and not a full astrophysical simulation.",
                "",
                *[
                    f"- arm_mode={row['arm_mode']}: RMSE={float(row['RMSE']):.6f}, dominant_mode=m{int(float(row['dominant_mode']))}, target_mode_ratio={float(row['target_mode_ratio']):.6f}"
                    for row in arm_mode_rows
                ],
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
                "residual_figure": repo_relative(residual_path),
                "morphology_figure": repo_relative(morphology_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "source_manifest": selection["manifest"],
            "limitations": "Finite toy-model mapping only; not a dark-matter replacement claim and not a full astrophysical simulation.",
        },
    )
    save_json(
        arm_mode_manifest_path,
        {
            "comparison": "spiral_rotation_arm_mode",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "parameter_sweep_level": sweep_level,
            "arm_mode_rows": arm_mode_rows,
            "best_preliminary_fit": min(arm_mode_rows, key=lambda row: float(row["RMSE"])),
            "output_paths": {
                "data": repo_relative(arm_mode_data_path),
                "metrics": repo_relative(arm_mode_metrics_path),
                "figure": repo_relative(arm_mode_figure_path),
                "report": repo_relative(arm_mode_report_path),
                "manifest": repo_relative(arm_mode_manifest_path),
            },
            "limitations": "Preliminary proxy fitting only; no morphology validation claim and no dark-matter replacement claim.",
        },
    )
    return {
        "paths": {
            **paths,
            "morphology_figure": morphology_path,
            "residual_figure": residual_path,
            "arm_mode_data": arm_mode_data_path,
            "arm_mode_metrics": arm_mode_metrics_path,
            "arm_mode_figure": arm_mode_figure_path,
            "arm_mode_report": arm_mode_report_path,
            "arm_mode_manifest": arm_mode_manifest_path,
        },
        "metrics": metrics,
        "arm_mode_summary": arm_mode_summary,
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
