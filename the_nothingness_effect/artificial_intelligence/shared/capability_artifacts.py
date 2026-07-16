"""Local artifact generation for the six TNE AI output capabilities."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import wave
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

from the_nothingness_effect._runtime.artifacts.io import save_csv, save_figure, write_metadata
from the_nothingness_effect.artificial_intelligence.bidirectional_color_classification import BidirectionalColorClassifier
from the_nothingness_effect.artificial_intelligence.bidirectional_sound_classification import BidirectionalSoundClassifier
from the_nothingness_effect.artificial_intelligence.color_classification import ColorClassifier
from the_nothingness_effect.artificial_intelligence.color_cloning import ColorCloner
from the_nothingness_effect.artificial_intelligence.qenn.contracts import APPENDIX, APPENDIX_SHA256
from the_nothingness_effect.artificial_intelligence.shared.capability_fixtures import (
    COLOR_LABELS,
    SOUND_PROTOTYPE_FREQUENCIES,
    color_clone_image,
    color_images,
    sound_clone_waveform,
    tone_batch,
)
from the_nothingness_effect.artificial_intelligence.sound_classification import SoundClassifier
from the_nothingness_effect.artificial_intelligence.sound_cloning import SoundCloner
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import git_commit, parameter_hash


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"
CAPABILITIES = (
    "color_classification",
    "sound_classification",
    "bidirectional_color_classification",
    "bidirectional_sound_classification",
    "color_cloning",
    "sound_cloning",
)
RELATED_COMPLEX_IDS = {
    "color_classification": (
        "dfi_entropy_plateau_dfi_divergence_spiking",
        "lyapunov_entropy_dissipation_functional",
    ),
    "sound_classification": (
        "pv_inflation_pure_point_diffraction_non_pv_salem_leakage",
        "pv_parseval_spectral_energy_lock",
    ),
    "bidirectional_color_classification": (
        "soi_modality_invariant_convergence_and_collapse_completeness",
        "soi_modality_dual_closure",
        "modality_collapse_symmetry_operator",
    ),
    "bidirectional_sound_classification": (
        "motif_spectral_dual_regularity_law_for_soinets",
        "soi_modality_dual_closure",
        "motif_spectral_modality_collapse_spatial_field",
    ),
    "color_cloning": (
        "lyapunov_weight_lattice_fourier_pisot_spectral_purification",
        "parseval_energy_bijection_for_epochs_energy_mass_imbalance",
    ),
    "sound_cloning": (
        "lyapunov_weight_lattice_fourier_pisot_spectral_purification",
        "pv_parseval_spectral_energy_lock",
    ),
}


@dataclass
class CapabilityEvaluation:
    rows: list[dict[str, Any]]
    metrics: dict[str, float]
    residuals: list[float]
    closure_status: str
    payload: dict[str, Any]


def _confusion_matrix(targets: torch.Tensor, predictions: torch.Tensor, size: int) -> np.ndarray:
    matrix = np.zeros((size, size), dtype=int)
    for truth, prediction in zip(targets.detach().cpu().tolist(), predictions.detach().cpu().tolist(), strict=True):
        matrix[int(truth), int(prediction)] += 1
    return matrix


def _classification_rows(
    targets: torch.Tensor,
    predictions: torch.Tensor,
    confidence: torch.Tensor,
    labels: tuple[str, ...],
) -> list[dict[str, Any]]:
    return [
        {
            "sample": index,
            "true_index": int(truth),
            "true_label": labels[int(truth)],
            "predicted_index": int(prediction),
            "predicted_label": labels[int(prediction)],
            "confidence": float(score),
            "correct": bool(truth == prediction),
        }
        for index, (truth, prediction, score) in enumerate(
            zip(targets, predictions, confidence, strict=True)
        )
    ]


def _evaluate(capability: str, *, seed: int, simulation: bool) -> CapabilityEvaluation:
    samples_per_class = 8 if simulation else 3
    if capability == "color_classification":
        images, targets = color_images(seed=seed, samples_per_class=samples_per_class, image_size=14 if simulation else 10)
        result = ColorClassifier()(images)
        accuracy = float((result.class_indices == targets).float().mean())
        rows = _classification_rows(targets, result.class_indices, result.confidence, result.labels)
        return CapabilityEvaluation(
            rows,
            {"accuracy": accuracy, "mean_confidence": float(result.confidence.mean())},
            [float(value) for value in result.residuals.values()],
            result.closure_status.value,
            {"images": images, "targets": targets, "result": result},
        )
    if capability == "sound_classification":
        waveforms, targets = tone_batch(seed=seed, samples_per_class=samples_per_class)
        model = SoundClassifier()
        result = model(waveforms)
        accuracy = float((result.class_indices == targets).float().mean())
        rows = _classification_rows(targets, result.class_indices, result.confidence, result.labels)
        frequencies = model.dominant_frequencies(waveforms)
        for row, frequency in zip(rows, frequencies, strict=True):
            row["dominant_frequency_hz"] = float(frequency)
        return CapabilityEvaluation(
            rows,
            {"accuracy": accuracy, "mean_confidence": float(result.confidence.mean())},
            [float(value) for value in result.residuals.values()],
            result.closure_status.value,
            {"waveforms": waveforms, "targets": targets, "result": result, "frequencies": frequencies},
        )
    if capability == "bidirectional_color_classification":
        images, targets = color_images(seed=seed, samples_per_class=samples_per_class, image_size=14 if simulation else 10)
        result = BidirectionalColorClassifier()(images)
        accuracy = float((result.forward.class_indices == targets).float().mean())
        roundtrip_accuracy = float((result.roundtrip.class_indices == result.forward.class_indices).float().mean())
        rows = _classification_rows(targets, result.forward.class_indices, result.forward.confidence, result.forward.labels)
        for row, roundtrip in zip(rows, result.roundtrip.predicted_labels, strict=True):
            row["roundtrip_label"] = roundtrip
        return CapabilityEvaluation(
            rows,
            {
                "accuracy": accuracy,
                "roundtrip_accuracy": roundtrip_accuracy,
                "modality_rmse": float(result.modality_reconstruction_residual),
            },
            [float(result.label_closure_residual), float(result.modality_reconstruction_residual)],
            result.closure_status.value,
            {"images": images, "targets": targets, "result": result},
        )
    if capability == "bidirectional_sound_classification":
        waveforms, targets = tone_batch(seed=seed, samples_per_class=samples_per_class)
        model = BidirectionalSoundClassifier()
        result = model(waveforms)
        accuracy = float((result.forward.class_indices == targets).float().mean())
        roundtrip_accuracy = float((result.roundtrip.class_indices == result.forward.class_indices).float().mean())
        rows = _classification_rows(targets, result.forward.class_indices, result.forward.confidence, result.forward.labels)
        input_frequencies = model.classifier.dominant_frequencies(waveforms)
        reconstructed_frequencies = model.classifier.dominant_frequencies(result.reconstructed_modality)
        for row, input_frequency, reconstructed_frequency in zip(
            rows, input_frequencies, reconstructed_frequencies, strict=True
        ):
            row["input_frequency_hz"] = float(input_frequency)
            row["reconstructed_frequency_hz"] = float(reconstructed_frequency)
        return CapabilityEvaluation(
            rows,
            {
                "accuracy": accuracy,
                "roundtrip_accuracy": roundtrip_accuracy,
                "modality_rmse": float(result.modality_reconstruction_residual),
            },
            [float(result.label_closure_residual), float(result.modality_reconstruction_residual)],
            result.closure_status.value,
            {
                "waveforms": waveforms,
                "targets": targets,
                "result": result,
                "input_frequencies": input_frequencies,
                "reconstructed_frequencies": reconstructed_frequencies,
            },
        )
    if capability == "color_cloning":
        image = color_clone_image(image_size=40 if simulation else 24)
        result = ColorCloner()(image)
        rmse = float(result.residuals["spectral_reconstruction"])
        peak_error = float(torch.max(torch.abs(image - result.clone)))
        return CapabilityEvaluation(
            [{"metric": "rmse", "value": rmse}, {"metric": "peak_error", "value": peak_error}],
            {"rmse": rmse, "peak_error": peak_error},
            [float(value) for value in result.residuals.values()],
            result.closure_status.value,
            {"image": image, "result": result},
        )
    if capability == "sound_cloning":
        waveform = sound_clone_waveform(sample_count=4096 if simulation else 2048)
        result = SoundCloner()(waveform)
        error = waveform - result.clone
        rmse = float(torch.sqrt(torch.mean(error.square())))
        signal_energy = float(torch.sum(waveform.square()))
        error_energy = float(torch.sum(error.square()))
        snr = 10.0 * math.log10(signal_energy / max(error_energy, 1e-30))
        return CapabilityEvaluation(
            [{"metric": "rmse", "value": rmse}, {"metric": "snr_db", "value": snr}],
            {"rmse": rmse, "snr_db": snr},
            [float(value) for value in result.residuals.values()],
            result.closure_status.value,
            {"waveform": waveform, "result": result},
        )
    raise ValueError(f"Unknown TNE AI capability: {capability}")


def _plot_evaluation(capability: str, evaluation: CapabilityEvaluation) -> plt.Figure:
    payload = evaluation.payload
    if capability in {"color_classification", "bidirectional_color_classification"}:
        result = payload["result"].forward if capability.startswith("bidirectional") else payload["result"]
        matrix = _confusion_matrix(payload["targets"], result.class_indices, len(COLOR_LABELS))
        figure, axis = plt.subplots(figsize=(6.2, 5.2), constrained_layout=True)
        image = axis.imshow(matrix, cmap="Blues")
        axis.set(
            title=capability.replace("_", " ").title(),
            xlabel="Predicted color",
            ylabel="True color",
            xticks=range(len(COLOR_LABELS)),
            yticks=range(len(COLOR_LABELS)),
        )
        axis.set_xticklabels(COLOR_LABELS, rotation=35, ha="right")
        axis.set_yticklabels(COLOR_LABELS)
        for row in range(matrix.shape[0]):
            for column in range(matrix.shape[1]):
                axis.text(column, row, int(matrix[row, column]), ha="center", va="center")
        figure.colorbar(image, ax=axis, label="samples")
        return figure
    if capability in {"sound_classification", "bidirectional_sound_classification"}:
        figure, axis = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
        if capability == "sound_classification":
            measured = payload["frequencies"].detach().cpu().numpy()
            predicted = SOUND_PROTOTYPE_FREQUENCIES[payload["result"].class_indices].detach().cpu().numpy()
        else:
            measured = payload["input_frequencies"].detach().cpu().numpy()
            predicted = payload["reconstructed_frequencies"].detach().cpu().numpy()
        axis.plot(measured, "o", label="measured dominant frequency")
        axis.plot(predicted, "x", label="observed/reconstructed prototype")
        axis.set(title=capability.replace("_", " ").title(), xlabel="sample", ylabel="frequency (Hz)")
        axis.legend()
        axis.grid(alpha=0.25)
        return figure
    if capability == "color_cloning":
        source = payload["image"].detach().cpu().numpy()
        clone = payload["result"].clone.detach().cpu().numpy()
        figure, axes = plt.subplots(1, 3, figsize=(9.0, 3.2), constrained_layout=True)
        axes[0].imshow(np.clip(source, 0.0, 1.0))
        axes[0].set_title("input")
        axes[1].imshow(np.clip(clone, 0.0, 1.0))
        axes[1].set_title("TNE clone")
        axes[2].imshow(np.abs(source - clone), cmap="magma")
        axes[2].set_title("absolute residual")
        for axis in axes:
            axis.axis("off")
        return figure
    source = payload["waveform"].detach().cpu().numpy()
    clone = payload["result"].clone.detach().cpu().numpy()
    figure, axis = plt.subplots(figsize=(8.0, 3.6), constrained_layout=True)
    extent = min(900, source.size)
    axis.plot(source[:extent], label="input", linewidth=1.2)
    axis.plot(clone[:extent], "--", label="TNE clone", linewidth=1.0)
    axis.set(title="Sound cloning waveform closure", xlabel="sample", ylabel="amplitude")
    axis.legend()
    axis.grid(alpha=0.25)
    return figure


def _animation_values(capability: str, evaluation: CapabilityEvaluation) -> np.ndarray:
    payload = evaluation.payload
    if "classification" in capability:
        result = payload["result"].forward if capability.startswith("bidirectional") else payload["result"]
        return result.confidence.detach().cpu().numpy()
    residual = max(evaluation.metrics["rmse"], 1e-10)
    return np.geomspace(1.0, residual, num=14)


def _save_animation(path: Path, capability: str, values: np.ndarray) -> Path:
    figure, axis = plt.subplots(figsize=(6.0, 3.4), constrained_layout=True)
    line, = axis.plot([], [], "o-", color="#4c72b0")
    axis.set_xlim(0, max(1, len(values) - 1))
    lower = min(0.0, float(np.min(values)) * 0.9)
    upper = max(1.0, float(np.max(values)) * 1.1)
    axis.set_ylim(lower, upper)
    axis.set(title=f"{capability.replace('_', ' ').title()} trace", xlabel="step", ylabel="confidence / residual")
    axis.grid(alpha=0.25)

    def update(frame: int):
        x = np.arange(frame + 1)
        line.set_data(x, values[: frame + 1])
        return (line,)

    movie = animation.FuncAnimation(figure, update, frames=len(values), interval=180, blit=True)
    movie.save(path, writer=animation.PillowWriter(fps=5))
    plt.close(figure)
    return path


def _write_wav(path: Path, waveform: torch.Tensor, *, sample_rate: int = 8000) -> Path:
    samples = torch.clamp(waveform.detach().cpu(), -1.0, 1.0).numpy()
    pcm = np.round(samples * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())
    return path


def _audio_files(capability: str, output: Path, evaluation: CapabilityEvaluation) -> list[Path]:
    payload = evaluation.payload
    if capability == "sound_classification":
        return [_write_wav(output / "sound_classification_sample.wav", payload["waveforms"][0])]
    if capability == "bidirectional_sound_classification":
        return [
            _write_wav(output / "bidirectional_sound_input.wav", payload["waveforms"][0]),
            _write_wav(output / "bidirectional_sound_reconstruction.wav", payload["result"].reconstructed_modality[0]),
        ]
    if capability == "sound_cloning":
        return [
            _write_wav(output / "sound_cloning_input.wav", payload["waveform"]),
            _write_wav(output / "sound_cloning_clone.wav", payload["result"].clone),
        ]
    return []


def run_capability(
    capability: str,
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = False,
    producer_architecture: str | None = None,
    producer_module: str | None = None,
) -> dict[str, Any]:
    """Run one capability and keep every generated artifact beside its producer."""

    if capability not in CAPABILITIES:
        raise ValueError(f"Unknown capability {capability!r}; expected one of {CAPABILITIES}")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    evaluation = _evaluate(capability, seed=seed, simulation=simulation)
    mode = "simulation" if simulation else "test"
    stem = f"{capability}_{mode}"
    metrics_path = save_csv(output / f"{stem}_results.csv", evaluation.rows)
    figure_handle = _plot_evaluation(capability, evaluation)
    figure_path = save_figure(figure_handle, output / f"{stem}_figure.png", dpi=160)
    plt.close(figure_handle)
    generated = [metrics_path, figure_path]
    if simulation:
        generated.append(_save_animation(output / f"{stem}_animation.gif", capability, _animation_values(capability, evaluation)))
        generated.extend(_audio_files(capability, output, evaluation))
    parameters = {
        "capability": capability,
        "mode": mode,
        "seed": seed,
        "synthetic_fixture": True,
        "producer_architecture": producer_architecture,
    }
    command_module = producer_module or (
        f"the_nothingness_effect.artificial_intelligence.{capability}.{mode}."
        f"{'run_simulation' if simulation else 'test_capability'}"
    )
    manifest_path = output / f"{stem}_manifest.json"
    manifest = write_metadata(
        manifest_path,
        {
            "capability_id": capability,
            "producer_architecture": producer_architecture,
            "intended_output_group": capability.replace("_", " "),
            "appendix_filename": APPENDIX,
            "appendix_source_sha256": APPENDIX_SHA256,
            "related_theorem_complex_ids": list(RELATED_COMPLEX_IDS[capability]),
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "numeric_tolerances": {"absolute": 1e-6},
            "residual_vector": evaluation.residuals,
            "closure_status": evaluation.closure_status,
            "metrics": evaluation.metrics,
            "source_status": "synthetic_deterministic_fixture",
            "generated_files": [path.name for path in generated] + [manifest_path.name],
            "regeneration_command": f"python -m {command_module}",
            "approximation_metadata": {
                "bidirectional_reconstruction": "class prototype, not exact source recovery",
                "classification_scope": "bounded synthetic color patches and tonal waveforms",
            },
        },
    )
    if "classification" in capability:
        if evaluation.metrics["accuracy"] < 0.95:
            raise AssertionError(f"{capability} accuracy fell below 0.95")
        if capability.startswith("bidirectional") and evaluation.metrics["roundtrip_accuracy"] < 1.0:
            raise AssertionError(f"{capability} failed label roundtrip closure")
    else:
        if evaluation.metrics["rmse"] > 1e-5:
            raise AssertionError(f"{capability} reconstruction residual exceeded tolerance")
    return {
        "metrics": metrics_path,
        "figure": figure_path,
        "animation": next((path for path in generated if path.suffix == ".gif"), None),
        "manifest": manifest,
        "generated_files": tuple(generated) + (manifest,),
        "evaluation": evaluation,
    }


def run_capability_test(capability: str, output_dir: str | Path, *, seed: int = 0) -> dict[str, Any]:
    return run_capability(capability, output_dir, seed=seed, simulation=False)


def run_capability_simulation(capability: str, output_dir: str | Path, *, seed: int = 0) -> dict[str, Any]:
    return run_capability(capability, output_dir, seed=seed, simulation=True)
