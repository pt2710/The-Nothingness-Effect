"""Generate Section 23 Figures 48-49 and Table 19 metrics."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from equations.noether_tne import (
    NoetherParams,
    noether_validation_metrics,
    simulate_fp_gauss_identity,
    simulate_kd_flux_under_phase_shift,
)
from utils.output_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from visualizations.plot_noether_validation import create_fp_gauss_figure, create_kd_flux_figure


def run(
    output_dir: str | Path = "outputs",
    grid_size: int = 128,
    quick: bool = False,
) -> dict[str, object]:
    root = Path(output_dir)
    params = NoetherParams(grid_size=32 if quick else grid_size, time_steps=40 if quick else 120)
    flux_result = simulate_kd_flux_under_phase_shift(params)
    gauss_result = simulate_fp_gauss_identity(params.grid_size, params)
    validation_rows = noether_validation_metrics(flux_result["metrics"], gauss_result["metrics"])

    figure48_path = root / "figures" / "section23" / "figure48_kd_flux_phase_shift.png"
    figure49_path = root / "figures" / "section23" / "figure49_fp_gauss_identity_128x128.png"
    flux_data_path = root / "data" / "noether_tne" / "figure48_kd_flux_trace.npz"
    gauss_data_path = root / "data" / "noether_tne" / "figure49_fp_gauss_grid.npz"
    metrics_path = root / "metrics" / "section23" / "table19_noether_validation_metrics.csv"
    metadata_path = root / "data" / "noether_tne" / "section23_noether_metadata.json"

    save_npz(
        flux_data_path,
        x=flux_result["x"],
        time=flux_result["time"],
        theta=flux_result["theta"],
        pi_E=flux_result["pi_E"],
        rx=flux_result["rx"],
    )
    save_npz(
        gauss_data_path,
        x=gauss_result["x"],
        y=gauss_result["y"],
        theta=gauss_result["theta"],
        pi_E=gauss_result["pi_E"],
        residual=gauss_result["residual"],
    )
    save_csv(
        metrics_path,
        [
            {"section": "23.4", "table": "19", **row, "claim_boundary": CLAIM_BOUNDARY}
            for row in validation_rows
        ],
    )
    fig48 = create_kd_flux_figure(flux_result)
    fig49 = create_fp_gauss_figure(gauss_result)
    save_figure(fig48, figure48_path)
    save_figure(fig49, figure49_path)
    plt.close(fig48)
    plt.close(fig49)
    write_metadata(
        metadata_path,
        {
            "section": "23.4",
            "figure": "48 and 49",
            "table": "19",
            "paper_caption_target": (
                "KD flux Rx(t) under fp phase shift and numerical check of fp-Gauss identity "
                "on a 128^2 grid."
            ),
            "script": "simulations.run_noether_figures48_49",
            "equations_module": "equations.noether_tne",
            "parameters": params.__dict__,
            "random_seed": None,
            "output_files": {
                "figure48": str(figure48_path.as_posix()),
                "figure49": str(figure49_path.as_posix()),
                "flux_data": str(flux_data_path.as_posix()),
                "gauss_data": str(gauss_data_path.as_posix()),
                "metrics": str(metrics_path.as_posix()),
            },
        },
    )
    return {
        "figure48": figure48_path,
        "figure49": figure49_path,
        "data": [flux_data_path, gauss_data_path],
        "metrics": metrics_path,
        "metadata": metadata_path,
        "passed_validation": all(bool(row["passed"]) for row in validation_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate finite illustrative Section 23 artifacts.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--grid-size", type=int, default=128)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, grid_size=args.grid_size, quick=args.quick)
    print(f"Generated Figure 48 artifact: {result['figure48']}")
    print(f"Generated Figure 49 artifact: {result['figure49']}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
