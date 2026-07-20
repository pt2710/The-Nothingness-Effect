"""Train, validate, and evaluate QENN, PGQENN, and SOInets together.

The pipeline uses deterministic synthetic fixtures as executable model evidence.
It does not reinterpret runtime performance as mathematical theorem closure or
as empirical validation on real-world observations.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev
import time
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from torch.nn import functional

from .multimodal.data import (
    MultimodalDataset,
    make_synthetic_multimodal_dataset,
)
from .multimodal.evaluation import (
    MultimodalEvaluation,
    classification_metrics_from_confusion,
    evaluate_multimodal_model,
    evaluate_source_removals,
)
from .multimodal.model import TNETrainableMultimodalModel
from .multimodal.training import (
    MultimodalTrainingRun,
    train_multimodal_model,
)


CLAIM_BOUNDARY = (
    "synthetic deterministic train/validation/test evidence; "
    "not empirical validation or a formal theorem proof"
)


def _status_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _residual_summary(residuals: dict[str, Any]) -> tuple[float, float]:
    values = [
        abs(float(torch.as_tensor(value).detach().cpu()))
        for value in residuals.values()
    ]
    if not values:
        return 0.0, 0.0
    return math.sqrt(sum(value * value for value in values)), max(values)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: "" if row.get(key) is None else row.get(key)
                    for key in fieldnames
                }
            )


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _model_size(model: torch.nn.Module) -> dict[str, int]:
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    trainable_count = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )
    parameter_bytes = sum(
        parameter.numel() * parameter.element_size()
        for parameter in model.parameters()
    )
    return {
        "parameter_count": int(parameter_count),
        "trainable_parameter_count": int(trainable_count),
        "parameter_bytes": int(parameter_bytes),
    }


def _prediction_rows(
    seed: int,
    evaluation: MultimodalEvaluation,
    labels: torch.Tensor,
    class_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    probabilities = evaluation.output.observation.detach().cpu()
    predictions = probabilities.argmax(dim=-1)
    confidence = probabilities.max(dim=-1).values
    rows: list[dict[str, Any]] = []
    for index in range(labels.numel()):
        row: dict[str, Any] = {
            "seed": seed,
            "sample_index": index,
            "true_index": int(labels[index]),
            "true_class": class_names[int(labels[index])],
            "predicted_index": int(predictions[index]),
            "predicted_class": class_names[int(predictions[index])],
            "confidence": float(confidence[index]),
            "correct": int(predictions[index] == labels[index]),
        }
        for class_index, class_name in enumerate(class_names):
            row[f"probability_{class_name}"] = float(
                probabilities[index, class_index]
            )
        rows.append(row)
    return rows


def _module_rows(
    seed: int,
    evaluation: MultimodalEvaluation,
    labels: torch.Tensor,
) -> list[dict[str, Any]]:
    output = evaluation.output
    backbone = output.backbone_output
    soinet = backbone.soinet_output
    rows: list[dict[str, Any]] = []

    for index, qenn in enumerate(soinet.qenn_outputs):
        probabilities = qenn.observation.detach()
        predictions = probabilities.argmax(dim=-1)
        confusion = torch.bincount(
            labels * probabilities.shape[-1] + predictions,
            minlength=probabilities.shape[-1] ** 2,
        ).reshape(probabilities.shape[-1], probabilities.shape[-1])
        residual_l2, max_residual = _residual_summary(qenn.residuals)
        metrics = classification_metrics_from_confusion(confusion)
        rows.append(
            {
                "seed": seed,
                "module": "QENN",
                "instance": index,
                "classification_scope": "per_sample",
                "accuracy": float((predictions == labels).float().mean()),
                "cross_entropy": float(
                    functional.cross_entropy(qenn.readout, labels)
                ),
                "macro_precision": metrics["macro_precision"],
                "macro_recall": metrics["macro_recall"],
                "macro_f1": metrics["macro_f1"],
                "micro_f1": metrics["micro_f1"],
                "mean_confidence": float(
                    probabilities.max(dim=-1).values.mean()
                ),
                "predictive_entropy": float(
                    torch.mean(
                        -torch.sum(
                            probabilities
                            * torch.log(probabilities.clamp_min(1e-9)),
                            dim=-1,
                        )
                    )
                ),
                "residual_l2": residual_l2,
                "max_residual": max_residual,
                "closure_status": _status_value(qenn.closure_status),
                "triadic_source_removal_delta": None,
                "signed_spectrum_source_removal_delta": None,
            }
        )

    for index, pgqenn in enumerate(soinet.pgqenn_outputs):
        probabilities = pgqenn.observation.detach()
        residual_l2, max_residual = _residual_summary(pgqenn.residuals)
        rows.append(
            {
                "seed": seed,
                "module": "PGQENN",
                "instance": index,
                "classification_scope": "graph_level_diagnostic",
                "accuracy": None,
                "cross_entropy": None,
                "macro_precision": None,
                "macro_recall": None,
                "macro_f1": None,
                "micro_f1": None,
                "mean_confidence": float(
                    probabilities.max(dim=-1).values.mean()
                ),
                "predictive_entropy": float(
                    torch.mean(
                        -torch.sum(
                            probabilities
                            * torch.log(probabilities.clamp_min(1e-9)),
                            dim=-1,
                        )
                    )
                ),
                "residual_l2": residual_l2,
                "max_residual": max_residual,
                "closure_status": _status_value(pgqenn.closure_status),
                "triadic_source_removal_delta": float(
                    pgqenn.triadic_stream_source_removal_delta.detach().cpu()
                ),
                "signed_spectrum_source_removal_delta": float(
                    pgqenn.signed_spectrum_source_removal_delta.detach().cpu()
                ),
            }
        )

    soinet_residual_l2, soinet_max_residual = _residual_summary(
        soinet.residuals
    )
    rows.append(
        {
            "seed": seed,
            "module": "SOInets",
            "instance": 0,
            "classification_scope": "per_sample_task_head",
            "accuracy": evaluation.metrics["accuracy"],
            "cross_entropy": evaluation.metrics["cross_entropy"],
            "macro_precision": evaluation.metrics["macro_precision"],
            "macro_recall": evaluation.metrics["macro_recall"],
            "macro_f1": evaluation.metrics["macro_f1"],
            "micro_f1": evaluation.metrics["micro_f1"],
            "mean_confidence": evaluation.metrics["mean_confidence"],
            "predictive_entropy": evaluation.metrics["predictive_entropy"],
            "residual_l2": soinet_residual_l2,
            "max_residual": soinet_max_residual,
            "closure_status": _status_value(soinet.closure_status),
            "triadic_source_removal_delta": None,
            "signed_spectrum_source_removal_delta": None,
        }
    )
    return rows


def _metric_rows(
    seed: int,
    split: str,
    evaluation: MultimodalEvaluation,
) -> list[dict[str, Any]]:
    return [
        {
            "seed": seed,
            "split": split,
            "metric": name,
            "value": value,
        }
        for name, value in evaluation.metrics.items()
    ]


def _aggregate_long_metrics(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        key = (str(row["split"]), str(row["metric"]))
        groups.setdefault(key, []).append(float(row["value"]))
    aggregate: list[dict[str, Any]] = []
    for (split, metric), values in sorted(groups.items()):
        aggregate.append(
            {
                "split": split,
                "metric": metric,
                "count": len(values),
                "mean": mean(values),
                "population_std": pstdev(values),
                "minimum": min(values),
                "maximum": max(values),
            }
        )
    return aggregate


def _aggregate_modules(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    numeric_fields = (
        "accuracy",
        "cross_entropy",
        "macro_f1",
        "micro_f1",
        "mean_confidence",
        "predictive_entropy",
        "residual_l2",
        "max_residual",
        "triadic_source_removal_delta",
        "signed_spectrum_source_removal_delta",
    )
    grouped: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        for field in numeric_fields:
            value = row.get(field)
            if value is None or value == "":
                continue
            grouped.setdefault(
                (str(row["module"]), field),
                [],
            ).append(float(value))
    result: list[dict[str, Any]] = []
    for (module, metric), values in sorted(grouped.items()):
        result.append(
            {
                "module": module,
                "metric": metric,
                "count": len(values),
                "mean": mean(values),
                "population_std": pstdev(values),
                "minimum": min(values),
                "maximum": max(values),
            }
        )
    return result


def _generalization_status(gap: float) -> str:
    absolute = abs(gap)
    if absolute <= 0.05:
        return "measured_low_gap"
    if absolute <= 0.15:
        return "measured_moderate_gap"
    return "measured_large_gap"


def _plot_learning_curves(
    output: Path,
    histories: list[dict[str, Any]],
) -> None:
    seeds = sorted({int(row["seed"]) for row in histories})
    epochs = sorted({int(row["epoch"]) for row in histories})
    train_mean: list[float] = []
    train_std: list[float] = []
    validation_mean: list[float] = []
    validation_std: list[float] = []
    for epoch in epochs:
        selected = [row for row in histories if int(row["epoch"]) == epoch]
        train_values = [float(row["train_total_loss"]) for row in selected]
        validation_values = [
            float(row["validation_loss"]) for row in selected
        ]
        train_mean.append(mean(train_values))
        train_std.append(pstdev(train_values))
        validation_mean.append(mean(validation_values))
        validation_std.append(pstdev(validation_values))
    figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    axis.errorbar(
        epochs,
        train_mean,
        yerr=train_std,
        marker="o",
        capsize=3,
        label="train total",
    )
    axis.errorbar(
        epochs,
        validation_mean,
        yerr=validation_std,
        marker="s",
        capsize=3,
        label="validation cross-entropy",
    )
    axis.set(
        title=f"AI training and validation across {len(seeds)} seeds",
        xlabel="epoch",
        ylabel="loss",
    )
    axis.legend()
    figure.savefig(output / "learning_curves.png", dpi=160)
    plt.close(figure)


def _plot_confusion(
    output: Path,
    confusion: torch.Tensor,
    class_names: tuple[str, ...],
) -> None:
    figure, axis = plt.subplots(figsize=(6, 5), constrained_layout=True)
    image = axis.imshow(confusion.numpy())
    for row in range(confusion.shape[0]):
        for column in range(confusion.shape[1]):
            axis.text(
                column,
                row,
                int(confusion[row, column]),
                ha="center",
                va="center",
            )
    axis.set(
        title="Aggregate held-out SOInets task confusion matrix",
        xlabel="predicted",
        ylabel="true",
        xticks=range(len(class_names)),
        yticks=range(len(class_names)),
        xticklabels=class_names,
        yticklabels=class_names,
    )
    axis.tick_params(axis="x", rotation=25)
    figure.colorbar(image, ax=axis)
    figure.savefig(output / "aggregate_confusion_matrix.png", dpi=160)
    plt.close(figure)


def _plot_module_summary(
    output: Path,
    module_summary: list[dict[str, Any]],
) -> None:
    residual_rows = [
        row for row in module_summary if row["metric"] == "residual_l2"
    ]
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.bar(
        [str(row["module"]) for row in residual_rows],
        [float(row["mean"]) for row in residual_rows],
        yerr=[float(row["population_std"]) for row in residual_rows],
        capsize=4,
    )
    axis.set(
        title="Module residual magnitude across seeds",
        ylabel="mean residual L2",
    )
    figure.savefig(output / "module_residual_summary.png", dpi=160)
    plt.close(figure)

    accuracy_rows = [
        row for row in module_summary if row["metric"] == "accuracy"
    ]
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.bar(
        [str(row["module"]) for row in accuracy_rows],
        [float(row["mean"]) for row in accuracy_rows],
        yerr=[float(row["population_std"]) for row in accuracy_rows],
        capsize=4,
    )
    axis.set(
        title="Per-sample classification accuracy",
        ylabel="accuracy",
        ylim=(0.0, 1.05),
    )
    figure.savefig(output / "module_accuracy_summary.png", dpi=160)
    plt.close(figure)


def _plot_generalization(
    output: Path,
    seed_summaries: list[dict[str, Any]],
) -> None:
    figure, axis = plt.subplots(figsize=(7, 5), constrained_layout=True)
    axis.bar(
        [str(row["seed"]) for row in seed_summaries],
        [float(row["generalization_gap_cross_entropy"]) for row in seed_summaries],
    )
    axis.axhline(0.0, linestyle="--")
    axis.set(
        title="Held-out generalization gap",
        xlabel="seed",
        ylabel="test cross-entropy - train cross-entropy",
    )
    figure.savefig(output / "generalization_gap.png", dpi=160)
    plt.close(figure)


def _write_report(
    path: Path,
    seed_summaries: list[dict[str, Any]],
    module_summary: list[dict[str, Any]],
    closure_counts: dict[str, dict[str, int]],
) -> None:
    clean_metrics = {
        (str(row["module"]), str(row["metric"])): row
        for row in module_summary
    }
    lines = [
        "# TNE AI Training, Validation, and Evaluation Report",
        "",
        f"**Claim boundary:** {CLAIM_BOUNDARY}.",
        "",
        "## Run status",
        "",
        "| Seed | Best epoch | Test accuracy | Macro F1 | Test loss | Generalization gap | Status |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in seed_summaries:
        lines.append(
            "| {seed} | {best_epoch} | {test_accuracy:.6f} | "
            "{test_macro_f1:.6f} | {test_cross_entropy:.6f} | "
            "{generalization_gap_cross_entropy:.6f} | "
            "{generalization_status} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Module summary",
            "",
            "| Module | Accuracy | Macro F1 | Residual L2 | Mean confidence |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    modules = sorted({module for module, _ in clean_metrics})
    for module in modules:
        def value(metric: str) -> str:
            row = clean_metrics.get((module, metric))
            return "n/a" if row is None else f"{float(row['mean']):.6f}"

        lines.append(
            f"| {module} | {value('accuracy')} | {value('macro_f1')} | "
            f"{value('residual_l2')} | {value('mean_confidence')} |"
        )
    lines.extend(
        [
            "",
            "## Closure status",
            "",
            "Runtime training and evaluation status is reported independently "
            "from theorem closure.",
            "",
        ]
    )
    for module, counts in sorted(closure_counts.items()):
        lines.append(
            f"- **{module}:** "
            + ", ".join(
                f"`{status}`={count}"
                for status, count in sorted(counts.items())
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- QENN accuracy is computed from its per-sample readout.",
            "- PGQENN is evaluated as a graph-level diagnostic because its canonical "
            "readout represents a complete prime graph rather than one label per sample.",
            "- SOInets task metrics use the trainable per-sample task head over the "
            "canonical QENN/PGQENN/SOInet backbone.",
            "- `OPEN` or other non-closed theorem statuses remain independent from "
            "successful runtime training.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_ai_module_training_evaluation(
    output_dir: str | Path,
    *,
    seeds: Iterable[int] = (0, 1, 2),
    epochs: int = 6,
    samples_per_class: int = 10,
) -> dict[str, Any]:
    """Run a complete multi-seed train/validate/test evaluation."""

    output = Path(output_dir)
    seeds = tuple(int(seed) for seed in seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be a non-empty unique sequence")
    if epochs < 1:
        raise ValueError("epochs must be positive")
    if samples_per_class < 5:
        raise ValueError("samples_per_class must be at least five")

    checkpoints = output / "checkpoints"
    trained_models = output / "trained_model"
    predictions_dir = output / "predictions"
    plots = output / "plots"
    for directory in (
        checkpoints,
        trained_models,
        predictions_dir,
        plots,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    metric_rows: list[dict[str, Any]] = []
    module_rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []
    history_rows: list[dict[str, Any]] = []
    seed_summaries: list[dict[str, Any]] = []
    aggregate_confusion: torch.Tensor | None = None
    split_manifest: list[dict[str, Any]] = []
    class_names: tuple[str, ...] | None = None

    for seed in seeds:
        torch.manual_seed(seed)
        dataset: MultimodalDataset = make_synthetic_multimodal_dataset(
            samples_per_class=samples_per_class,
            seed=seed,
        )
        class_names = dataset.class_names
        model = TNETrainableMultimodalModel()
        started = time.perf_counter()
        training: MultimodalTrainingRun = train_multimodal_model(
            model,
            dataset.train,
            dataset.validation,
            epochs=epochs,
            seed=seed,
            optimize_K_D=True,
            adaptive_learning_rate=True,
        )
        training_seconds = time.perf_counter() - started

        train_evaluation = evaluate_multimodal_model(
            model,
            dataset.train,
        )
        validation_evaluation = evaluate_multimodal_model(
            model,
            dataset.validation,
        )
        inference_started = time.perf_counter()
        test_evaluation = evaluate_multimodal_model(
            model,
            dataset.test,
        )
        inference_seconds = time.perf_counter() - inference_started
        test_size = int(dataset.test.labels.numel())

        checkpoint_payload = {
            "schema_version": "1.0",
            "seed": seed,
            "best_epoch": training.best_epoch,
            "best_validation_objective": (
                training.best_validation_objective
            ),
            "restored_best_checkpoint": (
                training.restored_best_checkpoint
            ),
            "state_dict": model.state_dict(),
            "class_names": dataset.class_names,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        checkpoint_path = checkpoints / f"seed_{seed}_best.pt"
        trained_path = trained_models / f"seed_{seed}_model.pt"
        torch.save(checkpoint_payload, checkpoint_path)
        torch.save(checkpoint_payload, trained_path)

        _write_csv(
            predictions_dir / f"seed_{seed}_test_predictions.csv",
            _prediction_rows(
                seed,
                test_evaluation,
                dataset.test.labels,
                dataset.class_names,
            ),
        )

        for split, evaluation in (
            ("train", train_evaluation),
            ("validation", validation_evaluation),
            ("test", test_evaluation),
        ):
            metric_rows.extend(_metric_rows(seed, split, evaluation))

        per_module = _module_rows(
            seed,
            test_evaluation,
            dataset.test.labels,
        )
        module_rows.extend(per_module)
        for row in evaluate_source_removals(model, dataset.test):
            ablation_rows.append({"seed": seed, **row})

        for epoch in training.history:
            history_rows.append(
                {
                    "seed": seed,
                    "epoch": epoch.epoch,
                    "train_total_loss": epoch.train_total_loss,
                    "train_task_loss": epoch.train_task_loss,
                    "train_reconstruction_loss": (
                        epoch.train_reconstruction_loss
                    ),
                    "train_energy_loss": epoch.train_energy_loss,
                    "train_closure_penalty": (
                        epoch.train_closure_penalty
                    ),
                    "train_accuracy": epoch.train_accuracy,
                    "validation_loss": epoch.validation_loss,
                    "validation_accuracy": (
                        epoch.validation_accuracy
                    ),
                    "gradient_norm": epoch.gradient_norm,
                    "learning_rate": epoch.learning_rate,
                    "K_D": epoch.K_D,
                    "soi_scale": epoch.soi_scale,
                    "validation_objective": (
                        epoch.validation_objective
                    ),
                    "is_best_epoch": int(
                        epoch.epoch == training.best_epoch
                    ),
                }
            )

        generalization_gap = (
            test_evaluation.metrics["cross_entropy"]
            - train_evaluation.metrics["cross_entropy"]
        )
        size = _model_size(model)
        seed_summaries.append(
            {
                "seed": seed,
                "training_status": "completed",
                "validation_status": "best_checkpoint_restored",
                "test_status": "evaluated_held_out",
                "best_epoch": training.best_epoch,
                "best_validation_objective": (
                    training.best_validation_objective
                ),
                "train_accuracy": train_evaluation.metrics["accuracy"],
                "validation_accuracy": (
                    validation_evaluation.metrics["accuracy"]
                ),
                "test_accuracy": test_evaluation.metrics["accuracy"],
                "test_macro_f1": (
                    test_evaluation.metrics["macro_f1"]
                ),
                "test_cross_entropy": (
                    test_evaluation.metrics["cross_entropy"]
                ),
                "test_ece": (
                    test_evaluation.metrics[
                        "expected_calibration_error"
                    ]
                ),
                "test_reconstruction_rmse": (
                    test_evaluation.metrics[
                        "mean_reconstruction_rmse"
                    ]
                ),
                "generalization_gap_cross_entropy": (
                    generalization_gap
                ),
                "generalization_status": (
                    _generalization_status(generalization_gap)
                ),
                "training_seconds": training_seconds,
                "inference_seconds": inference_seconds,
                "inference_seconds_per_sample": (
                    inference_seconds / max(1, test_size)
                ),
                "checkpoint_bytes": checkpoint_path.stat().st_size,
                **size,
                "closure_status": _status_value(
                    test_evaluation.output.closure_status
                ),
            }
        )

        aggregate_confusion = (
            test_evaluation.confusion_matrix.clone()
            if aggregate_confusion is None
            else aggregate_confusion
            + test_evaluation.confusion_matrix
        )
        split_manifest.append(
            {
                "seed": seed,
                "train_samples": int(dataset.train.labels.numel()),
                "validation_samples": int(
                    dataset.validation.labels.numel()
                ),
                "test_samples": test_size,
                "class_counts": {
                    split: [
                        int(
                            torch.sum(
                                getattr(dataset, split).labels
                                == class_index
                            )
                        )
                        for class_index in range(
                            len(dataset.class_names)
                        )
                    ]
                    for split in ("train", "validation", "test")
                },
            }
        )

    if (
        aggregate_confusion is None
        or class_names is None
        or not seed_summaries
    ):
        raise RuntimeError("evaluation produced no results")

    aggregate_metrics = _aggregate_long_metrics(metric_rows)
    module_summary = _aggregate_modules(module_rows)
    closure_counts: dict[str, dict[str, int]] = {}
    for row in module_rows:
        module = str(row["module"])
        status = str(row["closure_status"])
        closure_counts.setdefault(module, {})
        closure_counts[module][status] = (
            closure_counts[module].get(status, 0) + 1
        )

    _write_csv(output / "metrics.csv", metric_rows)
    _write_csv(output / "aggregate_metrics.csv", aggregate_metrics)
    _write_csv(output / "module_metrics.csv", module_rows)
    _write_csv(output / "module_metric_summary.csv", module_summary)
    _write_csv(output / "source_removal.csv", ablation_rows)
    _write_csv(output / "training_history.csv", history_rows)
    _write_csv(output / "seed_summary.csv", seed_summaries)

    _write_json(
        output / "configuration.json",
        {
            "schema_version": "1.0",
            "seeds": list(seeds),
            "epochs": epochs,
            "samples_per_class": samples_per_class,
            "architecture": "TNETrainableMultimodalModel",
            "modules": ["QENN", "PGQENN", "SOInets"],
            "best_checkpoint_selection": (
                "minimum validation objective"
            ),
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    _write_json(
        output / "dataset_manifest.json",
        {
            "schema_version": "1.0",
            "dataset": "deterministic_synthetic_multimodal_fixture",
            "class_names": list(class_names),
            "modalities": ["color", "sound", "vision"],
            "split_records": split_manifest,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    metrics_payload = {
        "schema_version": "1.0",
        "training_status": "completed_all_seeds",
        "validation_status": "best_checkpoint_restored_all_seeds",
        "test_performance": {
            "seed_summary": seed_summaries,
            "aggregate_metrics": aggregate_metrics,
        },
        "generalization_status": {
            str(row["seed"]): row["generalization_status"]
            for row in seed_summaries
        },
        "closure_status": closure_counts,
        "module_summary": module_summary,
        "source_removal_records": len(ablation_rows),
        "all_metrics_finite": all(
            math.isfinite(float(row["value"]))
            for row in metric_rows
        )
        and all(
            math.isfinite(float(row["mean"]))
            for row in module_summary
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(output / "metrics.json", metrics_payload)

    _plot_learning_curves(plots, history_rows)
    _plot_confusion(plots, aggregate_confusion, class_names)
    _plot_module_summary(plots, module_summary)
    _plot_generalization(plots, seed_summaries)
    _write_report(
        output / "evaluation_report.md",
        seed_summaries,
        module_summary,
        closure_counts,
    )

    if not metrics_payload["all_metrics_finite"]:
        raise RuntimeError("AI evaluation generated non-finite metrics")
    if not all(
        row["validation_status"] == "best_checkpoint_restored"
        for row in seed_summaries
    ):
        raise RuntimeError("best validation checkpoint was not restored")
    return metrics_payload
