"""Generate a deterministic 3D TNE proxy animation of Hawking-like flux from entropic tension."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.black_hole_dynamics.animation.common import SCRIPT_DIR, build_black_hole_result, radial_field_grid, save_animation_bundle
from equations.black_hole_dynamics.black_hole_dynamics import hawking_like_flux, hawking_like_temperature, surface_gradient


def run(
    output_dir: str | Path | None = None,
    quick: bool = False,
    fps: int | None = None,
    preferred_format: str = "auto",
) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params, result = build_black_hole_result(quick=quick)
    fps_value = fps or (10 if quick else 16)
    frame_count = len(result["time"])
    threshold = float(params.threshold)
    resolution = 56 if quick else 72
    frames: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    z_min = float("inf")
    z_max = float("-inf")
    for time_value, pi_profile in zip(result["time"], result["pi_E_time"]):
        temperature_profile = hawking_like_temperature(surface_gradient(result["r"], pi_profile), params.K_D)
        flux_profile = hawking_like_flux(temperature_profile)
        xx, yy, flux_field = radial_field_grid(result["r"], flux_profile, resolution=resolution, extent=7.5)
        rr = np.sqrt(xx**2 + yy**2)
        pi_field = np.interp(np.clip(rr, result["r"].min(), result["r"].max()), result["r"], pi_profile)
        shell_radius = 1.0 + 4.0 * float(time_value)
        shell = np.exp(-((rr - shell_radius) ** 2) / (2.0 * 0.45**2))
        z_surface = np.log10(np.maximum(flux_field + shell * (np.max(flux_profile) + 1e-12), 1e-12))
        z_min = min(z_min, float(np.min(z_surface)))
        z_max = max(z_max, float(np.max(z_surface)))
        frames.append((xx, yy, z_surface, pi_field))

    fig = plt.figure(figsize=(7.4, 5.9), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int):
        ax.clear()
        xx, yy, z_surface, pi_field = frames[frame]
        stride = 2
        surface = ax.plot_surface(
            xx[::stride, ::stride],
            yy[::stride, ::stride],
            z_surface[::stride, ::stride],
            cmap="inferno",
            linewidth=0.0,
            antialiased=False,
            alpha=0.92,
        )
        ax.contour(xx, yy, pi_field, levels=[threshold], zdir="z", offset=z_min - 0.12, colors=["#8bd646"], linewidths=1.2)
        ax.set_title(f"Section 18: Hawking-like radiation proxy t={result['time'][frame]:.2f}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("log10 flux proxy")
        ax.set_zlim(z_min - 0.12, z_max + 0.04)
        ax.view_init(elev=31, azim=40 + 4 * frame)
        return surface

    update(0)
    return save_animation_bundle(
        fig=fig,
        update_func=update,
        frame_count=frame_count,
        root=root,
        stem="hawking_flux_from_entropic_tension_3d",
        data_payload={
            "time": result["time"],
            "r": result["r"],
            "pi_E_time": result["pi_E_time"],
            "flux_proxy": result["flux_proxy"],
            "horizon_radius": result["horizon_radius"],
        },
        metadata={
            "section": "18.13",
            "animation_name": "hawking_flux_from_entropic_tension_3d",
            "source_equation_module": "equations.black_hole_dynamics.black_hole_dynamics",
            "source_simulation_function": "simulate_black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
        },
        fps=fps_value,
        preferred_format=preferred_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 3D TNE proxy Hawking-flux animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format)
    print(f"Generated Hawking-flux 3D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
