"""Shared black-hole animation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from equations.animation_io import figure_to_frame, resolve_animation_writer, save_animation, save_frame_strip, save_gif_fallback, write_animation_metadata
from equations.artifact_io import CLAIM_BOUNDARY, ensure_dir, save_npz
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, simulate_black_hole_dynamics


SCRIPT_DIR = Path(__file__).resolve().parent


def build_black_hole_result(quick: bool = False) -> tuple[BlackHoleParams, dict[str, np.ndarray]]:
    params = BlackHoleParams(grid_size=96 if quick else 180, steps=18 if quick else 54)
    return params, simulate_black_hole_dynamics(params)


def radial_field_grid(
    r_samples: np.ndarray,
    radial_values: np.ndarray,
    resolution: int = 128,
    extent: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    radius = np.asarray(r_samples, dtype=float)
    values = np.asarray(radial_values, dtype=float)
    bound = float(extent if extent is not None else radius.max())
    axis = np.linspace(-bound, bound, resolution)
    xx, yy = np.meshgrid(axis, axis)
    rr = np.sqrt(xx**2 + yy**2)
    field = np.interp(np.clip(rr, radius.min(), radius.max()), radius, values)
    return xx, yy, field


def save_animation_bundle(
    fig: Any,
    update_func: Callable[[int], Any],
    frame_count: int,
    root: Path,
    stem: str,
    data_payload: dict[str, Any],
    metadata: dict[str, Any],
    fps: int,
    preferred_format: str = "auto",
) -> dict[str, object]:
    ensure_dir(root)
    anim = animation.FuncAnimation(
        fig,
        update_func,
        frames=frame_count,
        interval=max(1, int(round(1000 / fps))),
        blit=False,
    )
    mp4_path = root / f"{stem}.mp4"
    gif_path = root / f"{stem}.gif"
    strip_path = root / f"{stem}_frame_strip.png"
    data_path = root / f"{stem}_data.npz"
    metadata_path = root / f"{stem}_metadata.json"

    if preferred_format == "mp4":
        prefer_mode = "mp4"
    elif preferred_format == "gif":
        prefer_mode = "gif"
    elif preferred_format == "frames":
        prefer_mode = "frame_strip"
    else:
        prefer_mode, _ = resolve_animation_writer(prefer_mp4=True)
    output_files: list[str] = []
    fallback_mode = "frame_strip"
    animation_path: Path | None = None
    if prefer_mode == "mp4":
        try:
            animation_path = save_animation(anim, mp4_path, fps=fps, dpi=150)
            fallback_mode = "mp4"
        except Exception:
            animation_path = None
    if animation_path is None and prefer_mode in {"mp4", "gif", "auto"}:
        try:
            animation_path = save_gif_fallback(anim, gif_path, fps=max(8, fps // 2))
            fallback_mode = "gif"
        except Exception:
            animation_path = None

    frame_indices = np.linspace(0, frame_count - 1, num=min(6, frame_count), dtype=int)
    strip_frames: list[np.ndarray] = []
    for frame_index in frame_indices:
        update_func(int(frame_index))
        strip_frames.append(figure_to_frame(fig))
    save_frame_strip(strip_frames, strip_path)
    output_files.append(strip_path.name)
    if animation_path is not None:
        output_files.insert(0, animation_path.name)
    save_npz(data_path, **data_payload)
    output_files.append(data_path.name)
    write_animation_metadata(
        metadata_path,
        {
            "claim_boundary": CLAIM_BOUNDARY,
            "frame_count": frame_count,
            "fps": fps,
            "fallback_mode": fallback_mode,
            "output_files": output_files,
            **metadata,
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
