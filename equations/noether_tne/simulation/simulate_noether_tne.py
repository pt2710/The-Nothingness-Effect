"""Run Noether TNE validation simulation and save artifacts in this folder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from equations.noether_tne.noether_tne import (
    NoetherParams,
    noether_validation_metrics,
    simulate_fp_gauss_identity,
    simulate_kd_flux_under_phase_shift,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _flux_figure(flux_result):
    time = flux_result["time"]
    rx = flux_result["rx"]
    metrics = flux_result["metrics"]
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.plot(time, rx, label="Rx(t)", linewidth=2)
    ax.axhline(rx[0], color="black", linestyle="--", label="Rx(0)")
    ax.set_title(f"Figure 48: KD flux Rx(t) under fp phase shift\nmax deviation={metrics['rx_max_deviation']:.3e}")
    ax.set_xlabel("time")
    ax.set_ylabel("KD flux Rx")
    ax.grid(True, alpha=0.25)
    ax.legend()
    return fig


def _gauss_figure(gauss_result):
    residual = gauss_result["residual"]
    metrics = gauss_result["metrics"]
    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    image = ax.imshow(residual, origin="lower", cmap="magma")
    ax.set_title(f"Figure 49: fp-Gauss identity check on 128^2 grid\ninf norm={metrics['gauss_residual_inf_norm']:.3e}")
    ax.set_xlabel("grid x")
    ax.set_ylabel("grid y")
    fig.colorbar(image, ax=ax, label="residual")
    return fig


def run(output_dir: str | Path | None = None, grid_size: int = 128, quick: bool = False) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = NoetherParams(grid_size=32 if quick else grid_size, time_steps=40 if quick else 120)
    flux_result = simulate_kd_flux_under_phase_shift(params)
    gauss_result = simulate_fp_gauss_identity(params.grid_size, params)
    validation_rows = noether_validation_metrics(flux_result["metrics"], gauss_result["metrics"])
    figure48_path = root / "figure48_kd_flux_phase_shift.png"
    figure49_path = root / "figure49_fp_gauss_identity_128x128.png"
    flux_data_path = root / "figure48_kd_flux_trace.npz"
    gauss_data_path = root / "figure49_fp_gauss_grid.npz"
    metrics_path = root / "table19_noether_validation_metrics.csv"
    metadata_path = root / "section23_noether_metadata.json"
    save_npz(flux_data_path, x=flux_result["x"], time=flux_result["time"], theta=flux_result["theta"], pi_E=flux_result["pi_E"], rx=flux_result["rx"])
    save_npz(gauss_data_path, x=gauss_result["x"], y=gauss_result["y"], theta=gauss_result["theta"], pi_E=gauss_result["pi_E"], residual=gauss_result["residual"])
    save_csv(metrics_path, [{"section": "23.4", "table": "19", **row, "claim_boundary": CLAIM_BOUNDARY} for row in validation_rows])
    fig48 = _flux_figure(flux_result)
    fig49 = _gauss_figure(gauss_result)
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
            "paper_caption_target": "KD flux Rx(t) under fp phase shift and numerical check of fp-Gauss identity on a 128^2 grid.",
            "script": "equations.noether_tne.simulation.simulate_noether_tne",
            "equations_module": "equations.noether_tne.noether_tne",
            "parameters": params.__dict__,
            "random_seed": None,
            "output_directory": _metadata_path(root),
        },
    )
    return {"figure48": figure48_path, "figure49": figure49_path, "data": [flux_data_path, gauss_data_path], "metrics": metrics_path, "metadata": metadata_path, "passed_validation": all(bool(row["passed"]) for row in validation_rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Noether TNE artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--grid-size", type=int, default=128)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, grid_size=args.grid_size, quick=args.quick)
    print(f"Generated Noether TNE simulation artifacts in {result['metrics'].parent}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
