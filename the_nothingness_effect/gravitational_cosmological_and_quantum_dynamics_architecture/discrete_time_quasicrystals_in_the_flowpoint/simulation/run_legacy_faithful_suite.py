"""Materialize source-faithful DTQC visual and data artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

try:
    from ..spatial_elastic_pi import spatial_2d_diagnostics
except ImportError:  # pragma: no cover - direct local verification helper
    from spatial_elastic_pi import spatial_2d_diagnostics

try:
    from ..legacy_faithful_runtime import (
        CANONICAL_DUBLER_SOURCE,
        CLAIM_BOUNDARY,
        LEGACY_VISUAL_SOURCE,
        LegacyFaithfulConfig,
        LegacyFaithfulState,
        generate_legacy_faithful_state,
    )
except ImportError:  # pragma: no cover - direct local verification helper
    from legacy_faithful_runtime import (
        CANONICAL_DUBLER_SOURCE,
        CLAIM_BOUNDARY,
        LEGACY_VISUAL_SOURCE,
        LegacyFaithfulConfig,
        LegacyFaithfulState,
        generate_legacy_faithful_state,
    )


STATIC_FILES = (
    "dtqc_legacy_summary.png",
    "dtqc_legacy_quasicrystal_contour.png",
    "dtqc_legacy_diffraction_fft.png",
    "dtqc_legacy_dfi_surface.png",
    "dtqc_legacy_elastic_pi_surface.png",
    "dtqc_legacy_wavelet_ridges.png",
)
ANIMATED_FILES = (
    "dtqc_legacy_flowpoint_flicker.gif",
    "dtqc_legacy_5d_scatter.gif",
    "dtqc_legacy_elastic_pi_sphere.gif",
    "dtqc_legacy_elastic_pi_half_sphere.gif",
)
DATA_FILES = (
    "dtqc_legacy_metrics.csv",
    "dtqc_legacy_state.npz",
    "dtqc_legacy_source_removal.csv",
)
CHECKSUM_FILE = "dtqc_legacy_checksums.json"
MANIFEST_FILE = "dtqc_legacy_metadata.json"
EXPECTED_INVENTORY = (*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES, CHECKSUM_FILE, MANIFEST_FILE)


def _png_bytes(figure: plt.Figure) -> np.ndarray:
    figure.canvas.draw()
    width, height = figure.canvas.get_width_height()
    rgba = np.frombuffer(figure.canvas.buffer_rgba(), dtype=np.uint8).reshape(height, width, 4)
    return rgba[:, :, :3].copy()


def _save_summary(path: Path, state: LegacyFaithfulState) -> None:
    figure, axes = plt.subplots(2, 3, figsize=(12.0, 7.7), constrained_layout=True)
    panels = (
        (state.carrier, "ten-wave decagonal carrier", "plasma"),
        (state.diffraction, "legacy log-magnitude FFT", "inferno"),
        (state.dfi_surface, "legacy DFI outer-product surface", "coolwarm"),
        (state.entropy, "mean legacy entropy profile", "cividis"),
        (state.static_pattern, "legacy Elastic-pi-modulated field", "viridis"),
        (state.flowpoint_frames[1], "phase-evolving Flowpoint flicker", "plasma"),
    )
    for axis, (value, title, cmap) in zip(axes.flat, panels, strict=True):
        image = axis.imshow(value, origin="lower", cmap=cmap, aspect="auto")
        axis.set_title(title)
        axis.axis("off")
        figure.colorbar(image, ax=axis, shrink=0.74)
    figure.savefig(path, dpi=170)
    plt.close(figure)


def _save_contour(path: Path, state: LegacyFaithfulState) -> None:
    figure = plt.figure(figsize=(5.0, 5.0))
    axis = figure.add_subplot(111)
    axis.contour(state.x, state.y, state.static_pattern, 60, cmap="plasma")
    axis.set_axis_off()
    axis.set_aspect("equal")
    figure.savefig(path, dpi=240, bbox_inches="tight", pad_inches=0)
    plt.close(figure)


def _save_image(path: Path, value: np.ndarray, cmap: str, *, aspect: str = "equal") -> None:
    figure = plt.figure(figsize=(5.0, 5.0))
    axis = figure.add_subplot(111)
    axis.imshow(value, origin="lower", cmap=cmap, aspect=aspect)
    axis.set_axis_off()
    figure.savefig(path, dpi=240, bbox_inches="tight", pad_inches=0)
    plt.close(figure)


def _save_surface(path: Path, state: LegacyFaithfulState, value: np.ndarray, cmap: str) -> None:
    figure = plt.figure(figsize=(6.0, 5.0))
    axis = figure.add_subplot(111, projection="3d")
    axis.plot_surface(
        state.x,
        state.y,
        value,
        cmap=cmap,
        rcount=min(300, state.config.grid_size),
        ccount=min(300, state.config.grid_size),
        linewidth=0,
        antialiased=True,
    )
    axis.set_axis_off()
    figure.savefig(path, dpi=240, bbox_inches="tight", pad_inches=0)
    plt.close(figure)


def _save_dfi_surface(path: Path, state: LegacyFaithfulState) -> None:
    size = state.dfi_surface.shape[0]
    grid = np.arange(size)
    x_grid, y_grid = np.meshgrid(grid, grid, indexing="xy")
    figure = plt.figure(figsize=(6.0, 3.8))
    axis = figure.add_subplot(111, projection="3d")
    axis.plot_surface(
        x_grid,
        y_grid,
        state.dfi_surface,
        cmap="coolwarm",
        rcount=min(240, size),
        ccount=min(240, size),
        linewidth=0,
        antialiased=True,
    )
    axis.set_axis_off()
    figure.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0)
    plt.close(figure)


def _flowpoint_animation(path: Path, state: LegacyFaithfulState) -> None:
    images: list[np.ndarray] = []
    levels = np.linspace(-1.0, 1.0, 65) * np.ptp(state.carrier)
    for frame in state.flowpoint_frames:
        figure, axis = plt.subplots(figsize=(5.0, 5.0))
        axis.contour(state.x, state.y, frame, levels=levels, cmap="plasma")
        axis.set_axis_off()
        axis.set_aspect("equal")
        images.append(_png_bytes(figure))
        plt.close(figure)
    duration = (state.config.legacy_frame_stride / 24.0)
    imageio.mimsave(path, images, duration=duration, loop=0, subrectangles=True)


def _scatter_animation(path: Path, state: LegacyFaithfulState) -> None:
    images: list[np.ndarray] = []
    absolute_limit = max(38.0, float(np.quantile(np.abs(state.projection_3d), 0.999)))
    for points, colors in zip(
        state.projection_3d,
        state.scatter_trajectory_4d[:, :, 3],
        strict=True,
    ):
        figure = plt.figure(figsize=(8.0, 8.0))
        axis = figure.add_subplot(111, projection="3d")
        axis.scatter(
            points[:, 0],
            points[:, 1],
            points[:, 2],
            s=1.8,
            c=colors,
            cmap="Spectral",
            depthshade=True,
            alpha=0.85,
        )
        axis.set(
            xlim=(-absolute_limit, absolute_limit),
            ylim=(-absolute_limit, absolute_limit),
            zlim=(-absolute_limit, absolute_limit),
        )
        axis.set_axis_off()
        images.append(_png_bytes(figure))
        plt.close(figure)
    duration = state.config.legacy_frame_stride / 24.0
    imageio.mimsave(path, images, duration=duration, loop=0, subrectangles=True)


def _sphere_coordinates(texture: np.ndarray, sector: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    resolution = texture.shape[0]
    theta = np.linspace(0.0, math.pi, resolution)
    phi = np.linspace(0.0, 2.0 * math.pi, resolution)
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="xy")
    values = sector * texture
    radius = 1.0 + 0.25 * values / np.ptp(values)
    x = radius * np.sin(theta_grid) * np.cos(phi_grid)
    y = radius * np.sin(theta_grid) * np.sin(phi_grid)
    z = radius * np.cos(theta_grid)
    normalized = (values - values.min()) / np.ptp(values)
    return x, y, z, normalized, phi_grid >= math.pi


def _sphere_animation(path: Path, state: LegacyFaithfulState, *, half: bool) -> None:
    images: list[np.ndarray] = []
    # Keep the complete interval; large tracked suites sample every other rendered frame.
    sphere_step = 4 if state.config.time_steps >= 32 else (2 if state.config.time_steps >= 16 else 1)
    for index in range(0, state.config.time_steps, sphere_step):
        x, y, z, normalized, back_mask = _sphere_coordinates(
            state.sphere_texture,
            float(state.flowpoint_sector[index]),
        )
        figure = plt.figure(figsize=(7.0, 7.0))
        axis = figure.add_subplot(111, projection="3d")
        facecolors = plt.cm.plasma(normalized)
        if half:
            axis.plot_surface(
                np.where(back_mask, x, np.nan),
                np.where(back_mask, y, np.nan),
                np.where(back_mask, z, np.nan),
                facecolors=np.where(back_mask[..., None], facecolors, np.nan),
                linewidth=0,
                antialiased=False,
                shade=False,
            )
            axis.plot_wireframe(
                np.where(~back_mask, x, np.nan),
                np.where(~back_mask, y, np.nan),
                np.where(~back_mask, z, np.nan),
                rcount=max(6, state.config.sphere_resolution // 8),
                ccount=max(6, state.config.sphere_resolution // 8),
                linewidth=0.3,
                alpha=0.7,
            )
            elevation = 20.0
        else:
            axis.plot_surface(
                x,
                y,
                z,
                facecolors=facecolors,
                rcount=state.config.sphere_resolution,
                ccount=state.config.sphere_resolution,
                linewidth=0,
                shade=False,
                antialiased=False,
            )
            elevation = 25.0
        axis.view_init(elevation, float(state.legacy_frame_index[index]) * 2.0)
        axis.set_axis_off()
        axis.set_box_aspect((1, 1, 1))
        images.append(_png_bytes(figure))
        plt.close(figure)
    duration = (sphere_step * state.config.legacy_frame_stride) / 24.0
    imageio.mimsave(path, images, duration=duration, loop=0, subrectangles=True)


def _write_metrics(path: Path, state: LegacyFaithfulState) -> None:
    signed_static = state.flowpoint_sector[:, None, None] * state.flowpoint_frames[0][None, :, :]
    legacy_spatial = spatial_2d_diagnostics(state.elastic_pi)
    canonical_spatial = spatial_2d_diagnostics(state.canonical_elastic_pi)
    rows = (
        ("carrier_std", float(np.std(state.carrier))),
        ("diffraction_peak", float(np.max(state.diffraction))),
        ("radial_profile_count", float(state.radial_profiles.shape[0])),
        ("legacy_elastic_pi_min", float(np.min(state.elastic_pi))),
        ("legacy_elastic_pi_max", float(np.max(state.elastic_pi))),
        ("legacy_elastic_pi_row_broadcast_residual", legacy_spatial["row_broadcast_residual"]),
        ("legacy_elastic_pi_column_broadcast_residual", legacy_spatial["column_broadcast_residual"]),
        ("legacy_elastic_pi_axis_gradient_balance", legacy_spatial["axis_gradient_balance"]),
        ("legacy_elastic_pi_effective_rank", legacy_spatial["effective_rank"]),
        ("canonical_elastic_pi_min", float(np.min(state.canonical_elastic_pi))),
        ("canonical_elastic_pi_max", float(np.max(state.canonical_elastic_pi))),
        ("canonical_elastic_pi_row_broadcast_residual", canonical_spatial["row_broadcast_residual"]),
        ("canonical_elastic_pi_column_broadcast_residual", canonical_spatial["column_broadcast_residual"]),
        ("canonical_elastic_pi_axis_gradient_balance", canonical_spatial["axis_gradient_balance"]),
        ("canonical_elastic_pi_effective_rank", canonical_spatial["effective_rank"]),
        ("flicker_intrinsic_deformation", float(np.linalg.norm(state.flowpoint_frames - signed_static))),
        ("scatter_intrinsic_deformation", float(np.linalg.norm(state.scatter_trajectory_4d[-1] - state.scatter_trajectory_4d[0]))),
        ("scatter_reference_rank", float(np.linalg.matrix_rank(state.scatter_reference_4d))),
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("metric", "value"))
        writer.writerows(rows)


def _write_source_removal(path: Path, state: LegacyFaithfulState) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("source", "necessity_residual", "necessary"))
        for source, residual in sorted(state.source_removal.items()):
            writer.writerow((source, f"{residual:.17g}", residual > 0.0))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_legacy_faithful_suite(
    output_dir: str | Path,
    *,
    seed: int = 1,
    grid_size: int = 240,
    time_steps: int = 48,
    point_count: int = 8000,
    sphere_resolution: int = 64,
) -> dict[str, object]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for existing in output.iterdir():
        if existing.is_file():
            existing.unlink()

    config = LegacyFaithfulConfig(
        seed=seed,
        grid_size=grid_size,
        time_steps=time_steps,
        point_count=point_count,
        sphere_resolution=sphere_resolution,
    )
    state = generate_legacy_faithful_state(config)

    _save_summary(output / STATIC_FILES[0], state)
    _save_contour(output / STATIC_FILES[1], state)
    _save_image(output / STATIC_FILES[2], state.diffraction, "inferno")
    _save_dfi_surface(output / STATIC_FILES[3], state)
    _save_surface(output / STATIC_FILES[4], state, state.static_pattern, "viridis")
    _save_image(output / STATIC_FILES[5], state.wavelet_ridges, "RdBu", aspect="auto")

    _flowpoint_animation(output / ANIMATED_FILES[0], state)
    _scatter_animation(output / ANIMATED_FILES[1], state)
    _sphere_animation(output / ANIMATED_FILES[2], state, half=False)
    _sphere_animation(output / ANIMATED_FILES[3], state, half=True)

    _write_metrics(output / DATA_FILES[0], state)
    np.savez_compressed(
        output / DATA_FILES[1],
        x=state.x,
        y=state.y,
        carrier=state.carrier,
        carrier_diffraction=state.carrier_diffraction,
        radial_profiles=state.radial_profiles,
        dfi_volume_profiles=state.dfi_volume_profiles,
        entropy_profiles=state.entropy_profiles,
        dfi_surface=state.dfi_surface,
        entropy=state.entropy,
        elastic_pi=state.elastic_pi,
        canonical_elastic_pi=state.canonical_elastic_pi,
        static_pattern=state.static_pattern,
        diffraction=state.diffraction,
        wavelet_ridges=state.wavelet_ridges,
        legacy_frame_index=state.legacy_frame_index,
        flowpoint_sector=state.flowpoint_sector,
        flowpoint_frames=state.flowpoint_frames,
        scatter_reference_4d=state.scatter_reference_4d,
        scatter_trajectory_4d=state.scatter_trajectory_4d,
        projection_3d=state.projection_3d,
        sphere_texture=state.sphere_texture,
    )
    _write_source_removal(output / DATA_FILES[2], state)

    manifest = {
        "schema_version": "3.0",
        "suite": "dtqc_legacy_faithful",
        "seed": seed,
        "grid_size": grid_size,
        "time_steps": time_steps,
        "legacy_frame_stride": state.config.legacy_frame_stride,
        "represented_legacy_frames": int(state.legacy_frame_index[-1] + state.config.legacy_frame_stride),
        "point_count": point_count,
        "radial_channels": state.config.radial_channels,
        "entropy_scale": state.config.entropy_scale,
        "source_audit": {
            "visual_generator": LEGACY_VISUAL_SOURCE,
            "canonical_dubler": CANONICAL_DUBLER_SOURCE,
            "visual_reference_directory": "tne_concepts/discrete_quasi_crystal_visualization",
        },
        "mathematical_bindings": {
            "carrier": "sum_{k=0}^{9} cos(2*pi*(cos(2*pi*k/10)*X + sin(2*pi*k/10)*Y)) / ptp",
            "diffraction": "log1p(abs(fftshift(fft2(field))))",
            "dfi": "sixty radial FFT profiles with the legacy DFI volume/entropy transform",
            "spatial_entropy": "S_2D(x,y)=mean_i interp(S_i,(x*cos(theta_i)+y*sin(theta_i))/sqrt(2)) over all sixty directional channels",
            "legacy_visual_elastic_pi": "pi*exp(+S_2D(x,y)/K_D); full-field directional backprojection with the legacy visual sign",
            "canonical_dubler_ratio": "pi*exp(-S_2D(x,y)/K_D); full-field canonical Dubler sign retained separately",
            "flowpoint": "alternating sector applied to an intrinsically phase-evolving ten-wave field",
            "scatter": "5-D integer cloud -> random 4-D projection -> phase-offset intrinsic 4-D oscillation -> OU-camera 3-D view",
        },
        "source_removal": state.source_removal,
        "spatial_regression": {
            "legacy_visual_elastic_pi": spatial_2d_diagnostics(state.elastic_pi),
            "canonical_dubler_elastic_pi": spatial_2d_diagnostics(state.canonical_elastic_pi),
        },
        "generated_files": [*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES, CHECKSUM_FILE],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    manifest_path = output / MANIFEST_FILE
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksummed = (*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES, MANIFEST_FILE)
    checksums = {
        "schema_version": "3.0",
        "algorithm": "sha256",
        "files": {name: _digest(output / name) for name in checksummed},
    }
    (output / CHECKSUM_FILE).write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    actual_inventory = tuple(sorted(path.name for path in output.iterdir() if path.is_file()))
    if actual_inventory != tuple(sorted(EXPECTED_INVENTORY)):
        raise RuntimeError(f"unexpected legacy-faithful artifact inventory: {actual_inventory}")
    for name in ANIMATED_FILES:
        with Image.open(output / name) as movie:
            if not movie.is_animated or movie.n_frames < 8:
                raise RuntimeError(f"{name} is not a valid multi-frame animation")

    return {
        "output_dir": output,
        "manifest": manifest_path,
        "checksums": output / CHECKSUM_FILE,
        "files": [output / name for name in EXPECTED_INVENTORY],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--grid-size", type=int, default=240)
    parser.add_argument("--time-steps", type=int, default=48)
    parser.add_argument("--point-count", type=int, default=8000)
    parser.add_argument("--sphere-resolution", type=int, default=64)
    args = parser.parse_args()
    run_legacy_faithful_suite(
        args.output_dir,
        seed=args.seed,
        grid_size=args.grid_size,
        time_steps=args.time_steps,
        point_count=args.point_count,
        sphere_resolution=args.sphere_resolution,
    )


if __name__ == "__main__":
    main()
