"""Run an EHT horizon/shadow comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import comparison_paths, named_figure_path, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import horizon_eht_mapping as mapping


def run(
    output_dir: str | Path | None = None,
    use_fixtures: bool = True,
    quick: bool = False,
    dataset_path: str | Path | None = None,
    parameter_sweep_level: str = "standard",
) -> dict[str, object]:
    del quick, parameter_sweep_level
    selection = (
        {
            "path": Path(dataset_path),
            "status": "cached",
            "manifest": {},
            "dataset_name": "eht_observables",
        }
        if dataset_path is not None
        else resolve_input_dataset("eht", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
    paths = comparison_paths("eht_horizon", output_dir)
    residual_path = named_figure_path("eht_horizon", "residuals", output_dir)

    rows = []
    for idx, source in enumerate(empirical["source"]):
        rows.append(
            {
                "source": source,
                "ring_diameter_observed": float(empirical["ring_diameter"][idx]),
                "ring_diameter_predicted_shared": float(prediction["ring_prediction"][idx]),
                "ring_diameter_predicted_source_specific": float(prediction["ring_prediction_source_specific"][idx]),
                "shadow_radius_observed": float(empirical["shadow_radius"][idx]),
                "shadow_radius_predicted_shared": float(prediction["shadow_prediction"][idx]),
                "shadow_radius_predicted_source_specific": float(prediction["shadow_prediction_source_specific"][idx]),
                "ring_residual_shared": float(residuals["ring_residual"][idx]),
                "shadow_residual_shared": float(residuals["shadow_residual"][idx]),
                "ring_residual_source_specific": float(residuals["ring_residual_source_specific"][idx]),
                "shadow_residual_source_specific": float(residuals["shadow_residual_source_specific"][idx]),
                "ring_normalized_residual": float(residuals["ring_normalized_residual"][idx]),
                "shadow_normalized_residual": float(residuals["shadow_normalized_residual"][idx]),
                "source_status": empirical["source_status"][idx],
            }
        )

    save_rows(paths["data"], rows)
    save_rows(
        paths["metrics"],
        [
            {
                **metrics,
                "model": "black_hole_dynamics",
                "empirical_dataset": selection["dataset_name"],
                "data_status": selection["status"],
            }
        ],
    )
    mapping.plot_comparison(empirical, prediction, {"curve": paths["figure"], "residual": residual_path})
    report_lines = [
        "# EHT Horizon Report",
        "",
        f"- data status: {selection['status']}",
        f"- shared scale: {fitted['shared_scale']:.6f}",
        f"- source scales: {fitted['source_scales']}",
        f"- threshold contour radius proxy: {fitted['threshold_contour_radius']:.6f}",
        f"- horizon radius proxy: {fitted['horizon_radius_proxy']:.6f}",
        f"- shared-scale RMSE: {metrics['RMSE']:.6f}",
        f"- shared-scale weighted RMSE: {metrics['weighted_RMSE']:.6f}",
        f"- per-source diagnostic RMSE: {metrics['source_specific_RMSE']:.6f}",
        "",
        "Interpretation: published summary observables only. Per-source scaling is a diagnostic interpolation aid, not an independent validation result and not a GRMHD reconstruction claim.",
    ]
    write_report(paths["report"], "\n".join(report_lines))
    write_manifest(
        paths["manifest"],
        {
            "comparison": "eht_horizon",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "fitted_parameters": fitted,
            "output_paths": {
                "data": repo_relative(paths["data"]),
                "metrics": repo_relative(paths["metrics"]),
                "figure": repo_relative(paths["figure"]),
                "residual_figure": repo_relative(residual_path),
                "report": repo_relative(paths["report"]),
                "manifest": repo_relative(paths["manifest"]),
            },
            "source_manifest": selection["manifest"],
            "limitations": "Published summary observables only; not raw EHT image products and not full GRMHD.",
        },
    )
    return {
        "paths": {**paths, "residual_figure": residual_path},
        "metrics": metrics,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "eht_observables",
            "data_status": selection["status"],
            "comparison_type": "horizon/shadow proxy comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "none",
            "TNE_vs_baseline_note": metrics["TNE_vs_baseline_note"],
            "limitations": "Published summary observables only",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the EHT horizon/shadow comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, use_fixtures=True, quick=args.quick, dataset_path=args.dataset_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
