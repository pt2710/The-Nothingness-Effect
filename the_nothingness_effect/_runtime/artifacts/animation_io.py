"""Shared helpers for deterministic animation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from the_nothingness_effect._runtime.artifacts.io import ensure_dir, save_json


def resolve_animation_writer(prefer_mp4: bool = True) -> tuple[str, type[Any] | None]:
    candidates: list[tuple[str, str]] = []
    if prefer_mp4:
        candidates.extend([("mp4", "FFMpegWriter"), ("mp4", "FFMpegFileWriter")])
    candidates.append(("gif", "PillowWriter"))
    for mode, writer_name in candidates:
        writer_cls = getattr(animation, writer_name, None)
        if writer_cls is None:
            continue
        try:
            if writer_cls.isAvailable():
                return mode, writer_cls
        except Exception:
            continue
    return "frame_strip", None


def save_animation(anim: animation.FuncAnimation, path: str | Path, fps: int = 24, dpi: int = 150) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    prefer_mp4 = output_path.suffix.lower() == ".mp4"
    _, writer_cls = resolve_animation_writer(prefer_mp4=prefer_mp4)
    if writer_cls is None:
        raise RuntimeError("No MP4-capable animation writer available.")
    anim.save(output_path, writer=writer_cls(fps=fps), dpi=dpi)
    return output_path


def save_gif_fallback(anim: animation.FuncAnimation, path: str | Path, fps: int = 12) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    writer_cls = getattr(animation, "PillowWriter", None)
    if writer_cls is None or not writer_cls.isAvailable():
        raise RuntimeError("No GIF-capable animation writer available.")
    anim.save(output_path, writer=writer_cls(fps=fps))
    return output_path


def save_frame_strip(frames: Iterable[np.ndarray], path: str | Path) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    frame_list = [np.asarray(frame, dtype=np.uint8) for frame in frames]
    if not frame_list:
        raise ValueError("At least one frame is required for frame-strip output.")
    height = max(frame.shape[0] for frame in frame_list)
    width = max(frame.shape[1] for frame in frame_list)
    rgba_frames = []
    for frame in frame_list:
        if frame.ndim != 3:
            raise ValueError("Each frame must be an RGB or RGBA image.")
        channels = frame.shape[2]
        if channels == 3:
            alpha = np.full((frame.shape[0], frame.shape[1], 1), 255, dtype=np.uint8)
            frame = np.concatenate([frame, alpha], axis=2)
        canvas = np.full((height, width, 4), 255, dtype=np.uint8)
        canvas[: frame.shape[0], : frame.shape[1], :] = frame
        rgba_frames.append(canvas)
    strip = np.concatenate(rgba_frames, axis=1)
    plt.imsave(output_path, strip)
    return output_path


def save_frame_pngs(
    fig_generator: Callable[[int], Any],
    output_dir: str | Path,
    frame_count: int,
) -> list[Path]:
    directory = ensure_dir(output_dir)
    outputs: list[Path] = []
    for frame in range(frame_count):
        produced = fig_generator(frame)
        fig = produced[0] if isinstance(produced, tuple) else produced
        output_path = directory / f"frame_{frame:04d}.png"
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        outputs.append(output_path)
    return outputs


def write_animation_metadata(path: str | Path, metadata: dict[str, Any]) -> Path:
    return save_json(path, metadata)


def figure_to_frame(fig: Any) -> np.ndarray:
    fig.canvas.draw()
    return np.asarray(fig.canvas.buffer_rgba()).copy()
