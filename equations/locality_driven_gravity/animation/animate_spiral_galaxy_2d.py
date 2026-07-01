"""Generate a deterministic 2D TNE proxy animation of spiral-like formation."""

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
from equations.locality_driven_gravity.locality_driven_gravity import LocalityGravityParams, compute_spiral_metrics, simulate_locality_spiral


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
        n_particles=120 if quick else 280,
        steps=60 if quick else 180,
        shear=0.18,
        damping=0.995,
    )
    result = simulate_locality_spiral(params=params, seed=seed)
    history = result["history"]
    metrics = compute_spiral_metrics(history)
    frame_count = history.shape[0]
    fps_value = fps or (12 if quick else 18)
    bound = float(np.max(np.abs(history)) * 1.08)

    fig, ax = plt.subplots(figsize=(6.6, 6.0), constrained_layout=True)
    current = history[0]
    scatter = ax.scatter(
        current[:, 0],
        current[:, 1],
        s=9,
        c=np.linalg.norm(current, axis=1),
        cmap="magma",
        alpha=0.9,
    )
    stride = max(1, history.shape[1] // 14)
    trail_particles = history[:, ::stride, :].transpose(1, 0, 2)
    trails = [ax.plot([], [], linewidth=0.65, alpha=0.28, color="#7f7f7f")[0] for _ in range(trail_particles.shape[0])]
    title = ax.set_title("Section 16.4: TNE proxy spiral-like formation")
    metric_text = ax.text(
        0.03,
        0.05,
        f"spiral diagnostic={metrics['spiral_order_parameter']:.3f}",
        transform=ax.transAxes,
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(-bound, bound)
    ax.set_ylim(-bound, bound)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.2)
    fig.colorbar(scatter, ax=ax, label="radius")

    def update(frame: int):
        positions = history[frame]
        scatter.set_offsets(positions)
        scatter.set_array(np.linalg.norm(positions, axis=1))
        for trail, particle in zip(trails, trail_particles):
            start = max(0, frame - 18)
            segment = particle[start : frame + 1]
            trail.set_data(segment[:, 0], segment[:, 1])
        title.set_text(f"Section 16.4: TNE proxy spiral-like formation t={frame / max(1, frame_count - 1):.2f}")
        return scatter

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
    save_npz(data_path, history=history, positions=result["positions"], velocities=result["velocities"])
    write_animation_metadata(
        metadata_path,
        {
            "claim_boundary": CLAIM_BOUNDARY,
            "section": "16.4",
            "animation_name": "spiral_galaxy_formation_2d",
            "source_equation_module": "equations.locality_driven_gravity.locality_driven_gravity",
            "source_simulation_function": "simulate_locality_spiral",
            "parameters": params.__dict__,
            "random_seed": seed,
            "output_files": [path.name for path in [p for p in [animation_path, strip_path, data_path] if p is not None]],
            "frame_count": frame_count,
            "fps": fps_value,
            "fallback_mode": fallback_mode,
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
    parser = argparse.ArgumentParser(description="Generate a 2D TNE proxy spiral-galaxy animation.")
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
