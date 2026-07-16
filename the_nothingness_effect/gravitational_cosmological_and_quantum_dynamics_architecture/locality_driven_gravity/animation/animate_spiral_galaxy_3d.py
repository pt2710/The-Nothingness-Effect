"""Generate a deterministic 3D TNE locality-driven galaxy proxy animation."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from the_nothingness_effect._runtime.artifacts.animation_io import figure_to_frame, resolve_animation_writer, save_animation, save_frame_strip, save_gif_fallback, write_animation_metadata
from the_nothingness_effect._runtime.artifacts.io import CLAIM_BOUNDARY, ensure_dir, save_npz
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.locality_driven_gravity import BodyType, LocalityGravityParams, compute_spiral_metrics, simulate_spiral_arm_mode


SCRIPT_DIR = Path(__file__).resolve().parent


def run(
    output_dir: str | Path | None = None,
    quick: bool = False,
    fps: int | None = None,
    preferred_format: str = "auto",
    seed: int = 2710,
    arm_mode: int | str = 2,
) -> dict[str, object]:
    root = Path(output_dir) if output_dir is not None else SCRIPT_DIR / "artifacts"
    params = LocalityGravityParams(
        n_particles=96 if quick else 240,
        steps=42 if quick else 160,
        grid_size=26 if quick else 42,
        radial_scale=3.1,
        central_mass=200.0 if quick else 220.0,
        arm_mode=arm_mode,  # type: ignore[arg-type]
    )
    result = simulate_spiral_arm_mode(arm_mode, params=params, seed=seed, quick=False)
    history = np.asarray(result["history"], dtype=float)
    density_history = np.asarray(result["density_history"], dtype=float)
    tension_history = np.asarray(result["tension_history"], dtype=float)
    masses = np.asarray(result["masses"], dtype=float)
    body_types = np.asarray(result["body_types"], dtype=object)
    metrics = compute_spiral_metrics(
        history,
        velocity_history=result["velocity_history"],
        masses=masses,
        body_types=body_types,
        tension_field=tension_history[-1],
        arm_mode=arm_mode,
    )
    frame_count = history.shape[0]
    fps_value = fps or (10 if quick else 16)
    bound = float(np.max(np.abs(history)) * 1.08)
    grid_axis = np.asarray(result["grid_axis"], dtype=float)
    xx, yy = np.meshgrid(grid_axis, grid_axis)
    center_mask = body_types == BodyType.CENTRAL_MASS.value

    fig = plt.figure(figsize=(8.0, 6.2), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int):
        ax.clear()
        positions = history[frame]
        density = density_history[frame]
        tension = tension_history[frame]
        surface = ax.plot_surface(
            xx,
            yy,
            tension,
            cmap="cividis",
            linewidth=0.0,
            antialiased=False,
            alpha=0.82,
        )
        ax.contour(xx, yy, density, levels=6, zdir="z", offset=0.0, colors="white", linewidths=0.6)
        z_particles = np.clip(0.18 * np.interp(np.linalg.norm(positions, axis=1), [0.0, max(bound, 1e-12)], [0.0, 1.0]) + 0.55 * np.max(tension) * 0.15, 0.0, 1.2)
        ax.scatter(positions[:, 0], positions[:, 1], z_particles, c=np.linalg.norm(positions, axis=1), cmap="magma", s=8 + 12 * masses / (np.max(masses) + 1e-12), alpha=0.9)
        ax.scatter(positions[center_mask, 0], positions[center_mask, 1], np.full(np.count_nonzero(center_mask), np.max(tension) * 0.95), c="#ffe08a", s=140, marker="*", edgecolors="black")
        ax.set_title(
            f"TNE locality-driven galaxy proxy  arm_mode={arm_mode}  t={frame / max(1, frame_count - 1):.2f}\n"
            f"spiral={metrics['spiral_order_parameter']:.3f}  contrast={metrics['density_arm_contrast']:.3f}"
        )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("tension / density proxy")
        ax.set_xlim(-bound, bound)
        ax.set_ylim(-bound, bound)
        ax.set_zlim(0.0, max(1.1, float(np.max(tension)) * 1.08))
        ax.view_init(elev=33, azim=38)
        return surface

    update(0)
    ensure_dir(root)
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=frame_count,
        interval=max(1, int(round(1000 / fps_value))),
        blit=False,
    )
    mode_suffix = f"_arm_mode_{arm_mode}"
    base_name = f"spiral_galaxy_formation_3d{mode_suffix}"
    mp4_path = root / f"{base_name}.mp4"
    gif_path = root / f"{base_name}.gif"
    strip_path = root / f"{base_name}_frame_strip.png"
    data_path = root / f"{base_name}_data.npz"
    metadata_path = root / f"{base_name}_metadata.json"
    default_mp4_path = root / "spiral_galaxy_formation_3d.mp4"
    default_gif_path = root / "spiral_galaxy_formation_3d.gif"
    default_strip_path = root / "spiral_galaxy_formation_3d_frame_strip.png"
    default_data_path = root / "spiral_galaxy_formation_3d_data.npz"
    default_metadata_path = root / "spiral_galaxy_formation_3d_metadata.json"

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
            animation_path = save_animation(anim, mp4_path, fps=fps_value, dpi=150)
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
        tension_history=tension_history,
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
            "animation_name": "spiral_galaxy_formation_3d",
            "source_equation_module": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.entropic_elastic_spiral",
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
    parser = argparse.ArgumentParser(description="Generate a 3D TNE locality-driven galaxy proxy animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    parser.add_argument("--seed", type=int, default=2710)
    parser.add_argument("--arm-mode", choices=["2", "3", "4", "mixed"], default="2")
    args = parser.parse_args()
    arm_mode: int | str = args.arm_mode if args.arm_mode == "mixed" else int(args.arm_mode)
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format, seed=args.seed, arm_mode=arm_mode)
    print(f"Generated spiral-galaxy 3D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
