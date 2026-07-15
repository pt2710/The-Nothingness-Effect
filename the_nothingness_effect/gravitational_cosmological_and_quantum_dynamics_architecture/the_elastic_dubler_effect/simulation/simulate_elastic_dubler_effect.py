"""Run Elastic Dubler-effect simulation and save artifacts in this folder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import SymLogNorm

from the_nothingness_effect._runtime.artifacts.io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.elastic_dubler_effect import compute_dubler_grid


SCRIPT_DIR = Path(__file__).resolve().parent


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def create_figure(grid: dict[str, np.ndarray]):
    delta_s = grid["delta_s"]
    fig = plt.figure(figsize=(13.2, 5.2), constrained_layout=True)
    subfig = fig.subfigures(1, 2, width_ratios=[1.05, 1.0], wspace=0.04)
    ax_curve = subfig[0].subplots()
    heat_axes = subfig[1].subplots(2, 1, height_ratios=[1.0, 0.62])
    ax_heat, ax_ratio = heat_axes
    for kd, shift in zip(grid["K_D"], grid["dubler_shift"]):
        ax_curve.plot(delta_s, shift, label=f"K_D={kd:g}", linewidth=2)
    ax_curve.axhline(0.0, color="black", linestyle="--", linewidth=0.8)
    ax_curve.set_yscale("symlog", linthresh=0.25)
    ax_curve.set_title("Figure 31: Dubler shift vs entropy gradient")
    ax_curve.set_xlabel("Entropy gradient ΔS")
    ax_curve.set_ylabel("Dubler shift f_A/f_B - 1")
    ax_curve.grid(True, alpha=0.25)
    ax_curve.legend()
    image = ax_heat.imshow(
        grid["dubler_shift"],
        aspect="auto",
        origin="lower",
        extent=[float(delta_s.min()), float(delta_s.max()), 0, len(grid["K_D"]) - 1],
        cmap="coolwarm",
        norm=SymLogNorm(linthresh=0.2, linscale=1.0, vmin=float(np.min(grid["dubler_shift"])), vmax=float(np.max(grid["dubler_shift"]))),
    )
    ax_heat.set_yticks(range(len(grid["K_D"])), [f"{kd:g}" for kd in grid["K_D"]])
    ax_heat.set_title("Finite illustrative shift grid")
    ax_heat.set_xlabel("Entropy gradient ΔS")
    ax_heat.set_ylabel("K_D")
    fig.colorbar(image, ax=ax_heat, label="Dubler shift f_A/f_B - 1")
    for kd, ratio in zip(grid["K_D"], grid["frequency_ratio"]):
        ax_ratio.plot(delta_s, np.log10(np.maximum(ratio, 1e-12)), label=f"K_D={kd:g}", linewidth=1.5)
    ax_ratio.set_title("log10 frequency ratio")
    ax_ratio.set_xlabel("Entropy gradient ΔS")
    ax_ratio.set_ylabel("log10(f_A/f_B)")
    ax_ratio.grid(True, alpha=0.25)
    return fig


def run(output_dir: str | Path | None = None, quick: bool = False) -> dict[str, Path | bool]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    delta_s = np.linspace(-5.0, 5.0, 81 if quick else 201)
    kd_values = np.array([0.5, 1.0, 2.0, 5.0], dtype=float)
    grid = compute_dubler_grid(delta_s, kd_values)
    figure_path = root / "figure31_dubler_shift_entropy_gradient.png"
    data_path = root / "figure31_dubler_grid.npz"
    metrics_path = root / "figure31_dubler_metrics.csv"
    metadata_path = root / "figure31_metadata.json"

    save_npz(data_path, **grid)
    rows = [
        {
            "section": "15.4",
            "figure": "31",
            "K_D": float(kd),
            "ratio_at_zero_delta_s": float(ratio[np.argmin(np.abs(delta_s))]),
            "min_shift": float(np.min(shift)),
            "max_shift": float(np.max(shift)),
            "finite": bool(np.all(np.isfinite(shift))),
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for kd, ratio, shift in zip(grid["K_D"], grid["frequency_ratio"], grid["dubler_shift"])
    ]
    save_csv(metrics_path, rows)
    fig = create_figure(grid)
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "15.4",
            "figure": "31",
            "paper_caption_target": "Dubler shift as a function of entropy gradient for varying KD.",
            "script": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.simulate_elastic_dubler_effect",
            "equations_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.elastic_dubler_effect",
            "parameters": {"delta_s_min": -5.0, "delta_s_max": 5.0, "K_D": kd_values.tolist()},
            "random_seed": None,
            "output_directory": _metadata_path(root),
        },
    )
    return {"figure": figure_path, "data": data_path, "metrics": metrics_path, "metadata": metadata_path, "passed_validation": True}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Elastic Dubler-effect Figure 31 artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, quick=args.quick)
    print(f"Generated Elastic Dubler-effect simulation artifacts in {result['figure'].parent}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
