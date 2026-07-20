"""Complete canonical five-axis DTQC artifact materialization.

This module complements the contract visualizer with artifact classes that were
previously available only in ``legacy_faithful``. Every generated artifact is
recomputed from the canonical five-axis carrier and its independently applied
Elastic-pi channels.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.spatial_elastic_pi import (
    axis_complete_dfi,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.visualization import (
    INTRINSIC_AXIS_COUNT,
    _elastic_pi_bundle,
    _quasicrystal_axis_components,
    _source_phases,
)


STATIC_FILES = (
    "dtqc_summary.png",
)
ANIMATED_FILES = (
    "dtqc_flowpoint_flicker.gif",
    "dtqc_5d_scatter.gif",
    "dtqc_elastic_pi_sphere.gif",
    "dtqc_elastic_pi_half_sphere.gif",
    "dtqc_intrinsic_axis_cycle.gif",
)
DATA_FILES = (
    "dtqc_state.npz",
    "dtqc_axis_source_removal.csv",
    "dtqc_visual_metrics.csv",
)
COMPLETE_CANONICAL_FILES = (*STATIC_FILES, *ANIMATED_FILES, *DATA_FILES)


def _axis_weights() -> np.ndarray:
    source_weights, _ = _source_phases()
    raw = np.asarray(
        [source_weights[index % len(source_weights)] for index in range(INTRINSIC_AXIS_COUNT)],
        dtype=float,
    )
    raw /= float(np.sum(raw))
    weights = 0.5 * raw + 0.5 / INTRINSIC_AXIS_COUNT
    weights /= float(np.sum(weights))
    return weights


def _bundle(size: int, phase: float = 0.0) -> dict[str, Any]:
    (
        x_grid,
        y_grid,
        field,
        axis_components,
        angles,
        directions,
        axis_names,
    ) = _quasicrystal_axis_components(size, phase)
    weights = _axis_weights()
    dfi, axis_dfi, dfi_diagnostics = axis_complete_dfi(
        axis_components,
        directions,
        weights,
    )
    entropy, elastic_pi, axis_elastic_pi, diagnostics = _elastic_pi_bundle(
        field,
        axis_components=axis_components,
        directions=directions,
        weights=weights,
    )
    return {
        "x": x_grid,
        "y": y_grid,
        "field": field,
        "axis_components": axis_components,
        "angles": angles,
        "directions": directions,
        "axis_names": axis_names,
        "weights": weights,
        "dfi": dfi,
        "axis_dfi": axis_dfi,
        "entropy": entropy,
        "elastic_pi": elastic_pi,
        "axis_elastic_pi": axis_elastic_pi,
        "dfi_diagnostics": dfi_diagnostics,
        "diagnostics": diagnostics,
    }


def _figure_rgb(figure: plt.Figure) -> np.ndarray:
    figure.canvas.draw()
    width, height = figure.canvas.get_width_height()
    rgba = np.frombuffer(figure.canvas.buffer_rgba(), dtype=np.uint8).reshape(
        height,
        width,
        4,
    )
    return rgba[:, :, :3].copy()


def _save_summary(path: Path, bundle: dict[str, Any]) -> Path:
    field = np.asarray(bundle["field"])
    diffraction = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(field))))
    panels = (
        (field, "five-axis DTQC carrier", "plasma"),
        (diffraction, "FFT diffraction support", "inferno"),
        (bundle["dfi"], "axis-complete DFI", "coolwarm"),
        (bundle["entropy"], "five-channel entropy aggregate", "cividis"),
        (bundle["elastic_pi"], "axis-complete Elastic-pi", "viridis"),
        (bundle["axis_elastic_pi"][3], "fourth diagonal axis w", "viridis"),
    )
    figure, axes = plt.subplots(2, 3, figsize=(12.0, 7.7), constrained_layout=True)
    for axis, (value, title, cmap) in zip(axes.flat, panels, strict=True):
        image = axis.imshow(value, origin="lower", cmap=cmap, aspect="equal")
        axis.set_title(title)
        axis.axis("off")
        figure.colorbar(image, ax=axis, shrink=0.72)
    figure.suptitle("Canonical DTQC five-axis artifact summary: x, y, z, w, u")
    result = save_figure(figure, path, dpi=170)
    plt.close(figure)
    return result


def _flowpoint_flicker(path: Path, *, size: int, frame_count: int) -> Path:
    images: list[np.ndarray] = []
    for frame_index in range(frame_count):
        phase = 2.0 * math.pi * frame_index / frame_count
        bundle = _bundle(size, phase)
        sector = 1.0 if frame_index % 2 == 0 else -1.0
        elastic_gain = bundle["elastic_pi"] / float(np.mean(bundle["elastic_pi"]))
        value = sector * bundle["field"] * elastic_gain
        figure, axis = plt.subplots(figsize=(5.4, 5.0), constrained_layout=True)
        image = axis.imshow(value, origin="lower", cmap="plasma", vmin=-1.4, vmax=1.4)
        axis.set_axis_off()
        axis.set_title(
            "Canonical Flowpoint flicker — Elastic-pi on x,y,z,w,u\n"
            f"sector={int(sector):+d}, phase={phase / (2.0 * math.pi):.2f} cycle"
        )
        figure.colorbar(image, ax=axis, shrink=0.72)
        images.append(_figure_rgb(figure))
        plt.close(figure)
    imageio.mimsave(path, images, duration=0.10, loop=0, subrectangles=True)
    return path


def _scatter_inputs(bundle: dict[str, Any], *, seed: int, point_count: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    base = rng.normal(0.0, 1.0, size=(point_count, INTRINSIC_AXIS_COUNT))
    axis_surfaces = np.asarray(bundle["axis_elastic_pi"], dtype=float)
    size = axis_surfaces.shape[-1]
    gains = np.empty_like(base)
    for axis_index in range(INTRINSIC_AXIS_COUNT):
        x_index = np.clip(
            ((np.tanh(base[:, axis_index]) + 1.0) * 0.5 * (size - 1)).astype(int),
            0,
            size - 1,
        )
        y_index = np.clip(
            ((np.tanh(base[:, (axis_index + 1) % INTRINSIC_AXIS_COUNT]) + 1.0) * 0.5 * (size - 1)).astype(int),
            0,
            size - 1,
        )
        sampled = axis_surfaces[axis_index, y_index, x_index]
        gains[:, axis_index] = sampled / float(np.mean(axis_surfaces[axis_index]))
    gains = np.clip(gains, 0.72, 1.28)
    projection_rng = np.random.default_rng(2710)
    orthogonal, _ = np.linalg.qr(
        projection_rng.normal(size=(INTRINSIC_AXIS_COUNT, INTRINSIC_AXIS_COUNT))
    )
    projection = orthogonal[:, :3].T
    return base, gains, projection


def _scatter_animation(
    path: Path,
    bundle: dict[str, Any],
    *,
    seed: int,
    frame_count: int,
    point_count: int,
) -> tuple[Path, np.ndarray, np.ndarray, np.ndarray]:
    base, gains, projection = _scatter_inputs(
        bundle,
        seed=seed,
        point_count=point_count,
    )
    images: list[np.ndarray] = []
    for frame_index in range(frame_count):
        phase = 2.0 * math.pi * frame_index / frame_count
        coordinates = base * gains
        for axis_index in range(INTRINSIC_AXIS_COUNT):
            coordinates[:, axis_index] += 0.32 * np.sin(
                base[:, (axis_index + 1) % INTRINSIC_AXIS_COUNT]
                + phase * (axis_index + 1)
            )
        projected = coordinates @ projection.T
        color = coordinates[:, 3] + coordinates[:, 4]
        limit = max(3.8, float(np.quantile(np.abs(projected), 0.997)))
        figure = plt.figure(figsize=(6.3, 6.0), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
        axis.scatter(
            projected[:, 0],
            projected[:, 1],
            projected[:, 2],
            c=color,
            cmap="Spectral",
            s=2.2,
            alpha=0.82,
            depthshade=True,
        )
        axis.set(
            xlim=(-limit, limit),
            ylim=(-limit, limit),
            zlim=(-limit, limit),
            title="Canonical 5D DTQC cloud — Elastic-pi gain on x,y,z,w,u",
        )
        axis.set_axis_off()
        images.append(_figure_rgb(figure))
        plt.close(figure)
    imageio.mimsave(path, images, duration=0.10, loop=0, subrectangles=True)
    return path, base, gains, projection


def _sphere_coordinates(texture: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    resolution = texture.shape[0]
    theta = np.linspace(0.0, math.pi, resolution)
    phi = np.linspace(0.0, 2.0 * math.pi, resolution)
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="xy")
    normalized = (texture - float(np.min(texture))) / max(float(np.ptp(texture)), 1e-12)
    radius = 1.0 + 0.22 * (normalized - 0.5)
    x = radius * np.sin(theta_grid) * np.cos(phi_grid)
    y = radius * np.sin(theta_grid) * np.sin(phi_grid)
    z = radius * np.cos(theta_grid)
    return x, y, z, normalized, phi_grid >= math.pi


def _sphere_animations(
    full_path: Path,
    half_path: Path,
    *,
    size: int,
    frame_count: int,
) -> tuple[Path, Path]:
    full_images: list[np.ndarray] = []
    half_images: list[np.ndarray] = []
    for frame_index in range(frame_count):
        phase = 2.0 * math.pi * frame_index / frame_count
        texture = np.asarray(_bundle(size, phase)["elastic_pi"], dtype=float)
        x, y, z, normalized, back_mask = _sphere_coordinates(texture)
        facecolors = plt.cm.viridis(normalized)

        figure = plt.figure(figsize=(6.0, 6.0), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
        axis.plot_surface(
            x,
            y,
            z,
            facecolors=facecolors,
            rcount=size,
            ccount=size,
            linewidth=0,
            antialiased=False,
            shade=False,
        )
        axis.view_init(25.0, 360.0 * frame_index / frame_count)
        axis.set_box_aspect((1, 1, 1))
        axis.set_axis_off()
        axis.set_title("Canonical Elastic-pi sphere — all five intrinsic axes")
        full_images.append(_figure_rgb(figure))
        plt.close(figure)

        figure = plt.figure(figsize=(6.0, 6.0), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
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
            rcount=max(6, size // 8),
            ccount=max(6, size // 8),
            linewidth=0.35,
            alpha=0.72,
        )
        axis.view_init(22.0, 360.0 * frame_index / frame_count)
        axis.set_box_aspect((1, 1, 1))
        axis.set_axis_off()
        axis.set_title("Canonical Elastic-pi half-sphere — all five intrinsic axes")
        half_images.append(_figure_rgb(figure))
        plt.close(figure)

    imageio.mimsave(full_path, full_images, duration=0.12, loop=0, subrectangles=True)
    imageio.mimsave(half_path, half_images, duration=0.12, loop=0, subrectangles=True)
    return full_path, half_path


def _axis_cycle(path: Path, bundle: dict[str, Any]) -> Path:
    images: list[np.ndarray] = []
    surfaces = np.asarray(bundle["axis_elastic_pi"], dtype=float)
    names = tuple(bundle["axis_names"])
    angles = np.asarray(bundle["angles"], dtype=float)
    minimum = float(np.min(surfaces))
    maximum = float(np.max(surfaces))
    for index, (surface, name, angle) in enumerate(
        zip(surfaces, names, angles, strict=True)
    ):
        for hold in range(2):
            figure, axis = plt.subplots(figsize=(5.6, 5.0), constrained_layout=True)
            image = axis.imshow(
                surface,
                origin="lower",
                cmap="viridis",
                vmin=minimum,
                vmax=maximum,
                aspect="equal",
            )
            axis.set_title(
                f"Intrinsic {name}-axis Elastic-pi — projection {np.degrees(angle):.0f}°\n"
                f"axis {index + 1}/{INTRINSIC_AXIS_COUNT}, hold {hold + 1}/2"
            )
            axis.set_xlabel("projected X")
            axis.set_ylabel("projected Y")
            figure.colorbar(image, ax=axis, label="per-axis Elastic-pi")
            images.append(_figure_rgb(figure))
            plt.close(figure)
    imageio.mimsave(path, images, duration=0.20, loop=0, subrectangles=True)
    return path


def _write_data(
    output: Path,
    bundle: dict[str, Any],
    *,
    seed: int,
    scatter_base: np.ndarray,
    scatter_gains: np.ndarray,
    scatter_projection: np.ndarray,
) -> tuple[Path, Path, Path]:
    state_path = output / DATA_FILES[0]
    np.savez_compressed(
        state_path,
        seed=np.asarray(seed),
        x=bundle["x"],
        y=bundle["y"],
        field=bundle["field"],
        axis_components=bundle["axis_components"],
        axis_angles=bundle["angles"],
        axis_directions=bundle["directions"],
        axis_weights=bundle["weights"],
        dfi=bundle["dfi"],
        axis_dfi=bundle["axis_dfi"],
        entropy=bundle["entropy"],
        elastic_pi=bundle["elastic_pi"],
        axis_elastic_pi=bundle["axis_elastic_pi"],
        scatter_reference_5d=scatter_base,
        scatter_elastic_pi_gains=scatter_gains,
        scatter_projection_3d=scatter_projection,
    )

    diagnostics = bundle["diagnostics"]
    dfi_diagnostics = bundle["dfi_diagnostics"]
    source_path = save_csv(
        output / DATA_FILES[1],
        [
            {
                "axis_index": index,
                "axis_name": name,
                "projection_angle_degrees": float(np.degrees(bundle["angles"][index])),
                "axis_weight": float(bundle["weights"][index]),
                "entropy_norm": float(diagnostics["axis_entropy_norms"][index]),
                "dfi_norm": float(dfi_diagnostics["axis_dfi_norms"][index]),
                "elastic_pi_span": float(diagnostics["axis_elastic_pi_spans"][index]),
                "source_removal_residual": float(
                    diagnostics["axis_source_removal_residuals"][index]
                ),
                "necessary": bool(
                    diagnostics["axis_source_removal_residuals"][index] > 0.0
                ),
            }
            for index, name in enumerate(bundle["axis_names"])
        ],
    )
    metrics_path = save_csv(
        output / DATA_FILES[2],
        [
            {"metric": "intrinsic_axis_count", "value": INTRINSIC_AXIS_COUNT},
            {
                "metric": "minimum_axis_source_removal_residual",
                "value": float(diagnostics["minimum_axis_source_removal_residual"]),
            },
            {
                "metric": "minimum_axis_dfi_norm",
                "value": float(dfi_diagnostics["minimum_axis_dfi_norm"]),
            },
            {
                "metric": "direct_law_residual",
                "value": float(diagnostics["direct_law_residual"]),
            },
            {
                "metric": "effective_rank",
                "value": float(diagnostics["effective_rank"]),
            },
            {
                "metric": "flowpoint_flicker_intrinsic_axes",
                "value": INTRINSIC_AXIS_COUNT,
            },
            {
                "metric": "scatter_dimension",
                "value": scatter_base.shape[1],
            },
        ],
    )
    return state_path, source_path, metrics_path


def generate_complete_canonical_artifacts(
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = True,
) -> dict[str, Path]:
    """Generate the complete root-level canonical artifact-class inventory."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    size = 64 if simulation else 48
    frame_count = 18 if simulation else 10
    sphere_frames = 12 if simulation else 8
    point_count = 1800 if simulation else 700
    bundle = _bundle(size)

    outputs: dict[str, Path] = {}
    outputs["summary"] = _save_summary(output / STATIC_FILES[0], bundle)
    outputs["flowpoint_flicker"] = _flowpoint_flicker(
        output / ANIMATED_FILES[0],
        size=48 if simulation else 40,
        frame_count=frame_count,
    )
    (
        outputs["scatter_5d"],
        scatter_base,
        scatter_gains,
        scatter_projection,
    ) = _scatter_animation(
        output / ANIMATED_FILES[1],
        bundle,
        seed=seed,
        frame_count=frame_count,
        point_count=point_count,
    )
    outputs["elastic_pi_sphere"], outputs["elastic_pi_half_sphere"] = (
        _sphere_animations(
            output / ANIMATED_FILES[2],
            output / ANIMATED_FILES[3],
            size=48 if simulation else 40,
            frame_count=sphere_frames,
        )
    )
    outputs["intrinsic_axis_cycle"] = _axis_cycle(
        output / ANIMATED_FILES[4],
        bundle,
    )
    (
        outputs["state"],
        outputs["axis_source_removal"],
        outputs["visual_metrics"],
    ) = _write_data(
        output,
        bundle,
        seed=seed,
        scatter_base=scatter_base,
        scatter_gains=scatter_gains,
        scatter_projection=scatter_projection,
    )

    missing = [name for name in COMPLETE_CANONICAL_FILES if not (output / name).is_file()]
    if missing:
        raise RuntimeError(f"missing canonical DTQC artifact classes: {missing}")
    return outputs
