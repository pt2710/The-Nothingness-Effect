"""Run locality-driven spiral simulation and save manuscript-linked artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, save_csv, save_figure, save_npz, write_metadata
from equations.locality_driven_gravity.locality_driven_gravity import (
    BodyType,
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


def create_figure(result: dict[str, object], metrics: dict[str, float]):
    history = np.asarray(result["history"], dtype=float)
    density_history = np.asarray(result["density_history"], dtype=float)
    tension_history = np.asarray(result["tension_history"], dtype=float)
    masses = np.asarray(result["masses"], dtype=float)
    body_types = np.asarray(result["body_types"], dtype=object)
    initial = history[0]
    final = history[-1]
    final_density = density_history[-1]
    final_tension = tension_history[-1]
    grid_axis = np.asarray(result["grid_axis"], dtype=float)
    xx, yy = np.meshgrid(grid_axis, grid_axis)

    fig = plt.figure(figsize=(14.8, 9.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)
    ax_initial = fig.add_subplot(gs[0, 0])
    ax_final = fig.add_subplot(gs[0, 1])
    ax_density = fig.add_subplot(gs[0, 2])
    ax_traj = fig.add_subplot(gs[1, 0])
    ax_metrics = fig.add_subplot(gs[1, 1])
    ax_tension = fig.add_subplot(gs[1, 2])

    initial_sizes = 8 + 8 * masses / (np.max(masses) + 1e-12)
    final_sizes = 8 + 8 * masses / (np.max(masses) + 1e-12)
    ax_initial.scatter(initial[:, 0], initial[:, 1], s=initial_sizes, c=np.linalg.norm(initial, axis=1), cmap="magma", alpha=0.9)
    ax_initial.scatter(initial[body_types == BodyType.CENTRAL_MASS.value, 0], initial[body_types == BodyType.CENTRAL_MASS.value, 1], s=120, c="#f2cf63", marker="*", label="central mass")
    ax_initial.set_title("Initial finite body field")
    ax_initial.legend(loc="upper right")

    density_map = ax_final.imshow(
        final_density,
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="inferno",
        alpha=0.52,
    )
    ax_final.contour(xx, yy, final_density, levels=6, colors="white", linewidths=0.7, alpha=0.6)
    ax_final.scatter(final[:, 0], final[:, 1], s=final_sizes, c=np.linalg.norm(final, axis=1), cmap="viridis", alpha=0.82)
    ax_final.scatter(final[body_types == BodyType.CENTRAL_MASS.value, 0], final[body_types == BodyType.CENTRAL_MASS.value, 1], s=140, c="#ffe08a", marker="*", edgecolors="black")
    ax_final.set_title("Final locality-driven spiral proxy")
    fig.colorbar(density_map, ax=ax_final, label="density proxy")

    density_image = ax_density.imshow(
        final_density,
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="magma",
    )
    ax_density.contour(xx, yy, final_tension, levels=6, colors="#9ecae1", linewidths=0.8)
    ax_density.set_title("Final density ridges and tension contours")
    fig.colorbar(density_image, ax=ax_density, label="density proxy")

    stride = max(1, history.shape[1] // 40)
    for particle_path in history[:, 1::stride, :].transpose(1, 0, 2):
        ax_traj.plot(particle_path[:, 0], particle_path[:, 1], linewidth=0.55, alpha=0.45, color="#4c78a8")
    ax_traj.scatter(final[:, 0], final[:, 1], s=5, color="#54a24b", alpha=0.65)
    ax_traj.set_title("Trajectory winding and spiral-arm emergence")

    metric_lines = [
        f"spiral_order_parameter = {metrics['spiral_order_parameter']:.3f}",
        f"m=2 amplitude = {metrics['mode_2_amplitude']:.3f}",
        f"m=3 amplitude = {metrics['mode_3_amplitude']:.3f}",
        f"pitch_angle_proxy = {metrics['pitch_angle_proxy']:.3f}",
        f"density_arm_contrast = {metrics['density_arm_contrast']:.3f}",
        f"arm_asymmetry_index = {metrics['arm_asymmetry_index']:.3f}",
        f"angular_momentum_drift = {metrics['angular_momentum_drift']:.4f}",
        f"elastic_tension_max = {metrics['elastic_tension_max']:.3f}",
    ]
    ax_metrics.axis("off")
    ax_metrics.set_title("Spiral metrics")
    ax_metrics.text(
        0.02,
        0.98,
        "\n".join(metric_lines),
        va="top",
        ha="left",
        fontsize=10,
        family="monospace",
        bbox={"facecolor": "#f7f7f7", "edgecolor": "#d0d0d0", "boxstyle": "round,pad=0.4"},
    )

    tension_map = ax_tension.imshow(
        final_tension,
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="cividis",
    )
    ax_tension.contour(xx, yy, final_density, levels=5, colors="white", linewidths=0.7, alpha=0.55)
    ax_tension.set_title("Entropic-elastic tension field")
    fig.colorbar(tension_map, ax=ax_tension, label="tension proxy")

    for ax in [ax_initial, ax_final, ax_density, ax_traj, ax_tension]:
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True, alpha=0.16)

    fig.suptitle("Figure 6: TNE locality-driven galaxy proxy", fontsize=13)
    return fig


def run(
    output_dir: str | Path | None = None,
    seed: int = 2710,
    steps: int | None = None,
    quick: bool = False,
) -> dict[str, Path | bool]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = LocalityGravityParams(
        n_particles=96 if quick else 240,
        steps=72 if quick else (steps or 220),
        grid_size=32 if quick else 52,
        radial_scale=3.1,
        central_mass=200.0 if quick else 220.0,
    )
    result = simulate_locality_spiral(params=params, seed=seed)
    metrics = compute_spiral_metrics(
        result["history"],
        velocity_history=result["velocity_history"],
        masses=result["masses"],
        body_types=result["body_types"],
        tension_field=result["tension_history"][-1],
    )
    figure_path = root / "figure6_locality_driven_spiral.png"
    data_path = root / "figure6_spiral_particles.npz"
    metrics_path = root / "figure6_spiral_metrics.csv"
    metadata_path = root / "figure6_metadata.json"
    locality_metrics_path = root / "locality_spiral_metrics.csv"
    locality_metadata_path = root / "locality_spiral_metadata.json"

    save_npz(
        data_path,
        history=result["history"],
        velocity_history=result["velocity_history"],
        density_history=result["density_history"],
        tension_history=result["tension_history"],
        entropy_history=result["entropy_history"],
        masses=result["masses"],
        body_types=result["body_types"],
        grid_axis=result["grid_axis"],
    )
    csv_row = {"section": "16.4", "figure": "6", **metrics, "claim_boundary": CLAIM_BOUNDARY}
    save_csv(metrics_path, [csv_row])
    save_csv(locality_metrics_path, [csv_row])
    fig = create_figure(result, metrics)
    save_figure(fig, figure_path)
    plt.close(fig)

    metadata_payload = {
        "section": "16.4",
        "figure": "6",
        "paper_caption_target": "Finite spiral-formation proxy under locality-driven gravity plus entropic-elastic feedback.",
        "script": "equations.locality_driven_gravity.simulation.simulate_locality_driven_gravity",
        "equations_module": "equations.locality_driven_gravity.entropic_elastic_spiral",
        "parameters": params.__dict__,
        "random_seed": seed,
        "output_directory": _metadata_path(root),
        "metrics": metrics,
        "claim_boundary_detail": "The locality-driven spiral model is a finite TNE proxy model in which mass-bearing bodies deform an entropic-elastic locality field, and the resulting gravity-plus-elastic tension field feeds back into body motion. It is not a full astrophysical galaxy simulation and is not an empirical validation claim.",
    }
    write_metadata(metadata_path, metadata_payload)
    write_metadata(locality_metadata_path, metadata_payload)
    return {
        "figure": figure_path,
        "data": data_path,
        "metrics": metrics_path,
        "metadata": metadata_path,
        "locality_metrics": locality_metrics_path,
        "locality_metadata": locality_metadata_path,
        "passed_validation": metrics["nan_count"] == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate locality-driven spiral simulation artifacts.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--seed", type=int, default=2710)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, seed=args.seed, steps=args.steps, quick=args.quick)
    print(f"Generated locality-driven spiral artifacts in {Path(result['figure']).parent}")
    print(f"Scope: {CLAIM_BOUNDARY}")


if __name__ == "__main__":
    main()
