"""SOInet-coupled artifact generation for the six TNE AI capabilities."""

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

from the_nothingness_effect._runtime.artifacts.io import (
    save_csv,
    save_figure,
    write_metadata,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    git_commit,
    parameter_hash,
)
from the_nothingness_effect.artificial_intelligence.qenn.contracts import (
    APPENDIX,
    APPENDIX_SHA256,
)
from the_nothingness_effect.artificial_intelligence.shared.soinet_capability_runtime import (
    evaluate_capability_with_soinet,
)


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
    checkpoint: dict[str, Any]


def _evaluate(capability: str, *, seed: int, simulation: bool) -> CapabilityEvaluation:
    result = evaluate_capability_with_soinet(
        capability, seed=seed, simulation=simulation
    )
    return CapabilityEvaluation(
        rows=result.rows,
        metrics=result.metrics,
        residuals=result.residuals,
        closure_status=result.closure_status,
        payload=result.payload,
        checkpoint=result.checkpoint,
    )


def _confusion_matrix(
    targets: torch.Tensor, predictions: torch.Tensor, size: int
) -> np.ndarray:
    matrix = np.zeros((size, size), dtype=int)
    for truth, prediction in zip(
        targets.detach().cpu().tolist(),
        predictions.detach().cpu().tolist(),
        strict=True,
    ):
        matrix[int(truth), int(prediction)] += 1
    return matrix


def _plot_evaluation(
    capability: str, evaluation: CapabilityEvaluation
) -> plt.Figure:
    payload = evaluation.payload
    if "classification" in capability:
        labels = tuple(payload["labels"])
        matrix = _confusion_matrix(
            payload["targets"], payload["predictions"], len(labels)
        )
        figure, axes = plt.subplots(
            1, 2, figsize=(11.0, 4.8), constrained_layout=True
        )
        image = axes[0].imshow(matrix, cmap="Blues")
        axes[0].set(
            title=f"{capability.replace('_', ' ').title()} — SOInet",
            xlabel="Predicted",
            ylabel="True",
            xticks=range(len(labels)),
            yticks=range(len(labels)),
        )
        axes[0].set_xticklabels(labels, rotation=35, ha="right")
        axes[0].set_yticklabels(labels)
        for row in range(matrix.shape[0]):
            for column in range(matrix.shape[1]):
                axes[0].text(
                    column,
                    row,
                    int(matrix[row, column]),
                    ha="center",
                    va="center",
                )
        figure.colorbar(image, ax=axes[0], label="held-out samples")
        probability = axes[1].imshow(
            payload["probabilities"].detach().cpu().numpy(),
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
            aspect="auto",
        )
        axes[1].set(
            title="SOInet held-out probabilities",
            xlabel="class",
            ylabel="test sample",
        )
        figure.colorbar(probability, ax=axes[1], label="probability")
        return figure

    source = payload["source"].detach().cpu().numpy()
    clone = payload["clone"].detach().cpu().numpy()
    if capability == "color_cloning":
        figure, axes = plt.subplots(
            1, 3, figsize=(11.0, 3.6), constrained_layout=True
        )
        sample_index = np.arange(len(source))
        for channel in range(source.shape[1]):
            axes[0].plot(sample_index, source[:, channel], marker="o")
            axes[1].plot(sample_index, clone[:, channel], marker="o")
        axes[0].set(title="Held-out RGB targets", xlabel="sample", ylabel="value")
        axes[1].set(title="SOInet RGB clone", xlabel="sample", ylabel="value")
        axes[2].imshow(np.abs(source - clone), cmap="magma", aspect="auto")
        axes[2].set(title="Absolute residual", xlabel="channel", ylabel="sample")
        return figure
    figure, axis = plt.subplots(figsize=(8.0, 3.8), constrained_layout=True)
    order = np.argsort(payload["samples"][:, 0].detach().cpu().numpy())
    axis.plot(source[order, 0], "o-", label="held-out amplitude")
    axis.plot(clone[order, 0], "x--", label="SOInet clone")
    axis.set(
        title="SOInet sound cloning on held-out coordinates",
        xlabel="ordered held-out coordinate",
        ylabel="amplitude",
    )
    axis.legend()
    axis.grid(alpha=0.25)
    return figure


def _animation_values(
    capability: str, evaluation: CapabilityEvaluation
) -> np.ndarray:
    payload = evaluation.payload
    if "classification" in capability:
        return (
            payload["probabilities"].max(dim=-1).values.detach().cpu().numpy()
        )
    residual = (
        payload["clone"] - payload["source"]
    ).abs().mean(dim=-1)
    return residual.detach().cpu().numpy()


def _save_animation(
    path: Path, capability: str, values: np.ndarray
) -> Path:
    values = np.asarray(values, dtype=float).reshape(-1)
    if values.size < 10:
        values = np.interp(
            np.linspace(0.0, 1.0, 10),
            np.linspace(0.0, 1.0, max(values.size, 2)),
            np.pad(values, (0, max(0, 2 - values.size)), mode="edge")[: max(values.size, 2)],
        )
    figure, axis = plt.subplots(figsize=(6.0, 3.4), constrained_layout=True)
    (line,) = axis.plot([], [], "o-")
    axis.set_xlim(0, max(1, len(values) - 1))
    lower = min(0.0, float(np.min(values)) * 0.9)
    upper = max(1.0, float(np.max(values)) * 1.1)
    axis.set_ylim(lower, upper)
    axis.set(
        title=f"{capability.replace('_', ' ').title()} — SOInet trace",
        xlabel="held-out sample",
        ylabel="confidence / absolute residual",
    )
    axis.grid(alpha=0.25)

    def update(frame: int):
        x = np.arange(frame + 1)
        line.set_data(x, values[: frame + 1])
        return (line,)

    movie = animation.FuncAnimation(
        figure, update, frames=len(values), interval=180, blit=True
    )
    movie.save(path, writer=animation.PillowWriter(fps=5))
    plt.close(figure)
    return path


def _write_wav(
    path: Path, waveform: torch.Tensor, *, sample_rate: int = 8000
) -> Path:
    samples = torch.clamp(waveform.detach().cpu().reshape(-1), -1.0, 1.0)
    if samples.numel() < 2048:
        x = torch.linspace(0.0, 1.0, samples.numel())
        target = torch.linspace(0.0, 1.0, 2048)
        samples = torch.from_numpy(
            np.interp(target.numpy(), x.numpy(), samples.numpy())
        )
    pcm = np.round(samples.numpy() * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())
    return path


def _audio_files(
    capability: str, output: Path, evaluation: CapabilityEvaluation
) -> list[Path]:
    payload = evaluation.payload
    if capability == "sound_classification":
        return [
            _write_wav(
                output / "sound_classification_sample.wav", payload["samples"][0]
            )
        ]
    if capability == "bidirectional_sound_classification":
        return [
            _write_wav(
                output / "bidirectional_sound_input.wav", payload["samples"][0]
            ),
            _write_wav(
                output / "bidirectional_sound_reconstruction.wav",
                payload["reconstructed_modality"][0],
            ),
        ]
    if capability == "sound_cloning":
        order = torch.argsort(payload["samples"][:, 0])
        return [
            _write_wav(
                output / "sound_cloning_input.wav", payload["source"][order]
            ),
            _write_wav(
                output / "sound_cloning_clone.wav", payload["clone"][order]
            ),
        ]
    return []


def _split_rows(evaluation: CapabilityEvaluation) -> list[dict[str, Any]]:
    metrics = evaluation.metrics
    rows = []
    for split in ("train", "validation", "test"):
        prefix = "" if split == "test" else f"{split}_"
        values = {
            name: value
            for name, value in metrics.items()
            if name.startswith(prefix) and (
                prefix == "" or name in {f"{prefix}accuracy", f"{prefix}rmse"}
            )
        }
        if not values:
            if split == "test":
                values = {
                    name: metrics[name]
                    for name in ("accuracy", "rmse", "test_loss", "mae", "snr_db")
                    if name in metrics
                }
            else:
                continue
        rows.append({"split": split, **values})
    return rows


def run_capability(
    capability: str,
    output_dir: str | Path,
    *,
    seed: int = 0,
    simulation: bool = False,
    producer_architecture: str | None = None,
    producer_module: str | None = None,
) -> dict[str, Any]:
    """Run one capability with metrics produced by the real SOInet chain."""

    if capability not in CAPABILITIES:
        raise ValueError(f"Unknown capability {capability!r}; expected one of {CAPABILITIES}")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    evaluation = _evaluate(capability, seed=seed, simulation=simulation)
    if evaluation.payload.get("metric_producer") != "SOInet":
        raise AssertionError("capability metrics are not coupled to SOInet")
    if not all(math.isfinite(float(value)) for value in evaluation.metrics.values()):
        raise AssertionError("capability metrics contain NaN or infinity")
    mode = "simulation" if simulation else "test"
    stem = f"{capability}_{mode}"
    metrics_path = save_csv(output / f"{stem}_results.csv", evaluation.rows)
    split_path = save_csv(output / f"{stem}_splits.csv", _split_rows(evaluation))
    figure_handle = _plot_evaluation(capability, evaluation)
    figure_path = save_figure(
        figure_handle, output / f"{stem}_figure.png", dpi=160
    )
    plt.close(figure_handle)
    checkpoint_path = output / f"{stem}_checkpoint.pt"
    torch.save(evaluation.checkpoint, checkpoint_path)
    generated = [metrics_path, split_path, figure_path, checkpoint_path]
    if simulation:
        generated.append(
            _save_animation(
                output / f"{stem}_animation.gif",
                capability,
                _animation_values(capability, evaluation),
            )
        )
        generated.extend(_audio_files(capability, output, evaluation))
    parameters = {
        "capability": capability,
        "mode": mode,
        "seed": seed,
        "synthetic_fixture": True,
        "producer_architecture": producer_architecture,
        "metric_producer": "SOInet",
        "split_policy": "disjoint_train_validation_test",
        "checkpoint_format": 1,
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
            "metric_producer": "SOInet",
            "architecture_coupled_metrics": True,
            "intended_output_group": capability.replace("_", " "),
            "appendix_filename": APPENDIX,
            "appendix_source_sha256": APPENDIX_SHA256,
            "related_theorem_complex_ids": list(RELATED_COMPLEX_IDS[capability]),
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "numeric_tolerances": {"finite_metrics": True},
            "residual_vector": evaluation.residuals,
            "closure_status": evaluation.closure_status,
            "metrics": evaluation.metrics,
            "source_status": "soinet_architecture_coupled_train_validation_test",
            "generated_files": [path.name for path in generated] + [manifest_path.name],
            "regeneration_command": f"python -m {command_module}",
            "approximation_metadata": {
                "classification_scope": "bounded synthetic held-out color and tone fixtures",
                "cloning_scope": "held-out coordinate regression through SOInet meta-states",
                "bidirectional_decoder": "probability-weighted finite modality reconstruction",
            },
            "claim_boundary": (
                "finite synthetic train/validation/test evidence; not a formal proof "
                "or a real-world generalization claim"
            ),
        },
    )
    return {
        "metrics": metrics_path,
        "splits": split_path,
        "figure": figure_path,
        "checkpoint": checkpoint_path,
        "animation": next((path for path in generated if path.suffix == ".gif"), None),
        "manifest": manifest,
        "generated_files": tuple(generated) + (manifest,),
        "evaluation": evaluation,
    }


def run_capability_test(
    capability: str, output_dir: str | Path, *, seed: int = 0
) -> dict[str, Any]:
    return run_capability(capability, output_dir, seed=seed, simulation=False)


def run_capability_simulation(
    capability: str, output_dir: str | Path, *, seed: int = 0
) -> dict[str, Any]:
    return run_capability(capability, output_dir, seed=seed, simulation=True)
