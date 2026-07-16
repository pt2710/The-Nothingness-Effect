"""Generate a deterministic 2D TNE proxy animation of Hawking-like flux."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.animation.common import SCRIPT_DIR, build_black_hole_result, radial_field_grid, save_animation_bundle
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics import hawking_like_flux, hawking_like_temperature, surface_gradient


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
    resolution = 96 if quick else 132
    fields: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    for time_value, pi_profile in zip(result["time"], result["pi_E_time"]):
        temperature_profile = hawking_like_temperature(surface_gradient(result["r"], pi_profile), params.K_D)
        flux_profile = hawking_like_flux(temperature_profile)
        xx, yy, base_field = radial_field_grid(result["r"], flux_profile, resolution=resolution)
        rr = np.sqrt(xx**2 + yy**2)
        shell_radius = 1.0 + 4.0 * float(time_value)
        shell = np.exp(-((rr - shell_radius) ** 2) / (2.0 * 0.45**2))
        pi_field = np.interp(np.clip(rr, result["r"].min(), result["r"].max()), result["r"], pi_profile)
        flux_field = base_field + shell * (0.35 + pi_field) * float(np.max(flux_profile) + 1e-12)
        fields.append((xx, yy, flux_field, pi_field))
    vmax = float(max(field.max() for _, _, field, _ in fields))
    vmin = np.log10(max(vmax, 1e-12)) - 4.0

    fig, ax = plt.subplots(figsize=(6.8, 5.8), constrained_layout=True)
    xx0, yy0, flux0, pi0 = fields[0]
    image = ax.imshow(
        np.log10(np.maximum(flux0, 1e-12)),
        origin="lower",
        extent=[float(xx0.min()), float(xx0.max()), float(yy0.min()), float(yy0.max())],
        cmap="inferno",
        vmin=vmin,
        vmax=np.log10(max(vmax, 1e-12)),
    )
    contour_state = {"contour": ax.contour(xx0, yy0, pi0, levels=[threshold], colors=["#8bd646"], linewidths=1.2)}
    title = ax.set_title(f"Section 18: TNE proxy Hawking-like flux t={result['time'][0]:.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.colorbar(image, ax=ax, label="log10 flux intensity")

    def update(frame: int):
        xx, yy, flux_field, pi_field = fields[frame]
        image.set_data(np.log10(np.maximum(flux_field, 1e-12)))
        contour_state["contour"].remove()
        contour_state["contour"] = ax.contour(xx, yy, pi_field, levels=[threshold], colors=["#8bd646"], linewidths=1.2)
        title.set_text(f"Section 18: TNE proxy Hawking-like flux t={result['time'][frame]:.2f}")
        return image

    return save_animation_bundle(
        fig=fig,
        update_func=update,
        frame_count=frame_count,
        root=root,
        stem="hawking_like_flux_2d",
        data_payload={
            "time": result["time"],
            "r": result["r"],
            "pi_E_time": result["pi_E_time"],
            "flux_proxy": result["flux_proxy"],
            "horizon_radius": result["horizon_radius"],
        },
        metadata={
            "section": "18.13",
            "animation_name": "hawking_like_flux_2d",
            "source_equation_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.black_hole_dynamics",
            "source_simulation_function": "simulate_black_hole_dynamics",
            "parameters": params.__dict__,
            "random_seed": None,
        },
        fps=fps_value,
        preferred_format=preferred_format,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 2D TNE proxy Hawking-like flux animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format)
    print(f"Generated Hawking-like flux 2D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
