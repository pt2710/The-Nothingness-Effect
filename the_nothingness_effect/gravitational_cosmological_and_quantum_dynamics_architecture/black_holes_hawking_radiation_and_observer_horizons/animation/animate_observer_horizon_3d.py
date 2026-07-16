"""Generate a deterministic 3D TNE proxy animation of observer-horizon emergence."""

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
    fps_value = fps or (10 if quick else 16)
    frame_count = len(result["time"])
    threshold = float(params.threshold)
    resolution = 56 if quick else 72
    frames: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    z_min = float("inf")
    z_max = float("-inf")
    for pi_profile in result["pi_E_time"]:
        xx, yy, field = radial_field_grid(result["r"], pi_profile, resolution=resolution, extent=7.5)
        z_surface = field
        z_min = min(z_min, float(np.min(z_surface)))
        z_max = max(z_max, float(np.max(z_surface)))
        rr = np.sqrt(xx**2 + yy**2)
        frames.append((xx, yy, z_surface, rr))

    fig = plt.figure(figsize=(8.1, 5.8), constrained_layout=True)
    ax_surface = fig.add_subplot(121, projection="3d")
    ax_trace = fig.add_subplot(122)

    def update(frame: int):
        ax_surface.clear()
        ax_trace.clear()
        xx, yy, z_surface, rr = frames[frame]
        stride = 2
        surface = ax_surface.plot_surface(
            xx[::stride, ::stride],
            yy[::stride, ::stride],
            z_surface[::stride, ::stride],
            cmap="cividis",
            linewidth=0.0,
            antialiased=False,
            alpha=0.92,
        )
        opacity = 0.2 + 0.8 * (result["memory"][frame] / (np.max(result["memory"]) + 1e-12))
        ax_surface.contour(xx, yy, z_surface, levels=[threshold], zdir="z", offset=z_min - 0.05, colors=[(0.96, 0.54, 0.10, opacity)], linewidths=1.5)
        observer_x = float(result["observer_path"][frame])
        observer_z = float(np.interp(abs(observer_x), result["r"], result["pi_E_time"][frame]))
        ax_surface.scatter([observer_x], [0.0], [observer_z], color="#e45756", s=45)
        ax_surface.set_title(f"Observer-horizon emergence proxy t={result['time'][frame]:.2f}")
        ax_surface.set_xlabel("x")
        ax_surface.set_ylabel("y")
        ax_surface.set_zlabel("π_E")
        ax_surface.set_zlim(z_min - 0.05, z_max + 0.03)
        ax_surface.view_init(elev=28, azim=35 + 4 * frame)

        ax_trace.plot(result["time"], result["memory"], color="#4c78a8", linewidth=2, label="memory proxy")
        ax_trace.plot(result["time"], result["observer_distance"], color="#54a24b", linewidth=1.5, label="observer distance")
        ax_trace.axvline(result["time"][frame], color="#e45756", linestyle="--", linewidth=1.2)
        ax_trace.set_title("Memory and distance trace")
        ax_trace.set_xlabel("normalized time")
        ax_trace.set_ylabel("proxy value")
        ax_trace.grid(True, alpha=0.25)
        ax_trace.legend(loc="upper right")
        return surface

    update(0)
    return save_animation_bundle(
        fig=fig,
        update_func=update,
        frame_count=frame_count,
        root=root,
        stem="observer_horizon_appear_disappear_3d",
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
            "animation_name": "observer_horizon_appear_disappear_3d",
            "source_equation_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics",
            "source_simulation_function": "simulate_black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
        },
        fps=fps_value,
        preferred_format=preferred_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 3D TNE proxy observer-horizon animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format)
    print(f"Generated observer-horizon 3D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
