"""Generate a deterministic 2D TNE proxy animation of observer horizon memory."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.common import SCRIPT_DIR, build_black_hole_result, radial_field_grid, save_animation_bundle


def run(
    output_dir: str | Path | None = None,
    quick: bool = False,
    fps: int | None = None,
    preferred_format: str = "auto",
) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR / "artifacts"
    params, result = build_black_hole_result(quick=quick)
    frame_count = len(result["time"])
    fps_value = fps or (12 if quick else 18)
    threshold = float(params.threshold)
    fields = [radial_field_grid(result["r"], profile, resolution=96 if quick else 132) for profile in result["pi_E_time"]]
    vmin = float(min(field.min() for _, _, field in fields))
    vmax = float(max(field.max() for _, _, field in fields))
    memory_scale = float(np.max(np.abs(result["memory"])) + 1e-12)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.9), constrained_layout=True)
    xx0, yy0, field0 = fields[0]
    image = axes[0].imshow(
        field0,
        origin="lower",
        extent=[float(xx0.min()), float(xx0.max()), float(yy0.min()), float(yy0.max())],
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
    )
    contour_state = {"contour": axes[0].contour(xx0, yy0, field0, levels=[threshold], colors=["#f58518"], linewidths=1.4)}
    observer_marker = axes[0].scatter([result["observer_path"][0]], [0.0], color="#e45756", s=40)
    axes[0].set_title("Observer and horizon proxy field")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    distance_text = axes[0].text(
        0.03,
        0.05,
        f"distance={result['observer_distance'][0]:.2f}",
        transform=axes[0].transAxes,
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    memory_line = axes[1].plot(result["time"], result["memory"] / memory_scale, color="#4c78a8", linewidth=2, label="normalized memory proxy")[0]
    distance_line = axes[1].plot(
        result["time"],
        result["observer_distance"] / (np.max(result["observer_distance"]) + 1e-12),
        color="#54a24b",
        linewidth=1.5,
        label="normalized observer distance",
    )[0]
    time_cursor = axes[1].axvline(result["time"][0], color="#e45756", linestyle="--", linewidth=1.2)
    axes[1].set_title("Memory and distance trace")
    axes[1].set_xlabel("normalized time")
    axes[1].set_ylabel("normalized proxy value")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(loc="upper right")
    fig.colorbar(image, ax=axes[0], label="normalized π_E")

    def update(frame: int):
        xx, yy, field = fields[frame]
        image.set_data(field)
        contour_state["contour"].remove()
        contour_state["contour"] = axes[0].contour(xx, yy, field, levels=[threshold], colors=["#f58518"], linewidths=1.4)
        observer_marker.set_offsets(np.array([[result["observer_path"][frame], 0.0]]))
        distance_text.set_text(f"distance={result['observer_distance'][frame]:.2f}")
        time_cursor.set_xdata([result["time"][frame], result["time"][frame]])
        return image

    return save_animation_bundle(
        fig=fig,
        update_func=update,
        frame_count=frame_count,
        root=root,
        stem="observer_horizon_memory_2d",
        data_payload={
            "time": result["time"],
            "r": result["r"],
            "pi_E_time": result["pi_E_time"],
            "observer_path": result["observer_path"],
            "observer_distance": result["observer_distance"],
            "memory": result["memory"],
        },
        metadata={
            "section": "18.13",
            "animation_name": "observer_horizon_memory_2d",
            "source_equation_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics",
            "source_simulation_function": "simulate_black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
        },
        fps=fps_value,
        preferred_format=preferred_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 2D TNE proxy observer horizon memory animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format)
    print(f"Generated observer-horizon memory 2D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
