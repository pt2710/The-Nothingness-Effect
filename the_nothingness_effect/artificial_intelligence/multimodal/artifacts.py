"""Rich producer-local training, validation and evaluation evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import torch

from the_nothingness_effect._runtime.artifacts.io import (
    ensure_dir,
    save_csv,
    save_figure,
    write_metadata,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import (
    git_commit,
    parameter_hash,
)

from .data import make_synthetic_multimodal_dataset
from .evaluation import evaluate_multimodal_model, evaluate_source_removals
from .model import TNETrainableMultimodalModel
from .network_artifacts import generate_multimodal_network_artifacts
from .training import MultimodalTrainingRun, train_multimodal_model


START_COMMIT = "b97a2da379ff9fc503c4c43185030674f887b85c"


def _save_plot(output: Path, name: str, draw: Callable[[Any], None]) -> Path:
    figure, axis = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    draw(axis)
    path = save_figure(figure, output / name, dpi=160)
    plt.close(figure)
    return path


def _history_arrays(run: MultimodalTrainingRun) -> dict[str, np.ndarray]:
    return {
        "epoch": np.array([item.epoch for item in run.history]),
        "train_total": np.array([item.train_total_loss for item in run.history]),
        "train_task": np.array([item.train_task_loss for item in run.history]),
        "train_reconstruction": np.array(
            [item.train_reconstruction_loss for item in run.history]
        ),
        "train_energy": np.array([item.train_energy_loss for item in run.history]),
        "validation_loss": np.array([item.validation_loss for item in run.history]),
        "train_accuracy": np.array([item.train_accuracy for item in run.history]),
        "validation_accuracy": np.array(
            [item.validation_accuracy for item in run.history]
        ),
        "gradient_norm": np.array([item.gradient_norm for item in run.history]),
        "weights": np.array([item.modality_weights for item in run.history]),
        "confusion": np.array([item.confusion_matrix for item in run.history]),
        "latent": np.array([item.latent_snapshot for item in run.history]),
        "axis": np.array([item.axis_snapshot for item in run.history]),
        "cluster_count": np.array([item.cluster_count for item in run.history]),
        "local_energy": np.array([item.local_free_energy for item in run.history]),
        "global_energy": np.array([item.global_free_energy for item in run.history]),
        "K_D": np.array([item.K_D for item in run.history]),
        "learning_rate": np.array([item.learning_rate for item in run.history]),
        "validation_objective": np.array(
            [item.validation_objective for item in run.history]
        ),
        "K_D_improvement": np.array(
            [item.K_D_selection_improvement for item in run.history]
        ),
    }


def _pca_projection(latent_history: np.ndarray) -> np.ndarray:
    epochs, samples, features = latent_history.shape
    flattened = latent_history.reshape(epochs * samples, features)
    centered = flattened - flattened.mean(axis=0, keepdims=True)
    _, _, vectors = np.linalg.svd(centered, full_matrices=False)
    basis = vectors[:2].T
    return (centered @ basis).reshape(epochs, samples, 2)


def _write_tables(
    output: Path,
    run: MultimodalTrainingRun,
    evaluation: Any,
    ablations: list[dict[str, Any]],
    names: tuple[str, ...],
) -> list[Path]:
    history = save_csv(
        output / "training_history.csv",
        [
            {
                "epoch": item.epoch,
                "train_total_loss": item.train_total_loss,
                "train_task_loss": item.train_task_loss,
                "train_reconstruction_loss": item.train_reconstruction_loss,
                "train_energy_loss": item.train_energy_loss,
                "train_closure_penalty": item.train_closure_penalty,
                "train_accuracy": item.train_accuracy,
                "validation_loss": item.validation_loss,
                "validation_accuracy": item.validation_accuracy,
                "gradient_norm": item.gradient_norm,
                "K_D": item.K_D,
                "learning_rate": item.learning_rate,
                "validation_objective": item.validation_objective,
                "K_D_selection_improvement": item.K_D_selection_improvement,
                **{
                    f"weight_{name}": item.modality_weights[index]
                    for index, name in enumerate(names)
                },
            }
            for item in run.history
        ],
    )
    metrics = save_csv(
        output / "test_evaluation_metrics.csv",
        [{"metric": name, "value": value} for name, value in evaluation.metrics.items()],
    )
    residuals = save_csv(
        output / "tne_residuals.csv",
        [{"residual": name, "value": value} for name, value in evaluation.residuals.items()],
    )
    ablation_table = save_csv(output / "source_removal_ablation.csv", ablations)
    confusion = save_csv(
        output / "test_confusion_matrix.csv",
        [
            {
                "true_class": row,
                **{
                    f"predicted_{column}": int(evaluation.confusion_matrix[row, column])
                    for column in range(evaluation.confusion_matrix.shape[1])
                },
            }
            for row in range(evaluation.confusion_matrix.shape[0])
        ],
    )
    similarity = save_csv(
        output / "modality_similarity_matrix.csv",
        [
            {
                "modality": names[row],
                **{
                    names[column]: float(evaluation.modality_similarity[row, column])
                    for column in range(len(names))
                },
            }
            for row in range(len(names))
        ],
    )
    reconstruction = save_csv(
        output / "modality_reconstruction_metrics.csv",
        [
            {"modality": name, "token_rmse": value}
            for name, value in evaluation.reconstruction_rmse.items()
        ],
    )
    kd_optimization = save_csv(
        output / "dynamic_kd_optimization.csv",
        [
            {
                "epoch": probe.epoch,
                "K_D": probe.K_D,
                "objective": probe.objective,
                "cross_entropy": probe.cross_entropy,
                "reconstruction_rmse": probe.reconstruction_rmse,
                "brier_score": probe.brier_score,
                "calibration_error": probe.calibration_error,
                "bounded_closure_penalty": probe.bounded_closure_penalty,
                "status": probe.status,
                "obstruction": probe.obstruction,
            }
            for probe in run.kd_probes
        ],
    )
    return [
        history,
        metrics,
        residuals,
        ablation_table,
        confusion,
        similarity,
        reconstruction,
        kd_optimization,
    ]


def _static_figures(
    output: Path,
    arrays: dict[str, np.ndarray],
    evaluation: Any,
    ablations: list[dict[str, Any]],
    names: tuple[str, ...],
    evaluation_labels: torch.Tensor,
    latent_labels: torch.Tensor,
    run: MultimodalTrainingRun,
) -> list[Path]:
    figures: list[Path] = []
    figures.append(
        _save_plot(
            output,
            "training_loss_curves.png",
            lambda axis: (
                axis.plot(arrays["epoch"], arrays["train_total"], label="train total"),
                axis.plot(arrays["epoch"], arrays["train_task"], label="train task"),
                axis.plot(arrays["epoch"], arrays["validation_loss"], label="validation"),
                axis.set(title="Multimodal training and validation losses", xlabel="epoch", ylabel="loss"),
                axis.legend(),
            ),
        )
    )
    figures.append(
        _save_plot(
            output,
            "training_accuracy_curve.png",
            lambda axis: (
                axis.plot(arrays["epoch"], arrays["train_accuracy"], marker="o", label="train"),
                axis.plot(arrays["epoch"], arrays["validation_accuracy"], marker="s", label="validation"),
                axis.set(title="Classification accuracy", xlabel="epoch", ylabel="accuracy", ylim=(0, 1.05)),
                axis.legend(),
            ),
        )
    )
    figures.append(
        _save_plot(
            output,
            "gradient_norm_curve.png",
            lambda axis: (
                axis.plot(arrays["epoch"], arrays["gradient_norm"], color="#e45756", marker="o"),
                axis.set(title="Gradient norm and clipping boundary", xlabel="epoch", ylabel="L2 norm"),
                axis.axhline(5.0, color="black", linestyle="--", label="clip boundary"),
                axis.legend(),
            ),
        )
    )

    def draw_weights(axis: Any) -> None:
        for index, name in enumerate(names):
            axis.plot(arrays["epoch"], arrays["weights"][:, index], marker="o", label=name)
        axis.set(title="Elastic Dubler modality weights", xlabel="epoch", ylabel="normalized weight", ylim=(0, 1))
        axis.legend()

    figures.append(_save_plot(output, "modality_weight_trajectories.png", draw_weights))

    def draw_confusion(axis: Any) -> None:
        image = axis.imshow(evaluation.confusion_matrix.numpy(), cmap="Blues")
        for row in range(evaluation.confusion_matrix.shape[0]):
            for column in range(evaluation.confusion_matrix.shape[1]):
                axis.text(column, row, int(evaluation.confusion_matrix[row, column]), ha="center", va="center")
        axis.set(title="Held-out confusion matrix", xlabel="predicted", ylabel="true")
        axis.figure.colorbar(image, ax=axis)

    figures.append(_save_plot(output, "test_confusion_matrix.png", draw_confusion))
    probabilities = evaluation.output.observation.detach().cpu()
    confidence, predictions = probabilities.max(dim=-1)
    bin_edges = torch.linspace(0, 1, 6)
    bin_confidence: list[float] = []
    bin_accuracy: list[float] = []
    for lower, upper in zip(bin_edges[:-1], bin_edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if bool(mask.any()):
            bin_confidence.append(float(confidence[mask].mean()))
            bin_accuracy.append(
                float((predictions[mask] == evaluation_labels[mask]).float().mean())
            )
    figures.append(
        _save_plot(
            output,
            "calibration_reliability.png",
            lambda axis: (
                axis.plot([0, 1], [0, 1], linestyle="--", color="black", label="ideal"),
                axis.plot(bin_confidence, bin_accuracy, marker="o", label="model"),
                axis.set(title="Reliability diagram", xlabel="confidence", ylabel="accuracy", xlim=(0, 1), ylim=(0, 1)),
                axis.legend(),
            ),
        )
    )
    projection = _pca_projection(arrays["latent"])[-1]

    def draw_latent(axis: Any) -> None:
        scatter = axis.scatter(
            projection[:, 0],
            projection[:, 1],
            c=latent_labels.numpy(),
            cmap="tab10",
            s=55,
        )
        axis.set(title="Held-out latent geometry (PCA)", xlabel="PC1", ylabel="PC2")
        axis.figure.colorbar(scatter, ax=axis, label="class")

    figures.append(_save_plot(output, "latent_space_pca.png", draw_latent))

    def heatmap(axis: Any, matrix: np.ndarray, title: str, color_map: str) -> None:
        image = axis.imshow(matrix, cmap=color_map)
        axis.set(xticks=range(len(names)), yticks=range(len(names)), xticklabels=names, yticklabels=names, title=title)
        axis.figure.colorbar(image, ax=axis)

    figures.append(
        _save_plot(
            output,
            "modality_similarity_heatmap.png",
            lambda axis: heatmap(axis, evaluation.modality_similarity.numpy(), "Cross-modal cosine similarity", "viridis"),
        )
    )
    ratio = evaluation.output.backbone_output.elastic_dubler_state.ratio.mean(dim=0).detach().cpu().numpy()
    figures.append(
        _save_plot(
            output,
            "elastic_dubler_ratio_heatmap.png",
            lambda axis: heatmap(axis, ratio, "Exact Elastic Dubler ratios R_AB", "magma"),
        )
    )
    figures.append(
        _save_plot(
            output,
            "reconstruction_rmse.png",
            lambda axis: (
                axis.bar(list(evaluation.reconstruction_rmse), list(evaluation.reconstruction_rmse.values()), color="#72b7b2"),
                axis.set(title="Shared-token reconstruction error", ylabel="RMSE"),
            ),
        )
    )
    ranked = sorted(evaluation.residuals.items(), key=lambda item: abs(item[1]), reverse=True)[:16]
    figures.append(
        _save_plot(
            output,
            "residual_spectrum.png",
            lambda axis: (
                axis.barh([name.replace("backbone::", "")[:44] for name, _ in ranked][::-1], [max(abs(value), 1e-12) for _, value in ranked][::-1]),
                axis.set_xscale("log"),
                axis.set(title="Largest TNE residuals", xlabel="absolute residual (log scale)"),
            ),
        )
    )
    figures.append(
        _save_plot(
            output,
            "source_removal_ablation.png",
            lambda axis: (
                axis.bar([row["variant"] for row in ablations], [row["cross_entropy"] for row in ablations], color="#f58518"),
                axis.tick_params(axis="x", rotation=20),
                axis.set(title="Observation/Elastic-Dubler source removal", ylabel="held-out cross entropy"),
            ),
        )
    )
    figures.append(
        _save_plot(
            output,
            "dynamic_kd_trajectory.png",
            lambda axis: (
                axis.plot(
                    arrays["epoch"], arrays["K_D"], marker="o", color="#7a5195"
                ),
                axis.set(
                    title="Validation-selected dynamic K_D trajectory",
                    xlabel="epoch",
                    ylabel="exact positive K_D",
                ),
                axis.set_yscale("log"),
            ),
        )
    )

    valid_probes = tuple(
        probe for probe in run.kd_probes if probe.objective is not None
    )

    def draw_kd_landscape(axis: Any) -> None:
        if not valid_probes:
            axis.text(0.5, 0.5, "No valid K_D probes", ha="center", va="center")
            return
        scatter = axis.scatter(
            [probe.K_D for probe in valid_probes],
            [float(probe.objective) for probe in valid_probes],
            c=[probe.epoch for probe in valid_probes],
            cmap="viridis",
            s=65,
            edgecolors="black",
            linewidths=0.35,
        )
        axis.set_xscale("log")
        axis.set(
            title="K_D validation-objective landscape",
            xlabel="candidate K_D",
            ylabel="composite validation objective",
        )
        axis.figure.colorbar(scatter, ax=axis, label="epoch")

    figures.append(_save_plot(output, "dynamic_kd_validation_landscape.png", draw_kd_landscape))

    def draw_hyperparameters(axis: Any) -> None:
        kd_scale = arrays["K_D"] / max(float(arrays["K_D"][0]), 1e-12)
        lr_scale = arrays["learning_rate"] / max(
            float(arrays["learning_rate"][0]), 1e-12
        )
        axis.plot(arrays["epoch"], kd_scale, marker="o", label="K_D / initial")
        axis.plot(
            arrays["epoch"], lr_scale, marker="s", label="learning rate / initial"
        )
        axis.plot(
            arrays["epoch"],
            arrays["validation_objective"] / max(
                float(arrays["validation_objective"][0]), 1e-12
            ),
            marker="^",
            label="validation objective / initial",
        )
        axis.set(
            title="Dynamic hyperparameter and objective response",
            xlabel="epoch",
            ylabel="relative value",
        )
        axis.legend()

    figures.append(_save_plot(output, "hyperparameter_optimization_response.png", draw_hyperparameters))
    return figures


def _save_animation(
    output: Path,
    name: str,
    frames: int,
    update: Callable[[int, Any], None],
) -> Path:
    figure, axis = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)

    def render(frame: int):
        axis.clear()
        update(frame, axis)
        return ()

    movie = animation.FuncAnimation(figure, render, frames=frames, interval=450, blit=False)
    path = output / name
    movie.save(path, writer=animation.PillowWriter(fps=2))
    plt.close(figure)
    return path


def _animations(
    output: Path,
    arrays: dict[str, np.ndarray],
    evaluation: Any,
    names: tuple[str, ...],
    latent_labels: torch.Tensor,
) -> list[Path]:
    frames = len(arrays["epoch"])
    projection = _pca_projection(arrays["latent"])
    animations = [
        _save_animation(
            output,
            "training_loss_evolution.gif",
            frames,
            lambda frame, axis: (
                axis.plot(arrays["epoch"][: frame + 1], arrays["train_total"][: frame + 1], label="train"),
                axis.plot(arrays["epoch"][: frame + 1], arrays["validation_loss"][: frame + 1], label="validation"),
                axis.set(title=f"Loss evolution: epoch {frame}", xlabel="epoch", ylabel="loss"),
                axis.legend(),
            ),
        ),
        _save_animation(
            output,
            "latent_space_evolution.gif",
            frames,
            lambda frame, axis: (
                axis.scatter(
                    projection[frame, :, 0],
                    projection[frame, :, 1],
                    c=latent_labels.numpy(),
                    cmap="tab10",
                    s=45,
                ),
                axis.set(title=f"Latent geometry: epoch {frame}", xlabel="PC1", ylabel="PC2"),
            ),
        ),
        _save_animation(
            output,
            "modality_weight_evolution.gif",
            frames,
            lambda frame, axis: (
                axis.bar(names, arrays["weights"][frame], color="#4c78a8"),
                axis.set(title=f"Elastic Dubler weights: epoch {frame}", ylabel="normalized weight", ylim=(0, 1)),
            ),
        ),
        _save_animation(
            output,
            "confusion_matrix_evolution.gif",
            frames,
            lambda frame, axis: (
                axis.imshow(arrays["confusion"][frame], cmap="Blues", vmin=0),
                axis.set(title=f"Validation confusion: epoch {frame}", xlabel="predicted", ylabel="true"),
            ),
        ),
    ]
    animations.append(
        _save_animation(
            output,
            "dynamic_kd_optimization.gif",
            frames,
            lambda frame, axis: (
                axis.plot(
                    arrays["epoch"][: frame + 1],
                    arrays["K_D"][: frame + 1],
                    color="#7a5195",
                    marker="o",
                    label="selected K_D",
                ),
                axis.set_yscale("log"),
                axis.set(
                    title=f"Dynamic K_D optimization — epoch {frame}",
                    xlabel="epoch",
                    ylabel="exact positive K_D",
                ),
                axis.legend(),
            ),
        )
    )
    tokens = evaluation.output.backbone_output.modality_tokens.detach().cpu()
    reconstruction = evaluation.output.reconstructed_fused_tokens.detach().cpu()
    sample_frames = min(tokens.shape[0], 8)

    def draw_reconstruction(frame: int, axis: Any) -> None:
        axis.plot(reconstruction[frame].numpy(), color="black", linewidth=2.5, label="shared reconstruction")
        for index, name in enumerate(names):
            axis.plot(tokens[frame, index].numpy(), marker="o", alpha=0.7, label=name)
        axis.set(title=f"Cross-modal token reconstruction: sample {frame}", xlabel="token coordinate", ylabel="magnitude")
        axis.legend(fontsize=8)

    animations.append(
        _save_animation(
            output,
            "cross_modal_reconstruction_evolution.gif",
            sample_frames,
            draw_reconstruction,
        )
    )
    return animations


def run_multimodal_pipeline_artifacts(
    output_dir: str | Path,
    *,
    seed: int = 0,
    epochs: int = 6,
    simulation: bool = False,
) -> dict[str, Any]:
    output = ensure_dir(output_dir)
    torch.manual_seed(seed)
    dataset = make_synthetic_multimodal_dataset(samples_per_class=8, seed=seed)
    model = TNETrainableMultimodalModel()
    run = train_multimodal_model(
        model,
        dataset.train,
        dataset.validation,
        epochs=epochs,
        seed=seed,
        optimize_K_D=True,
        adaptive_learning_rate=True,
    )
    evaluation = evaluate_multimodal_model(model, dataset.test)
    ablations = evaluate_source_removals(model, dataset.test)
    names = evaluation.output.backbone_output.modality_names
    arrays = _history_arrays(run)
    tables = _write_tables(output, run, evaluation, ablations, names)
    figures = _static_figures(
        output,
        arrays,
        evaluation,
        ablations,
        names,
        dataset.test.labels,
        dataset.train.labels,
        run,
    )
    movies = _animations(output, arrays, evaluation, names, dataset.train.labels)
    network = generate_multimodal_network_artifacts(
        model, run, evaluation, output, seed=seed, simulation=simulation
    )
    tables.extend(network["tables"])
    figures.extend(network["figures"])
    movies.extend(network["animations"])
    generated = [path.name for path in (*tables, *figures, *movies)]
    generated.append(network["manifest"].name)
    parameters = {
        "architecture": "TNE Trainable Multimodal SOInet",
        "seed": seed,
        "epochs": epochs,
        "simulation": simulation,
        "modalities": list(names),
        "classes": list(dataset.class_names),
        "synthetic_samples_per_class": 8,
        "dynamic_K_D": {
            "enabled": True,
            "initial": (
                run.kd_selections[0].previous_K_D if run.kd_selections else 1.0
            ),
            "final": run.history[-1].K_D if run.history else 1.0,
            "probe_count": len(run.kd_probes),
            "selection_count": len(run.kd_selections),
            "total_probe_improvement": sum(
                selection.improvement for selection in run.kd_selections
            ),
        },
        "adaptive_learning_rate": True,
    }
    manifest = write_metadata(
        output / "multimodal_pipeline_manifest.json",
        {
            "architecture": parameters["architecture"],
            "repository_start_commit": START_COMMIT,
            "repository_result_commit": git_commit(Path(__file__).resolve().parents[3]),
            "parameters": parameters,
            "parameter_hash": parameter_hash(parameters),
            "seed": seed,
            "closure_status": evaluation.output.closure_status.value,
            "numeric_tolerances": {"absolute": 1e-5},
            "residual_vector": list(evaluation.residuals.values()),
            "dependency_chain": list(evaluation.output.metadata["dependency_chain"]),
            "generated_files": generated,
            "regeneration_command": (
                "python -m the_nothingness_effect.artificial_intelligence.multimodal."
                f"{'simulation' if simulation else 'test'}.run_pipeline"
            ),
            "source_status": "synthetic_deterministic_training_fixture",
            "evaluation_metrics": evaluation.metrics,
        },
    )
    return {
        "model": model,
        "training": run,
        "evaluation": evaluation,
        "tables": tables,
        "figures": figures,
        "animations": movies,
        "manifest": manifest,
        "network": network,
    }
