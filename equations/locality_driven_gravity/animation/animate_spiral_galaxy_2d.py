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
from equations.locality_driven_gravity.locality_driven_gravity import BodyType, LocalityGravityParams, compute_spiral_metrics, simulate_spiral_arm_mode


SCRIPT_DIR = Path(__file__).resolve().parent


def run(
    output_dir: str | Path | None = None,
    quick: bool = False,
    fps: int | None = None,
    preferred_format: str = "auto",
    seed: int = 2710,
    arm_mode: int | str = 2,
) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR
    params = LocalityGravityParams(
        n_particles=96 if quick else 240,
        steps=48 if quick else 180,
        grid_size=28 if quick else 48,
        radial_scale=3.1,
        central_mass=200.0 if quick else 220.0,
        arm_mode=arm_mode,  # type: ignore[arg-type]
    )
    result = simulate_spiral_arm_mode(arm_mode, params=params, seed=seed, quick=False)
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
        arm_mode=arm_mode,
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
        ax.set_title(f"TNE locality-driven galaxy proxy  arm_mode={arm_mode}  t={frame / max(1, frame_count - 1):.2f}")
        ax.text(
            0.02,
            0.04,
            f"spiral={metrics['spiral_order_parameter']:.3f}\n"
            f"m2={metrics['mode_2_amplitude']:.3f}  m3={metrics['mode_3_amplitude']:.3f}  m4={metrics['mode_4_amplitude']:.3f}\n"
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
    mode_suffix = f"_arm_mode_{arm_mode}"
    base_name = f"spiral_galaxy_formation_2d{mode_suffix}"
    mp4_path = root / f"{base_name}.mp4"
    gif_path = root / f"{base_name}.gif"
    strip_path = root / f"{base_name}_frame_strip.png"
    data_path = root / f"{base_name}_data.npz"
    metadata_path = root / f"{base_name}_metadata.json"
    default_mp4_path = root / "spiral_galaxy_formation_2d.mp4"
    default_gif_path = root / "spiral_galaxy_formation_2d.gif"
    default_strip_path = root / "spiral_galaxy_formation_2d_frame_strip.png"
    default_data_path = root / "spiral_galaxy_formation_2d_data.npz"
    default_metadata_path = root / "spiral_galaxy_formation_2d_metadata.json"

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
        arm_mode_assignment=result["arm_mode_assignment"],
        arm_phase_offsets=result["arm_phase_offsets"],
    )
    write_animation_metadata(
        metadata_path,
        {
            "claim_boundary": CLAIM_BOUNDARY,
            "section": "16.4",
            "animation_name": "spiral_galaxy_formation_2d",
            "source_equation_module": "equations.locality_driven_gravity.entropic_elastic_spiral",
            "source_simulation_function": "simulate_spiral_arm_mode",
            "parameters": params.__dict__,
            "arm_mode": arm_mode,
            "random_seed": seed,
            "output_files": [path.name for path in [p for p in [animation_path, strip_path, data_path] if p is not None]],
            "frame_count": frame_count,
            "fps": fps_value,
            "fallback_mode": fallback_mode,
            "metrics": metrics,
            "claim_boundary_detail": "TNE locality-driven galaxy proxy with controlled arm-mode initialization. Not a full astrophysical simulation, not an empirical validation claim, and not a formal proof substitute.",
        },
    )
    if str(arm_mode) == "2":
        if animation_path is not None and animation_path.suffix == ".mp4":
            default_mp4_path.write_bytes(mp4_path.read_bytes())
        elif animation_path is not None and animation_path.suffix == ".gif":
            default_gif_path.write_bytes(gif_path.read_bytes())
        default_strip_path.write_bytes(strip_path.read_bytes())
        default_data_path.write_bytes(data_path.read_bytes())
        default_metadata_path.write_text(metadata_path.read_text(encoding="utf-8"), encoding="utf-8")
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
    parser.add_argument("--arm-mode", choices=["2", "3", "4", "mixed"], default="2")
    args = parser.parse_args()
    arm_mode: int | str = args.arm_mode if args.arm_mode == "mixed" else int(args.arm_mode)
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format, seed=args.seed, arm_mode=arm_mode)
    print(f"Generated spiral-galaxy 2D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
