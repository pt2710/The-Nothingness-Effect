"""DTQC-specific static and dynamic evidence derived from canonical contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts import contracts
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import evaluate_elastic_pi, require_elastic_pi_value
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_artifacts import fixture
from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure, write_metadata
from the_nothingness_effect._runtime.artifacts.module_evidence import run_module_evidence
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import git_commit, parameter_hash


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


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


def _quasicrystal_field(size: int, phase: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    weights, phases = _source_phases()
    axis = np.linspace(-np.pi, np.pi, size)
    x_grid, y_grid = np.meshgrid(axis, axis, indexing="xy")
    angles = np.pi * np.arange(5) / 5.0
    frequencies = (1.0, np.sqrt(2.0), (1.0 + np.sqrt(5.0)) / 2.0, np.sqrt(3.0), np.sqrt(5.0))
    field = np.zeros_like(x_grid)
    for index, (angle, frequency) in enumerate(zip(angles, frequencies, strict=True)):
        projection = x_grid * np.cos(angle) + y_grid * np.sin(angle)
        weight = float(weights[index % len(weights)])
        source_phase = phases[index % len(phases)]
        field += weight * np.cos(frequency * projection + source_phase + phase * (index + 1) / 5.0)
    field -= float(np.mean(field))
    scale = float(np.max(np.abs(field)))
    if scale <= 0.0 or not np.isfinite(scale):
        raise ValueError("DTQC source laws produced a degenerate visualization field")
    return x_grid, y_grid, field / scale


def _wavelet_scalogram(row: np.ndarray) -> np.ndarray:
    maximum_scale = max(6, min(28, row.size // 4))
    scales = np.arange(2, maximum_scale + 1)
    coefficients = []
    for scale in scales:
        radius = min(4 * scale, row.size // 2 - 1)
        coordinate = np.arange(-radius, radius + 1, dtype=float)
        wavelet = np.exp(-(coordinate**2) / (2.0 * scale**2)) * np.cos(5.0 * coordinate / scale)
        wavelet -= float(np.mean(wavelet))
        norm = float(np.linalg.vector_norm(wavelet))
        coefficients.append(np.abs(np.convolve(row, wavelet / norm, mode="same")))
    return np.asarray(coefficients)


def _static_visuals(output: Path, *, size: int) -> dict[str, Path]:
    x_grid, y_grid, field = _quasicrystal_field(size)
    gradient_y, gradient_x = np.gradient(field)
    dfi = np.hypot(gradient_x, gradient_y)
    dfi_scale = float(np.max(dfi))
    dfi = dfi / dfi_scale if dfi_scale > 0.0 else dfi
    elastic = evaluate_elastic_pi(dfi.reshape(-1), K_D=max(float(np.mean(dfi)), 1e-6))
    elastic_surface = require_elastic_pi_value(elastic).reshape(dfi.shape)
    diffraction = np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(field))))
    scalogram = _wavelet_scalogram(field[field.shape[0] // 2])
    outputs: dict[str, Path] = {}

    figure, axis = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)
    contour = axis.contourf(x_grid, y_grid, field, levels=28, cmap="plasma")
    axis.set(title="DTQC quasiperiodic closure field", xlabel="x", ylabel="y", aspect="equal")
    figure.colorbar(contour, ax=axis, label="normalized response")
    outputs["contour"] = save_figure(figure, output / "qc_contour.png", dpi=170)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(6.2, 5.5), constrained_layout=True)
    image = axis.imshow(diffraction, origin="lower", cmap="inferno")
    axis.set(title="DTQC FFT diffraction support", xlabel="frequency x", ylabel="frequency y")
    figure.colorbar(image, ax=axis, label="log amplitude")
    outputs["diffraction"] = save_figure(figure, output / "diffraction_fft.png", dpi=170)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    image = axis.imshow(scalogram, origin="lower", aspect="auto", cmap="RdBu_r")
    axis.set(title="DTQC central-row wavelet scalogram", xlabel="sample", ylabel="scale index")
    figure.colorbar(image, ax=axis, label="wavelet magnitude")
    outputs["wavelet"] = save_figure(figure, output / "wavelet_central_row.png", dpi=170)
    plt.close(figure)

    for name, surface, title, cmap in (
        ("dfi", dfi, "DTQC normalized DFI surface", "coolwarm"),
        ("elastic_pi", elastic_surface, "DTQC exact Elastic-pi surface", "viridis"),
    ):
        figure = plt.figure(figsize=(7.0, 5.2), constrained_layout=True)
        axis = figure.add_subplot(111, projection="3d")
        axis.plot_surface(x_grid, y_grid, surface, cmap=cmap, linewidth=0.0, antialiased=True)
        axis.set(title=title, xlabel="x", ylabel="y", zlabel=name)
        outputs[name] = save_figure(figure, output / f"{name}_surface.png", dpi=150)
        plt.close(figure)
    return outputs


def _animation(output: Path, *, size: int, frame_count: int) -> Path:
    _, _, initial = _quasicrystal_field(size)
    figure, axis = plt.subplots(figsize=(5.4, 5.0), constrained_layout=True)
    image = axis.imshow(initial, origin="lower", cmap="plasma", vmin=-1.0, vmax=1.0, animated=False)
    axis.set_axis_off()

    def update(frame: int):
        phase = 2.0 * np.pi * frame / frame_count
        _, _, field = _quasicrystal_field(size, phase)
        image.set_data(field)
        axis.set_title(f"DTQC phase-clock evolution: {phase / (2.0 * np.pi):.2f} cycle")
        return (image,)

    movie = animation.FuncAnimation(figure, update, frames=frame_count, interval=90, blit=False)
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
    base = run_module_evidence("dtqc", contract_runner, output, seed=seed, simulation=simulation)
    size = 96 if simulation else 64
    frame_count = 18 if simulation else 12
    visuals = _static_visuals(output, size=size)
    movie = _animation(output, size=64 if simulation else 48, frame_count=frame_count)
    phases = np.linspace(0.0, 2.0 * np.pi, frame_count, endpoint=False)
    phase_data = save_csv(
        output / f"dtqc_{mode}_phase_trace.csv",
        [
            {
                "frame": index,
                "phase_radians": float(phase),
                "center_response": float(_quasicrystal_field(32, float(phase))[2][16, 16]),
            }
            for index, phase in enumerate(phases)
        ],
    )
    parameters = {"module": "dtqc", "mode": mode, "seed": seed, "grid_size": size, "frame_count": frame_count}
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
            "generated_files": [*(path.name for path in visuals.values()), movie.name, phase_data.name],
            "regeneration_command": f"python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.{mode}.run_evidence",
            "approximation_metadata": {
                "field": "finite quasiperiodic projection of all four DTQC A-source responses",
                "wavelet": "finite real Morlet-like diagnostic",
            },
        },
    )
    return {**base, "visuals": visuals, "dtqc_animation": movie, "phase_data": phase_data, "visualization_manifest": manifest}
