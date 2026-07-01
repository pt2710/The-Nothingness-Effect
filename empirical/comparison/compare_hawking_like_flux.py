"""Deprecated compatibility shim for the former Hawking empirical comparison slot."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from empirical.io import comparison_paths, repo_relative, save_rows, write_manifest, write_report
from equations.artifact_io import save_figure
from theoretical_benchmarks.hawking.compare_tne_hawking_like_flux import run as run_theoretical_comparison
from theoretical_benchmarks.hawking.simulation.simulate_hawking_theoretical_benchmark import run as run_theoretical_benchmark


def run(
    output_dir: str | Path | None = None,
    use_fixtures: bool = True,
    quick: bool = False,
    dataset_path: str | Path | None = None,
    parameter_sweep_level: str = "standard",
) -> dict[str, object]:
    del use_fixtures, quick, dataset_path, parameter_sweep_level
    benchmark = run_theoretical_benchmark()
    comparison = run_theoretical_comparison()
    metrics_row = dict(comparison["rows"][0])
    paths = comparison_paths("hawking_like_flux", output_dir)
    save_rows(
        paths["data"],
        [
            {
                "status": "deprecated_empirical_slot",
                "data_status": "theoretical_benchmark",
                "redirected_to": "theoretical_benchmarks/hawking",
            }
        ],
    )
    save_rows(paths["metrics"], [metrics_row])
    fig, ax = plt.subplots(figsize=(7.0, 4.0), constrained_layout=True)
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "Hawking empirical slot deprecated.\nUse theoretical_benchmarks/hawking/ instead.",
        ha="center",
        va="center",
        fontsize=12,
    )
    save_figure(fig, paths["figure"], dpi=220)
    plt.close(fig)
    write_report(
        paths["report"],
        "\n".join(
            [
                "# Hawking-like Flux Compatibility Note",
                "",
                "This empirical entrypoint is deprecated.",
                "No direct astrophysical empirical Hawking-radiation dataset is fetched here.",
                "Use the Hawking theoretical benchmark artifacts under `theoretical_benchmarks/hawking/`.",
                "",
                "This is a theoretical consistency comparison, not empirical validation.",
            ]
        ),
    )
    write_manifest(
        paths["manifest"],
        {
            "comparison": "hawking_like_flux",
            "data_status": "theoretical_benchmark",
            "deprecated": True,
            "redirected_to": "theoretical_benchmarks/hawking",
            "benchmark_paths": {name: str(path) for name, path in benchmark["paths"].items()},
            "comparison_report": str(comparison["report"]),
            "comparison_manifest": str(comparison["manifest"]),
            "compatibility_figure": repo_relative(paths["figure"]),
        },
    )
    return {
        "paths": paths,
        "metrics": metrics_row,
        "summary": {
            "model": "black_hole_dynamics",
            "empirical_dataset": "hawking_theoretical_benchmark",
            "data_status": "theoretical_benchmark",
            "comparison_type": "deprecated empirical slot redirected to theoretical benchmark",
            "fitted_parameters": metrics_row.get("fitted_parameters", {}),
            "RMSE": metrics_row["RMSE"],
            "MAE": metrics_row["MAE"],
            "R2": metrics_row["R2"],
            "chi_square": float("nan"),
            "AIC": float("nan"),
            "BIC": float("nan"),
            "baseline_model": "hawking_theoretical_formulas",
            "TNE_vs_baseline_note": "Theoretical benchmark consistency only; not empirical validation.",
            "limitations": "Deprecated empirical slot; use theoretical benchmark outputs instead.",
            "passed_validation": metrics_row["passed_benchmark_checks"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deprecated Hawking empirical-comparison shim.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
