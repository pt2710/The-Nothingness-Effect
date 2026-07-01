"""Run an observer-memory comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import observer_memory_mapping as mapping


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
        else resolve_input_dataset("memory", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
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
    mapping.plot_comparison(empirical, prediction, paths["figure"])
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Observer Memory Report",
                "",
                f"- data status: {selection['status']}",
                f"- amplitude scale: {fitted['amplitude_scale']:.6f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                "",
                "Interpretation: preliminary memory-like proxy comparison only; not an empirical validation claim.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "observer_memory",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "source_manifest": selection["manifest"],
            "limitations": "Memory proxy alignment only; not a direct observational memory measurement.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "ligo_waveforms",
            "data_status": selection["status"],
            "comparison_type": "memory-trace comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "none",
            "TNE_vs_baseline_note": "Preliminary comparison only",
            "limitations": "Memory proxy uses waveform-style comparison data",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the observer-memory comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, use_fixtures=True, quick=args.quick, dataset_path=args.dataset_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
