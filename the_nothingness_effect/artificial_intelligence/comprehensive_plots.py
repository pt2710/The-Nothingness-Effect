"""Visual diagnostics for comprehensive TNE AI evaluation."""

from __future__ import annotations

from pathlib import Path
from statistics import mean, pstdev
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from .comprehensive_support import STREAM_NAMES


def _plot_save(figure: plt.Figure, path: Path) -> None:
    figure.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(figure)


def plot_learning(
    plots: Path,
    history: list[dict[str, Any]],
) -> None:
    epochs = sorted({int(row["epoch"]) for row in history})
    for filename, fields, title, ylabel in (
        (
            "learning_loss_curves.png",
            ("train_total_loss", "validation_loss"),
            "Training and validation loss",
            "loss",
        ),
        (
            "learning_accuracy_curves.png",
            ("train_accuracy", "validation_accuracy"),
            "Training and validation accuracy",
            "accuracy",
        ),
    ):
        figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
        for field in fields:
            values = [
                mean(
                    float(row[field])
                    for row in history
                    if int(row["epoch"]) == epoch
                )
                for epoch in epochs
            ]
            deviations = [
                pstdev(
                    float(row[field])
                    for row in history
                    if int(row["epoch"]) == epoch
                )
                for epoch in epochs
            ]
            axis.errorbar(
                epochs,
                values,
                yerr=deviations,
                marker="o",
                label=field,
            )
        axis.set(title=title, xlabel="epoch", ylabel=ylabel)
        if ylabel == "accuracy":
            axis.set_ylim(0.0, 1.05)
        axis.legend()
        _plot_save(figure, plots / filename)


def plot_confusions(
    plots: Path,
    confusion: torch.Tensor,
    class_names: tuple[str, ...],
) -> None:
    for filename, matrix, title, fmt in (
        (
            "aggregate_confusion_matrix.png",
            confusion.to(torch.float64),
            "Aggregate held-out confusion matrix",
            ".0f",
        ),
        (
            "normalized_confusion_matrix.png",
            confusion.to(torch.float64)
            / confusion.sum(dim=1, keepdim=True).clamp_min(1),
            "Row-normalized held-out confusion matrix",
            ".2f",
        ),
    ):
        figure, axis = plt.subplots(figsize=(6, 5), constrained_layout=True)
        image = axis.imshow(matrix.numpy())
        for row in range(matrix.shape[0]):
            for column in range(matrix.shape[1]):
                axis.text(
                    column,
                    row,
                    format(float(matrix[row, column]), fmt),
                    ha="center",
                    va="center",
                )
        axis.set(
            title=title,
            xlabel="predicted",
            ylabel="true",
            xticks=range(len(class_names)),
            yticks=range(len(class_names)),
            xticklabels=class_names,
            yticklabels=class_names,
        )
        axis.tick_params(axis="x", rotation=25)
        figure.colorbar(image, ax=axis)
        _plot_save(figure, plots / filename)


def plot_class_metrics(
    plots: Path,
    class_rows: list[dict[str, Any]],
) -> None:
    rows = [row for row in class_rows if row["split"] == "test"]
    names = sorted({str(row["class_name"]) for row in rows})
    figure, axis = plt.subplots(figsize=(9, 5), constrained_layout=True)
    positions = torch.arange(len(names), dtype=torch.float64).numpy()
    width = 0.24
    for offset, metric in zip(
        (-width, 0.0, width),
        ("precision", "recall", "f1"),
        strict=True,
    ):
        values = [
            mean(
                float(row[metric])
                for row in rows
                if row["class_name"] == name
            )
            for name in names
        ]
        axis.bar(positions + offset, values, width=width, label=metric)
    axis.set_xticks(positions, names, rotation=20)
    axis.set_ylim(0.0, 1.05)
    axis.set_title("Held-out class-wise metrics across seeds")
    axis.legend()
    _plot_save(figure, plots / "per_class_metrics.png")


def plot_calibration(
    plots: Path,
    calibration: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
) -> None:
    figure, axis = plt.subplots(figsize=(6, 5), constrained_layout=True)
    axis.plot([0, 1], [0, 1], linestyle="--", label="perfect")
    populated = [row for row in calibration if int(row["count"]) > 0]
    axis.plot(
        [float(row["mean_confidence"]) for row in populated],
        [float(row["accuracy"]) for row in populated],
        marker="o",
        label="model",
    )
    axis.set(
        title="Reliability diagram",
        xlabel="mean confidence",
        ylabel="empirical accuracy",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    axis.legend()
    _plot_save(figure, plots / "calibration_curve.png")

    test = [row for row in predictions if row["split"] == "test"]
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.hist(
        [
            float(row["confidence"])
            for row in test
            if int(row["correct"]) == 1
        ],
        bins=10,
        alpha=0.6,
        label="correct",
    )
    axis.hist(
        [
            float(row["confidence"])
            for row in test
            if int(row["correct"]) == 0
        ],
        bins=10,
        alpha=0.6,
        label="incorrect",
    )
    axis.set(
        title="Held-out confidence distribution",
        xlabel="confidence",
        ylabel="count",
    )
    axis.legend()
    _plot_save(figure, plots / "confidence_histogram.png")

    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.scatter(
        [float(row["predictive_entropy"]) for row in test],
        [float(row["confidence"]) for row in test],
        s=18,
    )
    axis.set(
        title="Predictive entropy versus confidence",
        xlabel="predictive entropy",
        ylabel="confidence",
    )
    _plot_save(figure, plots / "entropy_confidence.png")


def plot_geometry(
    plots: Path,
    geometry: list[dict[str, Any]],
) -> None:
    rows = [row for row in geometry if row["split"] == "test"]
    modalities = sorted({str(row["modality"]) for row in rows})
    figure = plt.figure(figsize=(8, 7), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    for modality in modalities:
        selected = [row for row in rows if row["modality"] == modality]
        axis.scatter(
            [float(row["x"]) for row in selected],
            [float(row["y"]) for row in selected],
            [float(row["z"]) for row in selected],
            s=16,
            label=modality,
        )
    axis.set(
        title="Modality-rotated 3D coordinate manifold",
        xlabel="x",
        ylabel="y",
        zlabel="z",
    )
    axis.legend()
    _plot_save(figure, plots / "modality_geometry_3d.png")

    for first, second, filename in (
        ("x", "y", "modality_geometry_xy.png"),
        ("x", "z", "modality_geometry_xz.png"),
        ("y", "z", "modality_geometry_yz.png"),
    ):
        figure, axis = plt.subplots(figsize=(7, 6), constrained_layout=True)
        for modality in modalities:
            selected = [row for row in rows if row["modality"] == modality]
            axis.scatter(
                [float(row[first]) for row in selected],
                [float(row[second]) for row in selected],
                s=14,
                label=modality,
            )
        axis.set(
            title=f"Modality geometry: {first}{second} projection",
            xlabel=first,
            ylabel=second,
        )
        axis.legend()
        _plot_save(figure, plots / filename)

    figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    for modality in modalities:
        selected = [
            float(row["observer_horizon"])
            for row in rows
            if row["modality"] == modality
        ]
        axis.hist(selected, bins=12, alpha=0.45, label=modality)
    axis.axvline(0.0, linestyle="--")
    axis.set(
        title="Observer-Horizon distribution",
        xlabel="horizon",
        ylabel="count",
    )
    axis.legend()
    _plot_save(figure, plots / "observer_horizon_distribution.png")

    stream_values = {
        stream: mean(float(row[f"stream_{stream}"]) for row in rows)
        for stream in STREAM_NAMES
    }
    figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    axis.bar(list(stream_values), list(stream_values.values()))
    axis.set(
        title="MPL-TC stream occupancy",
        ylabel="mean routing weight",
    )
    axis.tick_params(axis="x", rotation=20)
    _plot_save(figure, plots / "mpl_tc_stream_occupancy.png")

    dual_residual = [
        max(
            abs(float(row["x"]) + float(row["dual_x"])),
            abs(float(row["y"]) + float(row["dual_y"])),
            abs(float(row["z"]) + float(row["dual_z"])),
        )
        for row in rows
    ]
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.hist(dual_residual, bins=12)
    axis.set(
        title="Antipodal dual involution residual",
        xlabel="max |r + dual(r)|",
    )
    _plot_save(figure, plots / "dual_involution_residual.png")


def plot_training_diagnostics(
    plots: Path,
    history: list[dict[str, Any]],
) -> None:
    epochs = sorted({int(row["epoch"]) for row in history})
    diagnostics = (
        (
            "modality_weight_evolution.png",
            tuple(key for key in history[0] if key.startswith("weight_")),
            "Modality weight evolution",
            "weight",
        ),
        (
            "cluster_growth.png",
            ("active_clusters", "growth_events"),
            "Cluster growth",
            "count",
        ),
        (
            "rbm_free_energy.png",
            ("local_free_energy", "global_free_energy"),
            "RBM free energy",
            "free energy",
        ),
        (
            "training_hyperparameters.png",
            ("K_D", "soi_scale", "learning_rate"),
            "Dynamic training parameters",
            "value",
        ),
        (
            "gradient_and_closure.png",
            ("gradient_norm", "train_closure_penalty"),
            "Gradient and closure diagnostics",
            "value",
        ),
    )
    for filename, fields, title, ylabel in diagnostics:
        figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
        for field in fields:
            values = [
                mean(
                    float(row[field])
                    for row in history
                    if int(row["epoch"]) == epoch
                )
                for epoch in epochs
            ]
            axis.plot(epochs, values, marker="o", label=field)
        axis.set(title=title, xlabel="epoch", ylabel=ylabel)
        axis.legend()
        _plot_save(figure, plots / filename)


def plot_summaries(
    plots: Path,
    split_metrics: list[dict[str, Any]],
    source_removal: list[dict[str, Any]],
    variation: list[dict[str, Any]],
    reconstruction: list[dict[str, Any]],
    module_rows: list[dict[str, Any]],
) -> None:
    test_rows = [row for row in split_metrics if row["split"] == "test"]
    seed_values = sorted({int(row["seed"]) for row in split_metrics})
    seeds = [str(seed) for seed in seed_values]
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.bar(
        seeds,
        [
            float(
                next(
                    row
                    for row in test_rows
                    if int(row["seed"]) == seed
                )["accuracy"]
            )
            for seed in seed_values
        ],
    )
    axis.set(
        title="Held-out accuracy by seed",
        xlabel="seed",
        ylabel="accuracy",
        ylim=(0, 1.05),
    )
    _plot_save(figure, plots / "seed_accuracy_distribution.png")

    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    gaps = [
        float(
            next(
                row
                for row in split_metrics
                if int(row["seed"]) == seed and row["split"] == "test"
            )["cross_entropy"]
        )
        - float(
            next(
                row
                for row in split_metrics
                if int(row["seed"]) == seed and row["split"] == "train"
            )["cross_entropy"]
        )
        for seed in seed_values
    ]
    axis.bar(seeds, gaps)
    axis.axhline(0.0, linestyle="--")
    axis.set(
        title="Generalization gap",
        xlabel="seed",
        ylabel="test CE - train CE",
    )
    _plot_save(figure, plots / "generalization_gap.png")

    variants = sorted({str(row["variant"]) for row in source_removal})
    figure, axis = plt.subplots(figsize=(11, 5), constrained_layout=True)
    values = [
        mean(
            float(row["accuracy"])
            for row in source_removal
            if row["variant"] == variant
        )
        for variant in variants
    ]
    axis.bar(variants, values)
    axis.set(
        title="Source-removal held-out accuracy",
        ylabel="accuracy",
        ylim=(0, 1.05),
    )
    axis.tick_params(axis="x", rotation=35)
    _plot_save(figure, plots / "source_removal_accuracy.png")

    figure, axis = plt.subplots(figsize=(10, 5), constrained_layout=True)
    labels = [f"{row['split']}:{row['modality']}" for row in variation]
    axis.bar(
        labels,
        [float(row["mean_pairwise_distance"]) for row in variation],
    )
    axis.set(
        title="Dataset variation by split and modality",
        ylabel="mean pairwise distance",
    )
    axis.tick_params(axis="x", rotation=45)
    _plot_save(figure, plots / "dataset_variation.png")

    modalities = sorted({str(row["modality"]) for row in reconstruction})
    figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    axis.bar(
        modalities,
        [
            mean(
                float(row["rmse"])
                for row in reconstruction
                if row["modality"] == modality
            )
            for modality in modalities
        ],
    )
    axis.set(title="Held-out reconstruction RMSE", ylabel="RMSE")
    _plot_save(figure, plots / "reconstruction_by_modality.png")

    modules = sorted({str(row["module"]) for row in module_rows})
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    accuracy = [
        mean(
            float(row["accuracy"])
            for row in module_rows
            if row["module"] == module
            and row.get("accuracy") not in (None, "")
        )
        if any(
            row["module"] == module
            and row.get("accuracy") not in (None, "")
            for row in module_rows
        )
        else 0.0
        for module in modules
    ]
    axis.bar(modules, accuracy)
    axis.set(
        title="Module-level per-sample accuracy",
        ylabel="accuracy",
        ylim=(0, 1.05),
    )
    _plot_save(figure, plots / "module_accuracy_summary.png")

    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    residual = [
        mean(
            float(row["residual_l2"])
            for row in module_rows
            if row["module"] == module
        )
        for module in modules
    ]
    axis.bar(modules, residual)
    axis.set(title="Module residual magnitude", ylabel="residual L2")
    _plot_save(figure, plots / "module_residual_summary.png")


def plot_latent(
    plots: Path,
    latent_rows: list[dict[str, Any]],
) -> None:
    matrix = torch.tensor(
        [row["latent"] for row in latent_rows],
        dtype=torch.float64,
    )
    matrix = matrix - matrix.mean(dim=0, keepdim=True)
    _, _, right = torch.linalg.svd(matrix, full_matrices=False)
    projected = matrix @ right[:2].T
    labels = [int(row["label"]) for row in latent_rows]
    figure, axis = plt.subplots(figsize=(7, 6), constrained_layout=True)
    for label in sorted(set(labels)):
        indices = [
            index
            for index, value in enumerate(labels)
            if value == label
        ]
        axis.scatter(
            projected[indices, 0].numpy(),
            projected[indices, 1].numpy(),
            s=18,
            label=str(label),
        )
    axis.set(title="Held-out latent PCA", xlabel="PC1", ylabel="PC2")
    axis.legend(title="class")
    _plot_save(figure, plots / "latent_pca_2d.png")
