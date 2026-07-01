"""Run a Dubler redshift comparison with fetched, cached, or fixture fallback data."""

from __future__ import annotations

import argparse
from pathlib import Path

from empirical.comparison.common import resolve_input_dataset
from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from empirical.mappings import dubler_redshift_mapping as mapping


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
            "dataset_name": "redshift_clock",
        }
        if dataset_path is not None
        else resolve_input_dataset("redshift", output_dir=output_dir, use_fixtures=use_fixtures)
    )
    empirical = mapping.prepare_empirical_observable(selection["path"])
    fitted = mapping.fit_parameters(empirical)
    prediction = mapping.prepare_model_prediction(empirical, fitted)
    residuals = mapping.compute_residuals(empirical, prediction)
    metrics = mapping.compute_metrics(empirical, prediction, residuals)
    metrics["data_status"] = selection["status"]
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
    save_rows(
        paths["metrics"],
        [
            {
                **metrics,
                "model": "elastic_dubler_effect",
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
                "# Dubler Redshift Report",
                "",
                f"- data status: {selection['status']}",
                f"- fitted beta: {fitted['beta']:.6f}",
                f"- fitted K_D: {fitted['K_D']:.6f}",
                f"- RMSE: {metrics['RMSE']:.6f}",
                f"- baseline RMSE: {metrics['baseline_RMSE']:.6f}",
                "",
                "Interpretation: preliminary comparison only; not an empirical validation claim.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "dubler_redshift",
            "data_status": selection["status"],
            "input_dataset_path": repo_relative(selection["path"]),
            "fitted_parameters": fitted,
            "output_paths": {name: repo_relative(path) for name, path in paths.items()},
            "source_manifest": selection["manifest"],
            "limitations": "Observable mapping adapter only; not a formal proof substitute.",
        },
    )
    return {
        "paths": paths,
        "metrics": metrics,
        "summary": {
            "model": "elastic_dubler_effect",
            "empirical_dataset": "redshift_clock",
            "data_status": selection["status"],
            "comparison_type": "redshift benchmark comparison",
            "fitted_parameters": fitted,
            "RMSE": metrics["RMSE"],
            "MAE": metrics["MAE"],
            "R2": metrics["R2"],
            "chi_square": metrics["chi_square"],
            "AIC": metrics["AIC"],
            "BIC": metrics["BIC"],
            "baseline_model": "published_or_fixture_baseline_shift",
            "TNE_vs_baseline_note": metrics["TNE_vs_baseline_note"],
            "limitations": "Preliminary comparison only",
            "passed_validation": metrics["passed_validation"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Dubler redshift comparison without claiming empirical validation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--use-fixtures", action="store_true")
    parser.add_argument("--dataset-path", default=None)
    args = parser.parse_args(argv)
    run(
        output_dir=args.output_dir,
        use_fixtures=True,
        quick=args.quick,
        dataset_path=args.dataset_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
