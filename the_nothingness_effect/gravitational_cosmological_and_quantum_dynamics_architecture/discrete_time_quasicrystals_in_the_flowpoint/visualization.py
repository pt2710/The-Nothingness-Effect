"""DTQC-specific static and dynamic evidence derived from canonical contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure, write_metadata
from the_nothingness_effect._runtime.artifacts.module_evidence import run_module_evidence
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import git_commit, parameter_hash
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import (
    evaluate_elastic_pi,
    require_elastic_pi_value,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import (
    fixture,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts import (
    contracts,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.spatial_elastic_pi import (
    apply_elastic_pi_on_all_axes,
    axis_complete_dfi,
    axis_complete_entropy,
    intrinsic_axis_names,
    projected_intrinsic_axes,
    require_true_2d,
)


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
INTRINSIC_AXIS_COUNT = 5


def _source_phases() -> tuple[np.ndarray, list[float]]:
    value = fixture()
    evaluations = [evaluate_contract(contract, value) for contract in contracts()]
    source_laws = evaluations[:4]
    phases = []
    weights = []
    for evaluation in source_laws:
        response = np.asarray(evaluation.output.response, dtype=float)
        phases.append(float(np.mean(response)))
        weights.append(float(np.linalg.vector_norm(response)) / np.sqrt(response.size))
    normalized_weights = np.asarray(weights, dtype=float)
    normalized_weights /= float(np.sum(normalized_weights))
    return normalized_weights, phases


def _quasicrystal_axis_components(
    size: int,
    phase: float = 0.0,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    tuple[str, ...],
]:
    """Return the projected five-axis carrier before scalar aggregation."""

    source_weights, phases = _source_phases()
    axis = np.linspace(-np.pi, np.pi, size)
    x_grid, y_grid = np.meshgrid(axis, axis, indexing="xy")
    angles, directions = projected_intrinsic_axes(INTRINSIC_AXIS_COUNT)
    frequencies = (
        1.0,
        np.sqrt(2.0),
        (1.0 + np.sqrt(5.0)) / 2.0,
        np.sqrt(3.0),
        np.sqrt(5.0),
    )
    raw_direction_weights = np.asarray(
        [source_weights[index % len(source_weights)] for index in range(len(angles))],
        dtype=float,
    )
    raw_direction_weights /= float(np.sum(raw_direction_weights))
    direction_weights = 0.5 * raw_direction_weights + 0.5 / len(angles)
    direction_weights /= float(np.sum(direction_weights))

    components = []
    for index, (direction, frequency) in enumerate(
        zip(directions, frequencies, strict=True)
    ):
        projection = x_grid * direction[0] + y_grid * direction[1]
        source_phase = phases[index % len(phases)]
        components.append(
            float(direction_weights[index])
            * np.cos(
                frequency * projection
                + source_phase
                + phase * (index + 1) / INTRINSIC_AXIS_COUNT
            )
        )
    axis_components = np.asarray(components, dtype=float)
    field = np.sum(axis_components, axis=0)
    field -= float(np.mean(field))
    scale = float(np.max(np.abs(field)))
    if scale <= 0.0 or not np.isfinite(scale):
        raise ValueError("DTQC source laws produced a degenerate visualization field")
    field /= scale
    axis_components /= scale
    return (
        x_grid,
        y_grid,
        field,
        axis_components,
        angles,
        directions,
        intrinsic_axis_names(INTRINSIC_AXIS_COUNT),
    )


def _quasicrystal_field(
    size: int,
    phase: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_grid, y_grid, field, _, _, _, _ = _quasicrystal_axis_components(size, phase)
    return x_grid, y_grid, field


def _wavelet_scalogram(row: np.ndarray) -> np.ndarray:
    maximum_scale = max(6, min(28, row.size // 4))
    scales = np.arange(2, maximum_scale + 1)
    coefficients = []
    for scale in scales:
        radius = min(4 * scale, row.size // 2 - 1)
        coordinate = np.arange(-radius, radius + 1, dtype=float)
        wavelet = np.exp(-(coordinate**2) / (2.0 * scale**2)) * np.cos(
            5.0 * coordinate / scale
        )
        wavelet -= float(np.mean(wavelet))
        norm = float(np.linalg.vector_norm(wavelet))
        coefficients.append(np.abs(np.convolve(row, wavelet / norm, mode="same")))
    return np.asarray(coefficients)


def _fallback_axis_components(
    field: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Provide a compatibility decomposition for direct private-function callers."""

    _, directions = projected_intrinsic_axes(INTRINSIC_AXIS_COUNT)
    components = np.repeat(
        np.asarray(field, dtype=float)[None, :, :] / INTRINSIC_AXIS_COUNT,
        INTRINSIC_AXIS_COUNT,
        axis=0,
    )
    weights = np.full(INTRINSIC_AXIS_COUNT, 1.0 / INTRINSIC_AXIS_COUNT)
    return components, directions, weights


def _elastic_entropy_field(
    field: np.ndarray,
    *,
    axis_components: np.ndarray | None = None,
    directions: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Construct five non-cancelling intrinsic-axis entropy channels."""

    if axis_components is None or directions is None or weights is None:
        axis_components, directions, weights = _fallback_axis_components(field)
    entropy, axis_entropy, diagnostics = axis_complete_entropy(
        axis_components,
        directions,
        weights,
    )
    require_true_2d(entropy, label="canonical DTQC axis-complete spatial entropy")
    return entropy, axis_entropy, diagnostics


def _elastic_pi_bundle(
    field: np.ndarray,
    *,
    axis_components: np.ndarray | None = None,
    directions: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    if axis_components is None or directions is None or weights is None:
        axis_components, directions, weights = _fallback_axis_components(field)
    axis_weights = np.asarray(weights, dtype=float)
    axis_weights /= float(np.sum(axis_weights))
    entropy, axis_entropy, entropy_diagnostics = _elastic_entropy_field(
        field,
        axis_components=axis_components,
        directions=directions,
        weights=axis_weights,
    )
    K_D = max(float(np.mean(entropy)), 1e-6)
    elastic_surface, axis_surfaces, axis_diagnostics = apply_elastic_pi_on_all_axes(
        axis_entropy,
        axis_weights,
        K_D=K_D,
        sign=-1.0,
    )

    direct = require_elastic_pi_value(
        evaluate_elastic_pi(
            entropy.reshape(-1),
            K_D=K_D,
        )
    ).reshape(entropy.shape)
    direct_residual = float(
        np.linalg.norm(elastic_surface - direct) / np.linalg.norm(direct)
    )
    if direct_residual > 1e-12:
        raise RuntimeError("axis-complete Elastic-pi disagrees with the canonical direct law")

    rendered_diagnostics = require_true_2d(
        elastic_surface,
        label="canonical DTQC axis-complete Elastic-pi surface",
    )
    angles, _ = projected_intrinsic_axes(axis_surfaces.shape[0])
    diagnostics: dict[str, Any] = {
        **rendered_diagnostics,
        **entropy_diagnostics,
        **axis_diagnostics,
        "axis_projection_angles_radians": [float(value) for value in angles],
        "axis_projection_angles_degrees": [float(np.degrees(value)) for value in angles],
        "direct_law_residual": direct_residual,
        "all_intrinsic_axes_applied": True,
    }
    return entropy, elastic_surface, axis_surfaces, diagnostics


def _elastic_pi_surface(
    field: np.ndarray,
    *,
    axis_components: np.ndarray | None = None,
    directions: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    entropy, elastic_surface, _, diagnostics = _elastic_pi_bundle(
        field,
        axis_components=axis_components,
        directions=directions,
        weights=weights,
    )
    return entropy, elastic_surface, diagnostics


def _save_axis_panel(
    output: Path,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    axis_surfaces: np.ndarray,
    axis_names: tuple[str, ...],
    angles: np.ndarray,
) -> Path:
    figure, axes = plt.subplots(2, 3, figsize=(11.4, 7.3), constrained_layout=True)
    minimum = float(np.min(axis_surfaces))
    maximum = float(np.max(axis_surfaces))
    image = None
    for axis, surface, name, angle in zip(
        axes.flat,
        axis_surfaces,
        axis_names,
        angles,
        strict=False,
    ):
        image = axis.imshow(
            surface,
            origin="lower",
            extent=(
                float(np.min(x_grid)),
                float(np.max(x_grid)),
                float(np.min(y_grid)),
                float(np.max(y_grid)),
            ),
            cmap="viridis",
            vmin=minimum,
            vmax=maximum,
            aspect="equal",
        )
        axis.set_title(f"intrinsic {name}-axis, projection {np.degrees(angle):.0f}°")
        axis.set_xlabel("projected X")
        axis.set_ylabel("projected Y")
    for axis in axes.flat[axis_surfaces.shape[0] :]:
        axis.axis("off")
    if image is not None:
        figure.colorbar(image, ax=list(axes.flat), label="per-axis Elastic-pi")
    figure.suptitle(
        "DTQC Elastic-pi applied independently on all intrinsic axes x, y, z, w, u"
    )
    path = save_figure(figure, output / "elastic_pi_intrinsic_axes.png", dpi=160)
    plt.close(figure)
    return path


def _static_visuals(
    output: Path,
    *,
    size: int,
) -> tuple[dict[str, Path], dict[str, Any]]:
    (
        x_grid,
        y_grid,
        field,
        axis_components,
        angles,
        directions,
        axis_names,
    ) = _quasicrystal_axis_components(size)
    source_weights, _ = _source_phases()
    raw_weights = np.asarray(
        [source_weights[index % len(source_weights)] for index in range(INTRINSIC_AXIS_COUNT)],
        dtype=float,
    )
    raw_weights /= float(np.sum(raw_weights))
    direction_weights = 0.5 * raw_weights + 0.5 / INTRINSIC_AXIS_COUNT
    direction_weights /= float(np.sum(direction_weights))

    dfi, _, dfi_diagnostics = axis_complete_dfi(
        axis_components,
        directions,
        direction_weights,
    )
    _, elastic_surface, axis_surfaces, spatial_diagnostics = _elastic_pi_bundle(
        field,
        axis_components=axis_components,
        directions=directions,
        weights=direction_weights,
    )
    spatial_diagnostics["dfi_axis_count"] = dfi_diagnostics["axis_count"]
    spatial_diagnostics["dfi_axis_names"] = dfi_diagnostics["axis_names"]
    spatial_diagnostics["dfi_axis_norms"] = dfi_diagnostics["axis_dfi_norms"]
    spatial_diagnostics["minimum_dfi_axis_norm"] = dfi_diagnostics[
        "minimum_axis_dfi_norm"
    ]

    diffraction = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(field))))
    scalogram = _wavelet_scalogram(field[field.shape[0] // 2])
    outputs: dict[str, Path] = {}

    figure, axis = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)
    contour = axis.contourf(x_grid, y_grid, field, levels=28, cmap="plasma")
    axis.set(
        title="DTQC quasiperiodic closure field",
        xlabel="projected X",
        ylabel="projected Y",
        aspect="equal",
    )
    figure.colorbar(contour, ax=axis, label="normalized response")
    outputs["contour"] = save_figure(figure, output / "qc_contour.png", dpi=170)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(6.2, 5.5), constrained_layout=True)
    image = axis.imshow(diffraction, origin="lower", cmap="inferno")
    axis.set(
        title="DTQC FFT diffraction support",
        xlabel="frequency X",
        ylabel="frequency Y",
    )
    figure.colorbar(image, ax=axis, label="log amplitude")
    outputs["diffraction"] = save_figure(
        figure,
        output / "diffraction_fft.png",
        dpi=170,
    )
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    image = axis.imshow(scalogram, origin="lower", aspect="auto", cmap="RdBu_r")
    axis.set(title="DTQC central-row wavelet scalogram", xlabel="sample", ylabel="scale index")
    figure.colorbar(image, ax=axis, label="wavelet magnitude")
    outputs["wavelet"] = save_figure(
        figure,
        output / "wavelet_central_row.png",
        dpi=170,
    )
    plt.close(figure)

    for name, surface, title, cmap in (
        (
            "dfi",
            dfi,
            "DTQC axis-complete normalized DFI (intrinsic x,y,z,w,u)",
            "coolwarm",
        ),
        (
            "elastic_pi",
            elastic_surface,
            "DTQC axis-complete Elastic-pi aggregate (intrinsic x,y,z,w,u)",
            "viridis",
        ),
    ):
        figure = plt.figure(figsize=(7.0, 5.2), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
        axis.plot_surface(
            x_grid,
            y_grid,
            surface,
            cmap=cmap,
            linewidth=0.0,
            antialiased=True,
        )
        axis.set(
            title=title,
            xlabel="projected X",
            ylabel="projected Y",
            zlabel=f"{name} scalar",
        )
        outputs[name] = save_figure(figure, output / f"{name}_surface.png", dpi=150)
        plt.close(figure)

    outputs["elastic_pi_axes"] = _save_axis_panel(
        output,
        x_grid,
        y_grid,
        axis_surfaces,
        axis_names,
        angles,
    )
    return outputs, spatial_diagnostics


def _animation(output: Path, *, size: int, frame_count: int) -> Path:
    _, _, initial = _quasicrystal_field(size)
    figure, axis = plt.subplots(figsize=(5.4, 5.0), constrained_layout=True)
    image = axis.imshow(
        initial,
        origin="lower",
        cmap="plasma",
        vmin=-1.0,
        vmax=1.0,
        animated=False,
    )
    axis.set_axis_off()

    def update(frame: int):
        phase = 2.0 * np.pi * frame / frame_count
        _, _, field = _quasicrystal_field(size, phase)
        image.set_data(field)
        axis.set_title(
            f"DTQC phase-clock evolution: {phase / (2.0 * np.pi):.2f} cycle"
        )
        return (image,)

    movie = animation.FuncAnimation(
        figure,
        update,
        frames=frame_count,
        interval=90,
        blit=False,
    )
    path = output / "dtqc_phase_clock_animation.gif"
    movie.save(path, writer=animation.PillowWriter(fps=10), dpi=95)
    plt.close(figure)
    return path


def run_dtqc_evidence(
    contract_runner: Any,
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = False,
) -> dict[str, Any]:
    output = Path(output_dir)
    mode = "simulation" if simulation else "test"
    base = run_module_evidence(
        "dtqc",
        contract_runner,
        output,
        seed=seed,
        simulation=simulation,
    )
    size = 96 if simulation else 64
    frame_count = 18 if simulation else 12
    visuals, spatial_diagnostics = _static_visuals(output, size=size)
    movie = _animation(output, size=64 if simulation else 48, frame_count=frame_count)
    phases = np.linspace(0.0, 2.0 * np.pi, frame_count, endpoint=False)
    phase_data = save_csv(
        output / f"dtqc_{mode}_phase_trace.csv",
        [
            {
                "frame": index,
                "phase_radians": float(phase),
                "center_response": float(
                    _quasicrystal_field(32, float(phase))[2][16, 16]
                ),
            }
            for index, phase in enumerate(phases)
        ],
    )
    parameters = {
        "module": "dtqc",
        "mode": mode,
        "seed": seed,
        "grid_size": size,
        "frame_count": frame_count,
        "intrinsic_axis_count": INTRINSIC_AXIS_COUNT,
    }
    manifest = write_metadata(
        output / f"dtqc_{mode}_visualization_manifest.json",
        {
            "module": "dtqc",
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[2]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "source_status": "canonical_dtqc_contract_outputs",
            "generated_files": [
                *(path.name for path in visuals.values()),
                movie.name,
                phase_data.name,
            ],
            "regeneration_command": (
                "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture."
                f"discrete_time_quasicrystals_in_the_flowpoint.{mode}.run_evidence"
            ),
            "approximation_metadata": {
                "field": (
                    "five intrinsic quasiperiodic carrier axes x,y,z,w,u projected into the rendered X-Y plane"
                ),
                "elastic_pi_entropy": (
                    "one independent entropy and Elastic-pi channel per intrinsic axis, built from axis carrier energy, "
                    "directional DFI, and directional Hessian curvature; positive weighted geometric aggregation; "
                    "the rendered surface height is the scalar response rather than an omitted spatial axis"
                ),
                "wavelet": "finite real Morlet-like diagnostic",
            },
            "intrinsic_axis_model": {
                "count": INTRINSIC_AXIS_COUNT,
                "names": list(intrinsic_axis_names(INTRINSIC_AXIS_COUNT)),
                "all_axes_applied": True,
                "additional_axes_policy": (
                    "axis count is derived from the active carrier decomposition; every declared axis receives its own channel"
                ),
            },
            "spatial_regression": spatial_diagnostics,
        },
    )
    return {
        **base,
        "visuals": visuals,
        "dtqc_animation": movie,
        "phase_data": phase_data,
        "visualization_manifest": manifest,
    }
