"""Generate a deterministic 2D TNE locality-driven galaxy proxy animation."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from equations.animation_io import figure_to_frame, resolve_animation_writer, save_animation, save_frame_strip, save_gif_fallback, write_animation_metadata
from equations.artifact_io import CLAIM_BOUNDARY, ensure_dir, save_npz
from equations.locality_driven_gravity.locality_driven_gravity import BodyType, LocalityGravityParams, compute_spiral_metrics, simulate_locality_spiral


SCRIPT_DIR = Path(__file__).resolve().parent


def run(
    output_dir: str | Path | None = None,
    quick: bool = False,
    fps: int | None = None,
    preferred_format: str = "auto",
    seed: int = 2710,
) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = LocalityGravityParams(
        n_particles=96 if quick else 240,
        steps=48 if quick else 180,
        grid_size=28 if quick else 48,
        radial_scale=3.1,
        central_mass=200.0 if quick else 220.0,
    )
    result = simulate_locality_spiral(params=params, seed=seed)
    history = np.asarray(result["history"], dtype=float)
    density_history = np.asarray(result["density_history"], dtype=float)
    masses = np.asarray(result["masses"], dtype=float)
    body_types = np.asarray(result["body_types"], dtype=object)
    metrics = compute_spiral_metrics(
        history,
        velocity_history=result["velocity_history"],
        masses=masses,
        body_types=body_types,
        tension_field=result["tension_history"][-1],
    )
    frame_count = history.shape[0]
    fps_value = fps or (12 if quick else 18)
    bound = float(np.max(np.abs(history)) * 1.06)
    grid_axis = np.asarray(result["grid_axis"], dtype=float)
    xx, yy = np.meshgrid(grid_axis, grid_axis)

    fig, ax = plt.subplots(figsize=(7.0, 6.4), constrained_layout=True)
    current = history[0]
    center_mask = body_types == BodyType.CENTRAL_MASS.value
    stride = max(1, history.shape[1] // 18)
    trail_particles = history[:, 1::stride, :].transpose(1, 0, 2)
    image = ax.imshow(
        density_history[0],
        extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
        origin="lower",
        cmap="inferno",
        alpha=0.55,
        animated=False,
    )
    fig.colorbar(image, ax=ax, label="density proxy")

    def update(frame: int):
        positions = history[frame]
        density = density_history[frame]
        ax.clear()
        ax.imshow(
            density,
            extent=(grid_axis[0], grid_axis[-1], grid_axis[0], grid_axis[-1]),
            origin="lower",
            cmap="inferno",
            alpha=0.55,
        )
        ax.contour(xx, yy, density, levels=5, colors="white", linewidths=0.65, alpha=0.55)
        ax.scatter(
            positions[:, 0],
            positions[:, 1],
            s=10 + 10 * masses / (np.max(masses) + 1e-12),
            c=np.linalg.norm(positions, axis=1),
            cmap="viridis",
            alpha=0.9,
        )
        ax.scatter(positions[center_mask, 0], positions[center_mask, 1], s=150, c="#ffe08a", marker="*", edgecolors="black")
        for particle in trail_particles:
            start = max(0, frame - 20)
            segment = particle[start : frame + 1]
            ax.plot(segment[:, 0], segment[:, 1], linewidth=0.75, alpha=0.26, color="#d9d9d9")
        ax.set_title(f"TNE locality-driven galaxy proxy  t={frame / max(1, frame_count - 1):.2f}")
        ax.text(
            0.02,
            0.04,
            f"spiral={metrics['spiral_order_parameter']:.3f}\n"
            f"m2={metrics['mode_2_amplitude']:.3f}  m3={metrics['mode_3_amplitude']:.3f}\n"
            f"pitch={metrics['pitch_angle_proxy']:.3f}  contrast={metrics['density_arm_contrast']:.3f}",
            transform=ax.transAxes,
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.82, "edgecolor": "none"},
        )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_xlim(-bound, bound)
        ax.set_ylim(-bound, bound)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.18)
        return ax

    ensure_dir(root)
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=frame_count,
        interval=max(1, int(round(1000 / fps_value))),
        blit=False,
    )
    mp4_path = root / "spiral_galaxy_formation_2d.mp4"
    gif_path = root / "spiral_galaxy_formation_2d.gif"
    strip_path = root / "spiral_galaxy_formation_2d_frame_strip.png"
    data_path = root / "spiral_galaxy_formation_2d_data.npz"
    metadata_path = root / "spiral_galaxy_formation_2d_metadata.json"

    if preferred_format == "mp4":
        prefer_mode = "mp4"
    elif preferred_format == "gif":
        prefer_mode = "gif"
    elif preferred_format == "frames":
        prefer_mode = "frame_strip"
    else:
        prefer_mode, _ = resolve_animation_writer(prefer_mp4=True)
    animation_path: Path | None = None
    fallback_mode = "frame_strip"
    if prefer_mode == "mp4":
        try:
            animation_path = save_animation(anim, mp4_path, fps=fps_value, dpi=155)
            fallback_mode = "mp4"
        except Exception:
            animation_path = None
    if animation_path is None and prefer_mode in {"mp4", "gif", "auto"}:
        try:
            animation_path = save_gif_fallback(anim, gif_path, fps=max(8, fps_value // 2))
            fallback_mode = "gif"
        except Exception:
            animation_path = None

    frame_indices = np.linspace(0, frame_count - 1, num=min(6, frame_count), dtype=int)
    strip_frames: list[np.ndarray] = []
    for frame_index in frame_indices:
        update(int(frame_index))
        strip_frames.append(figure_to_frame(fig))
    save_frame_strip(strip_frames, strip_path)
    save_npz(
        data_path,
        history=history,
        density_history=density_history,
        tension_history=result["tension_history"],
        positions=result["positions"],
        velocities=result["velocities"],
        masses=masses,
        body_types=body_types,
        grid_axis=result["grid_axis"],
    )
    write_animation_metadata(
        metadata_path,
        {
            "claim_boundary": CLAIM_BOUNDARY,
            "section": "16.4",
            "animation_name": "spiral_galaxy_formation_2d",
            "source_equation_module": "equations.locality_driven_gravity.entropic_elastic_spiral",
            "source_simulation_function": "simulate_locality_spiral",
            "parameters": params.__dict__,
            "random_seed": seed,
            "output_files": [path.name for path in [p for p in [animation_path, strip_path, data_path] if p is not None]],
            "frame_count": frame_count,
            "fps": fps_value,
            "fallback_mode": fallback_mode,
            "metrics": metrics,
            "claim_boundary_detail": "The locality-driven spiral model is a finite TNE proxy model in which mass-bearing bodies deform an entropic-elastic locality field, and the resulting gravity-plus-elastic tension field feeds back into body motion. It is not a full astrophysical galaxy simulation and is not an empirical validation claim.",
        },
    )
    plt.close(fig)
    return {
        "animation": animation_path or strip_path,
        "frame_strip": strip_path,
        "data": data_path,
        "metadata": metadata_path,
        "fallback_mode": fallback_mode,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 2D TNE locality-driven galaxy proxy animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    parser.add_argument("--seed", type=int, default=2710)
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format, seed=args.seed)
    print(f"Generated spiral-galaxy 2D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
