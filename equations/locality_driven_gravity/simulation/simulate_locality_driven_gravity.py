"""Run locality-driven gravity simulation and save artifacts in this folder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from equations.locality_driven_gravity.locality_driven_gravity import (
    LocalityGravityParams,
    compute_spiral_metrics,
    simulate_locality_spiral,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def _metadata_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def create_figure(history, metrics):
    initial = history[0]
    final = history[-1]
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8), constrained_layout=True)
    axes[0].scatter(initial[:, 0], initial[:, 1], s=10, alpha=0.75, color="#4c78a8")
    axes[0].set_title("Initial finite particle field")
    density = axes[1].hexbin(final[:, 0], final[:, 1], gridsize=24, cmap="magma", mincnt=1)
    axes[1].scatter(final[:, 0], final[:, 1], s=5, alpha=0.25, color="white")
    axes[1].set_title("Final spiral-like density field")
    fig.colorbar(density, ax=axes[1], label="particle count")
    stride = max(1, history.shape[1] // 80)
    for particle_path in history[:, ::stride, :].transpose(1, 0, 2):
        axes[2].plot(particle_path[:, 0], particle_path[:, 1], linewidth=0.55, alpha=0.4)
    axes[2].scatter(final[:, 0], final[:, 1], s=6, color="#54a24b", alpha=0.65)
    axes[2].set_title("Spiral-like trajectory winding")
    for ax in axes:
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.2)
    radius = np.linalg.norm(final, axis=1)
    theta = np.unwrap(np.arctan2(final[:, 1], final[:, 0]))
    axes[0].text(
        0.03,
        0.04,
        f"spiral order diagnostic={metrics['spiral_order_parameter']:.3f}\n"
        f"mean radius={np.mean(radius):.2f}",
        transform=axes[0].transAxes,
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    axes[2].plot([], [], alpha=0.0, label=f"phase span={np.ptp(theta):.2f} rad")
    axes[2].legend(loc="upper left", frameon=True)
    fig.suptitle("Figure 6: Locality-driven spiral-like trajectory emergence", fontsize=12)
    return fig


def run(
    output_dir: str | Path | None = None,
    seed: int = 2710,
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, Path | bool]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = LocalityGravityParams(
        n_particles=120 if quick else 240,
        steps=60 if quick else (steps or 220),
        shear=0.18,
        damping=0.995,
    )
    result = simulate_locality_spiral(params=params, seed=seed)
    metrics = compute_spiral_metrics(result["history"])
    figure_path = root / "figure6_locality_driven_spiral.png"
    data_path = root / "figure6_spiral_particles.npz"
    metrics_path = root / "figure6_spiral_metrics.csv"
    metadata_path = root / "figure6_metadata.json"
    save_npz(data_path, history=result["history"], positions=result["positions"], velocities=result["velocities"])
    save_csv(metrics_path, [{"section": "16.4", "figure": "6", **metrics, "claim_boundary": CLAIM_BOUNDARY}])
    fig = create_figure(result["history"], metrics)
    save_figure(fig, figure_path)
    plt.close(fig)
    write_metadata(
        metadata_path,
        {
            "section": "16.4",
            "figure": "6",
            "paper_caption_target": "Simulation of spiral structure emergence under locality-driven gravity.",
            "script": "equations.locality_driven_gravity.simulation.simulate_locality_driven_gravity",
            "equations_module": "equations.locality_driven_gravity.locality_driven_gravity",
            "parameters": params.__dict__,
            "random_seed": seed,
            "output_directory": _metadata_path(root),
        },
    )
    return {"figure": figure_path, "data": data_path, "metrics": metrics_path, "metadata": metadata_path, "passed_validation": metrics["nan_count"] == 0}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate locality-driven gravity artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--seed", type=int, default=2710)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, seed=args.seed, steps=args.steps, quick=args.quick)
    print(f"Generated locality-driven gravity simulation artifacts in {result['figure'].parent}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
