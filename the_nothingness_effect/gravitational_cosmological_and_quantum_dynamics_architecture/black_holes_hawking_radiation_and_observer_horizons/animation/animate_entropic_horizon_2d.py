"""Generate a deterministic 2D TNE proxy animation of entropic horizon crossing."""

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
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params, result = build_black_hole_result(quick=quick)
    frame_count = len(result["time"])
    fps_value = fps or (12 if quick else 18)
    threshold = float(params.threshold)
    fields = [radial_field_grid(result["r"], profile, resolution=96 if quick else 140) for profile in result["pi_E_time"]]
    vmin = float(min(field.min() for _, _, field in fields))
    vmax = float(max(field.max() for _, _, field in fields))

    fig, ax = plt.subplots(figsize=(6.6, 5.6), constrained_layout=True)
    xx0, yy0, field0 = fields[0]
    image = ax.imshow(
        field0,
        origin="lower",
        extent=[float(xx0.min()), float(xx0.max()), float(yy0.min()), float(yy0.max())],
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
    )
    contour_state = {"contour": ax.contour(xx0, yy0, field0, levels=[threshold], colors=["#f58518"], linewidths=1.4)}
    horizon_circle = plt.Circle((0.0, 0.0), radius=0.0 if not np.isfinite(result["horizon_radius"][0]) else float(result["horizon_radius"][0]), fill=False, color="white", linestyle="--", linewidth=1.1)
    ax.add_patch(horizon_circle)
    title = ax.set_title(f"Section 18: TNE proxy horizon crossing t={result['time'][0]:.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.colorbar(image, ax=ax, label="normalized π_E")

    def update(frame: int):
        xx, yy, field = fields[frame]
        image.set_data(field)
        contour_state["contour"].remove()
        contour_state["contour"] = ax.contour(xx, yy, field, levels=[threshold], colors=["#f58518"], linewidths=1.4)
        radius = float(result["horizon_radius"][frame])
        horizon_circle.set_radius(0.0 if not np.isfinite(radius) else radius)
        title.set_text(f"Section 18: TNE proxy horizon crossing t={result['time'][frame]:.2f}")
        return image

    return save_animation_bundle(
        fig=fig,
        update_func=update,
        frame_count=frame_count,
        root=root,
        stem="entropic_horizon_crossing_2d",
        data_payload={
            "time": result["time"],
            "r": result["r"],
            "pi_E_time": result["pi_E_time"],
            "horizon_radius": result["horizon_radius"],
            "threshold": np.array([threshold], dtype=float),
        },
        metadata={
            "section": "18.6",
            "animation_name": "entropic_horizon_crossing_2d",
            "source_equation_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics",
            "source_simulation_function": "simulate_black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
        },
        fps=fps_value,
        preferred_format=preferred_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 2D TNE proxy entropic horizon animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format)
    print(f"Generated entropic horizon 2D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
