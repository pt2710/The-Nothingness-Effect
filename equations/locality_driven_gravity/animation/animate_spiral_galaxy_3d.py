"""Generate a deterministic 3D TNE proxy animation of spiral-like galaxy formation."""

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


def _density_surface(positions: np.ndarray, bound: float, bins: int = 40) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    hist, xedges, yedges = np.histogram2d(positions[:, 0], positions[:, 1], bins=bins, range=[[-bound, bound], [-bound, bound]])
    xc = 0.5 * (xedges[:-1] + xedges[1:])
    yc = 0.5 * (yedges[:-1] + yedges[1:])
    xx, yy = np.meshgrid(xc, yc)
    return xx, yy, hist.T


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
        steps=55 if quick else 180,
        shear=0.18,
        damping=0.995,
    )
    result = simulate_locality_spiral(params=params, seed=seed)
    history = result["history"]
    metrics = compute_spiral_metrics(history)
    frame_count = history.shape[0]
    fps_value = fps or (10 if quick else 16)
    bound = float(np.max(np.abs(history)) * 1.08)
    bins = 28 if quick else 36

    fig = plt.figure(figsize=(7.6, 5.9), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int):
        ax.clear()
        positions = history[frame]
        xx, yy, density = _density_surface(positions, bound, bins=bins)
        stride = 2
        surface = ax.plot_surface(
            xx[::stride, ::stride],
            yy[::stride, ::stride],
            density[::stride, ::stride],
            cmap="magma",
            linewidth=0.0,
            antialiased=False,
            alpha=0.7,
        )
        radius = np.linalg.norm(positions, axis=1)
        ax.scatter(positions[:, 0], positions[:, 1], radius * 0.12, c=radius, cmap="viridis", s=8, alpha=0.9)
        ax.set_title(
            f"Section 16.4: locality-driven spiral formation toy model t={frame / max(1, frame_count - 1):.2f}\n"
            f"spiral diagnostic={metrics['spiral_order_parameter']:.3f}"
        )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("density / radius proxy")
        ax.set_xlim(-bound, bound)
        ax.set_ylim(-bound, bound)
        ax.set_zlim(0.0, float(np.max(density) + 0.5))
        ax.view_init(elev=30, azim=42 + 3 * frame)
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
    mp4_path = root / "spiral_galaxy_formation_3d.mp4"
    gif_path = root / "spiral_galaxy_formation_3d.gif"
    strip_path = root / "spiral_galaxy_formation_3d_frame_strip.png"
    data_path = root / "spiral_galaxy_formation_3d_data.npz"
    metadata_path = root / "spiral_galaxy_formation_3d_metadata.json"

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
            "animation_name": "spiral_galaxy_formation_3d",
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
    parser = argparse.ArgumentParser(description="Generate a 3D TNE proxy spiral-galaxy animation.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--format", choices=["auto", "mp4", "gif", "frames"], default="auto")
    parser.add_argument("--seed", type=int, default=2710)
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, quick=args.quick, fps=args.fps, preferred_format=args.format, seed=args.seed)
    print(f"Generated spiral-galaxy 3D artifacts in {Path(result['data']).parent}")


if __name__ == "__main__":
    main()
