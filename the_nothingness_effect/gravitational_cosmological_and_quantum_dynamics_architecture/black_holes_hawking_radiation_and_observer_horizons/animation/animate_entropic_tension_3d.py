"""Generate a deterministic 3D TNE proxy animation of entropic spacetime tension."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.common import SCRIPT_DIR, build_black_hole_result, radial_field_grid, save_animation_bundle
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics import entropy_profile_radial, surface_gradient


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
    surfaces: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    z_min = float("inf")
    z_max = float("-inf")
    for time_value, pi_profile in zip(result["time"], result["pi_E_time"]):
        mass_t = params.mass_proxy * (1.0 - 0.08 * float(time_value))
        entropy = entropy_profile_radial(result["r"], mass_t, params.entropy_scale, params.width)
        gradient = np.abs(surface_gradient(result["r"], entropy))
        tension_profile = gradient * (1.0 - pi_profile)
        tension_profile = tension_profile - np.min(tension_profile)
        tension_profile = tension_profile / (np.max(tension_profile) + 1e-12)
        xx, yy, tension_field = radial_field_grid(result["r"], tension_profile, resolution=resolution, extent=7.5)
        rr = np.sqrt(xx**2 + yy**2)
        pi_field = np.interp(np.clip(rr, result["r"].min(), result["r"].max()), result["r"], pi_profile)
        z_surface = -tension_field
        z_min = min(z_min, float(np.min(z_surface)))
        z_max = max(z_max, float(np.max(z_surface)))
        surfaces.append((xx, yy, z_surface, pi_field))

    fig = plt.figure(figsize=(7.4, 5.9), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int):
        ax.clear()
        xx, yy, z_surface, pi_field = surfaces[frame]
        stride = 2
        surface = ax.plot_surface(
            xx[::stride, ::stride],
            yy[::stride, ::stride],
            z_surface[::stride, ::stride],
            cmap="viridis",
            linewidth=0.0,
            antialiased=False,
            alpha=0.95,
        )
        level = float(np.nanmean(z_surface))
        ax.contour(xx, yy, pi_field, levels=[threshold], zdir="z", offset=level - 0.08, colors=["#f58518"], linewidths=1.3)
        ax.set_title(f"Section 18: entropic spacetime-tension field t={result['time'][frame]:.2f}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("tension proxy")
        ax.set_zlim(z_min - 0.08, z_max + 0.04)
        ax.view_init(elev=30, azim=34 + 4 * frame)
        return surface

    update(0)
    return save_animation_bundle(
        fig=fig,
        update_func=update,
        frame_count=frame_count,
        root=root,
        stem="entropic_tension_3d",
        data_payload={
            "time": result["time"],
            "r": result["r"],
            "pi_E_time": result["pi_E_time"],
            "horizon_radius": result["horizon_radius"],
        },
        metadata={
            "section": "18.6",
            "animation_name": "entropic_tension_3d",
            "source_equation_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics",
            "source_simulation_function": "simulate_black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
        },
        fps=fps_value,
        preferred_format=preferred_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 3D TNE proxy entropic-tension animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format)
    print(f"Generated entropic tension 3D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
