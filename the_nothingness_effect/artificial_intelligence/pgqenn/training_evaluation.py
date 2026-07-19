"""Explicit train/validation/test evidence for graph-level PGQENN readouts.

Each aligned multimodal observation is represented as one graph whose nodes are
its named modality tokens.  PGQENN therefore retains graph-level semantics
while receiving one supervised graph target per observation.  The canonical
PGQENN backbone is already optimized indirectly by the integrated SOInet loss;
this module adds validation-selected ridge fine-tuning of the graph readout,
calibration, held-out metrics, source-removal witnesses, and reproducible
artifacts without relabelling theorem closure.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

import matplotlib.pyplot as plt
import torch
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.multimodal.data import (
    MultimodalBatch,
)
from the_nothingness_effect.artificial_intelligence.multimodal.evaluation import (
    MultimodalEvaluation,
    classification_metrics_from_confusion,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.model import (
    PGQENNModel,
)

_GRAPH_METRICS: list[dict[str, Any]] = []
_GRAPH_PREDICTIONS: list[dict[str, Any]] = []
_HYPERPARAMETERS: list[dict[str, Any]] = []
_SOURCE_REMOVALS: list[dict[str, Any]] = []


def reset_pgqenn_graph_evidence() -> None:
    """Clear process-local evidence before one comprehensive evaluation run."""

    _GRAPH_METRICS.clear()
    _GRAPH_PREDICTIONS.clear()
    _HYPERPARAMETERS.clear()
    _SOURCE_REMOVALS.clear()


def _pgqenn_modules(model: torch.nn.Module) -> tuple[PGQENNModel, ...]:
    modules = tuple(module for module in model.modules() if isinstance(module, PGQENNModel))
    if not modules:
        raise RuntimeError("integrated TNE AI model exposes no PGQENN modules")
    return modules


def _modality_graphs(
    model: torch.nn.Module,
    batch: MultimodalBatch,
) -> tuple[torch.Tensor, torch.Tensor, tuple[str, ...]]:
    """Return one modality-node graph per aligned observation."""

    batch.validate()
    model.eval()
    with torch.no_grad():
        names, tokens, _ = model.backbone._tokenize(batch.modalities)
    if tokens.ndim != 3 or tokens.shape[0] != batch.labels.shape[0]:
        raise RuntimeError("PGQENN modality graphs require [observations, nodes, features]")
    if tokens.shape[1] < 2:
        raise RuntimeError("each PGQENN graph requires at least two modality nodes")
    return tokens.detach(), batch.labels.detach(), names


def _graph_embeddings(
    module: PGQENNModel,
    graphs: torch.Tensor,
) -> torch.Tensor:
    embeddings: list[torch.Tensor] = []
    module.eval()
    with torch.no_grad():
        for graph in graphs:
            output = module(graph)
            if output.node_state is None:
                raise RuntimeError("PGQENN graph output omitted node_state")
            embeddings.append(output.node_state.mean(dim=0))
    return torch.stack(embeddings)


def _ridge_regression(
    features: torch.Tensor,
    labels: torch.Tensor,
    classes: int,
    ridge: float,
) -> torch.Tensor:
    x = features.detach().to(torch.float64)
    target = functional.one_hot(labels, num_classes=classes).to(torch.float64)
    ones = torch.ones((x.shape[0], 1), dtype=x.dtype, device=x.device)
    design = torch.cat((x, ones), dim=-1)
    penalty = torch.eye(design.shape[-1], dtype=x.dtype, device=x.device)
    penalty[-1, -1] = 0.0
    system = design.T @ design + float(ridge) * penalty
    return torch.linalg.solve(system, design.T @ target)


def _logits_from_beta(features: torch.Tensor, beta: torch.Tensor) -> torch.Tensor:
    return features.to(torch.float64) @ beta[:-1] + beta[-1]


def _confusion(
    labels: torch.Tensor,
    predictions: torch.Tensor,
    classes: int,
) -> torch.Tensor:
    encoded = labels * classes + predictions
    return torch.bincount(
        encoded,
        minlength=classes * classes,
    ).reshape(classes, classes)


def _ece(probabilities: torch.Tensor, labels: torch.Tensor, bins: int = 5) -> float:
    confidence, predictions = probabilities.max(dim=-1)
    result = torch.zeros((), dtype=probabilities.dtype, device=probabilities.device)
    edges = torch.linspace(
        0.0,
        1.0,
        bins + 1,
        dtype=probabilities.dtype,
        device=probabilities.device,
    )
    total = max(1, labels.numel())
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if bool(mask.any()):
            accuracy = (predictions[mask] == labels[mask]).float().mean()
            result = result + mask.float().sum() / total * torch.abs(
                accuracy - confidence[mask].mean()
            )
    return float(result)


def _metric_bundle(
    probabilities: torch.Tensor,
    labels: torch.Tensor,
) -> tuple[dict[str, float], torch.Tensor]:
    predictions = probabilities.argmax(dim=-1)
    classes = probabilities.shape[-1]
    confusion = _confusion(labels, predictions, classes)
    classification = classification_metrics_from_confusion(confusion)
    log_probabilities = torch.log(probabilities.clamp_min(1e-12))
    one_hot = functional.one_hot(labels, num_classes=classes).to(probabilities.dtype)
    metrics = {
        "accuracy": float((predictions == labels).float().mean()),
        "cross_entropy": float(functional.nll_loss(log_probabilities, labels)),
        "brier_score": float(torch.mean((probabilities - one_hot) ** 2)),
        "mean_confidence": float(probabilities.max(dim=-1).values.mean()),
        "predictive_entropy": float(
            torch.mean(
                -torch.sum(
                    probabilities * torch.log(probabilities.clamp_min(1e-12)),
                    dim=-1,
                )
            )
        ),
        "expected_calibration_error": _ece(probabilities, labels),
        **classification,
    }
    return metrics, confusion


def _set_buffer(model: torch.nn.Module, name: str, value: float) -> None:
    tensor = torch.tensor(float(value))
    if hasattr(model, name):
        existing = getattr(model, name)
        if not isinstance(existing, torch.Tensor):
            raise RuntimeError(f"PGQENN hyperparameter slot {name} is not a tensor")
        existing.fill_(float(value))
    else:
        model.register_buffer(name, tensor)


def fit_pgqenn_graph_heads(
    model: torch.nn.Module,
    train_batch: MultimodalBatch,
    validation_batch: MultimodalBatch,
    *,
    seed: int,
) -> tuple[dict[str, Any], ...]:
    """Fit PGQENN graph readouts and select ridge/temperature on validation."""

    train_graphs, train_labels, names = _modality_graphs(model, train_batch)
    validation_graphs, validation_labels, validation_names = _modality_graphs(
        model,
        validation_batch,
    )
    if names != validation_names:
        raise RuntimeError("PGQENN train and validation modality-node domains differ")
    modules = _pgqenn_modules(model)
    ridge_candidates = (1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0)
    temperature_candidates = (0.55, 0.7, 0.85, 1.0, 1.15, 1.35, 1.6)
    rows: list[dict[str, Any]] = []

    for index, module in enumerate(modules):
        train_embeddings = _graph_embeddings(module, train_graphs)
        validation_embeddings = _graph_embeddings(module, validation_graphs)
        classes = module.readout_layer.out_features
        best_score = math.inf
        best_ridge = ridge_candidates[0]
        best_beta: torch.Tensor | None = None
        for ridge in ridge_candidates:
            beta = _ridge_regression(
                train_embeddings,
                train_labels,
                classes,
                ridge,
            )
            validation_logits = _logits_from_beta(validation_embeddings, beta)
            accuracy = float(
                (validation_logits.argmax(dim=-1) == validation_labels).float().mean()
            )
            score = float(functional.cross_entropy(validation_logits, validation_labels))
            score = score + 0.25 * (1.0 - accuracy)
            if score < best_score:
                best_score = score
                best_ridge = float(ridge)
                best_beta = beta
        if best_beta is None:
            raise RuntimeError("PGQENN ridge search produced no finite candidate")
        with torch.no_grad():
            module.readout_layer.weight.copy_(
                best_beta[:-1].T.to(
                    dtype=module.readout_layer.weight.dtype,
                    device=module.readout_layer.weight.device,
                )
            )
            module.readout_layer.bias.copy_(
                best_beta[-1].to(
                    dtype=module.readout_layer.bias.dtype,
                    device=module.readout_layer.bias.device,
                )
            )

        raw_validation_logits = _logits_from_beta(validation_embeddings, best_beta)
        selected_temperature = 1.0
        selected_temperature_score = math.inf
        for temperature in temperature_candidates:
            probabilities = torch.softmax(raw_validation_logits / temperature, dim=-1)
            score = float(
                functional.nll_loss(
                    torch.log(probabilities.clamp_min(1e-12)),
                    validation_labels,
                )
            ) + 0.35 * _ece(probabilities, validation_labels)
            if score < selected_temperature_score:
                selected_temperature_score = score
                selected_temperature = float(temperature)

        _set_buffer(model, f"pgqenn_graph_ridge_lambda_{index}", best_ridge)
        _set_buffer(
            model,
            f"pgqenn_graph_temperature_{index}",
            selected_temperature,
        )
        row = {
            "seed": int(seed),
            "instance": index,
            "training_protocol": "validation_selected_ridge_graph_readout",
            "graph_domain": "one_observation_with_named_modality_nodes",
            "modality_nodes": len(names),
            "train_graphs": int(train_graphs.shape[0]),
            "validation_graphs": int(validation_graphs.shape[0]),
            "selected_ridge_lambda": best_ridge,
            "selected_temperature": selected_temperature,
            "best_validation_objective": selected_temperature_score,
        }
        rows.append(row)
        _HYPERPARAMETERS.append(row)

    setattr(model, "_pgqenn_evidence_seed", int(seed))
    setattr(model, "_pgqenn_evidence_split_cursor", 0)
    return tuple(rows)


def _temperature(model: torch.nn.Module, index: int) -> float:
    value = getattr(model, f"pgqenn_graph_temperature_{index}", None)
    if value is None:
        raise RuntimeError("PGQENN graph temperature was not validation-selected")
    result = float(value.detach().cpu()) if isinstance(value, torch.Tensor) else float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise RuntimeError("PGQENN graph temperature must be finite and positive")
    return result


def evaluate_pgqenn_graph_heads(
    model: torch.nn.Module,
    batch: MultimodalBatch,
) -> dict[str, Any]:
    """Evaluate every PGQENN graph head and their probability ensemble."""

    graphs, labels, names = _modality_graphs(model, batch)
    module_probabilities: list[torch.Tensor] = []
    module_metrics: list[dict[str, Any]] = []
    modules = _pgqenn_modules(model)
    for index, module in enumerate(modules):
        logits: list[torch.Tensor] = []
        module.eval()
        with torch.no_grad():
            for graph in graphs:
                output = module(graph)
                logits.append(output.readout.squeeze(0))
        stacked = torch.stack(logits)
        probabilities = torch.softmax(stacked / _temperature(model, index), dim=-1)
        metrics, confusion = _metric_bundle(probabilities, labels)
        module_probabilities.append(probabilities)
        module_metrics.append(
            {
                "instance": index,
                "graph_count": int(graphs.shape[0]),
                "modality_nodes": len(names),
                "confusion_matrix": confusion.tolist(),
                **metrics,
            }
        )
    ensemble = torch.stack(module_probabilities).mean(dim=0)
    ensemble_metrics, ensemble_confusion = _metric_bundle(ensemble, labels)
    return {
        "probabilities": ensemble,
        "labels": labels,
        "predictions": ensemble.argmax(dim=-1),
        "metrics": {
            "graph_count": int(graphs.shape[0]),
            "modality_nodes": len(names),
            "confusion_matrix": ensemble_confusion.tolist(),
            **ensemble_metrics,
        },
        "module_metrics": module_metrics,
    }


def _source_removal_rows(
    model: torch.nn.Module,
    batch: MultimodalBatch,
    *,
    seed: int,
) -> list[dict[str, Any]]:
    modules = _pgqenn_modules(model)
    original = tuple(
        (module.triadic_streams_enabled, module.signed_spectrum_enabled)
        for module in modules
    )
    complete = evaluate_pgqenn_graph_heads(model, batch)
    complete_probabilities = complete["probabilities"]
    rows: list[dict[str, Any]] = []
    variants = (
        ("complete", None),
        ("triadic_stream_removed", "triadic"),
        ("signed_spectrum_removed", "signed"),
    )
    try:
        for name, removed in variants:
            for module, (triadic, signed) in zip(modules, original, strict=True):
                module.triadic_streams_enabled = triadic and removed != "triadic"
                module.signed_spectrum_enabled = signed and removed != "signed"
            evaluated = evaluate_pgqenn_graph_heads(model, batch)
            probability_delta = float(
                torch.mean(torch.abs(evaluated["probabilities"] - complete_probabilities))
            )
            rows.append(
                {
                    "seed": int(seed),
                    "variant": name,
                    "graph_count": evaluated["metrics"]["graph_count"],
                    "accuracy": evaluated["metrics"]["accuracy"],
                    "macro_f1": evaluated["metrics"]["macro_f1"],
                    "cross_entropy": evaluated["metrics"]["cross_entropy"],
                    "mean_probability_delta_from_complete": probability_delta,
                    "nondegenerate_necessity_witness": int(
                        name == "complete" or probability_delta > 0.0
                    ),
                }
            )
    finally:
        for module, (triadic, signed) in zip(modules, original, strict=True):
            module.triadic_streams_enabled = triadic
            module.signed_spectrum_enabled = signed
    return rows


def augment_pgqenn_evaluation(
    model: torch.nn.Module,
    batch: MultimodalBatch,
    evaluation: MultimodalEvaluation,
) -> MultimodalEvaluation:
    """Attach graph metrics and collect split-level evidence."""

    cursor = int(getattr(model, "_pgqenn_evidence_split_cursor", 0))
    split_names = ("train", "validation", "test")
    if cursor >= len(split_names):
        raise RuntimeError("unexpected extra comprehensive PGQENN split evaluation")
    split = split_names[cursor]
    setattr(model, "_pgqenn_evidence_split_cursor", cursor + 1)
    seed = int(getattr(model, "_pgqenn_evidence_seed", -1))
    result = evaluate_pgqenn_graph_heads(model, batch)
    metrics = result["metrics"]
    evaluation.metrics.update(
        {
            "pgqenn_graph_accuracy": metrics["accuracy"],
            "pgqenn_graph_cross_entropy": metrics["cross_entropy"],
            "pgqenn_graph_macro_f1": metrics["macro_f1"],
            "pgqenn_graph_balanced_accuracy": metrics["balanced_accuracy"],
            "pgqenn_graph_ece": metrics["expected_calibration_error"],
            "pgqenn_graph_count": float(metrics["graph_count"]),
        }
    )
    _GRAPH_METRICS.append(
        {
            "seed": seed,
            "split": split,
            "evaluation_scope": "graph_level_modality_node_classification",
            **metrics,
        }
    )
    probabilities = result["probabilities"].detach().cpu()
    labels = result["labels"].detach().cpu()
    predictions = result["predictions"].detach().cpu()
    for graph_index in range(labels.numel()):
        row: dict[str, Any] = {
            "seed": seed,
            "split": split,
            "graph_index": graph_index,
            "true_index": int(labels[graph_index]),
            "predicted_index": int(predictions[graph_index]),
            "confidence": float(probabilities[graph_index].max()),
            "correct": int(predictions[graph_index] == labels[graph_index]),
        }
        for class_index in range(probabilities.shape[-1]):
            row[f"probability_class_{class_index}"] = float(
                probabilities[graph_index, class_index]
            )
        _GRAPH_PREDICTIONS.append(row)
    if split == "test":
        rows = _source_removal_rows(model, batch, seed=seed)
        _SOURCE_REMOVALS.extend(rows)
    setattr(model, "_pgqenn_latest_module_metrics", result["module_metrics"])
    return evaluation


def apply_pgqenn_module_metrics(
    rows: list[dict[str, Any]],
    evaluation: MultimodalEvaluation,
) -> list[dict[str, Any]]:
    """Replace N/A PGQENN entries with explicit graph-level metrics."""

    module_metrics = getattr(
        evaluation.output,
        "_pgqenn_module_metrics",
        None,
    )
    if module_metrics is None:
        module_metrics = []
    for row in rows:
        if row.get("module") != "PGQENN":
            continue
        index = int(row.get("instance", 0))
        if index < len(module_metrics):
            metrics = module_metrics[index]
            row.update(
                {
                    "accuracy": metrics["accuracy"],
                    "macro_f1": metrics["macro_f1"],
                    "cross_entropy": metrics["cross_entropy"],
                    "balanced_accuracy": metrics["balanced_accuracy"],
                    "expected_calibration_error": metrics[
                        "expected_calibration_error"
                    ],
                    "graph_count": metrics["graph_count"],
                    "evaluation_scope": "graph_level_modality_node_classification",
                }
            )
        else:
            row.update(
                {
                    "accuracy": evaluation.metrics["pgqenn_graph_accuracy"],
                    "macro_f1": evaluation.metrics["pgqenn_graph_macro_f1"],
                    "cross_entropy": evaluation.metrics[
                        "pgqenn_graph_cross_entropy"
                    ],
                    "balanced_accuracy": evaluation.metrics[
                        "pgqenn_graph_balanced_accuracy"
                    ],
                    "expected_calibration_error": evaluation.metrics[
                        "pgqenn_graph_ece"
                    ],
                    "graph_count": int(
                        evaluation.metrics["pgqenn_graph_count"]
                    ),
                    "evaluation_scope": "graph_level_modality_node_classification",
                }
            )
    return rows


def attach_latest_module_metrics(
    model: torch.nn.Module,
    evaluation: MultimodalEvaluation,
) -> None:
    metrics = getattr(model, "_pgqenn_latest_module_metrics", None)
    if metrics is not None:
        setattr(evaluation.output, "_pgqenn_module_metrics", metrics)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"PGQENN evidence table is empty: {path.name}")
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _plot_split_metrics(output: Path) -> None:
    splits = ("train", "validation", "test")
    accuracy = [
        mean(
            float(row["accuracy"])
            for row in _GRAPH_METRICS
            if row["split"] == split
        )
        for split in splits
    ]
    cross_entropy = [
        mean(
            float(row["cross_entropy"])
            for row in _GRAPH_METRICS
            if row["split"] == split
        )
        for split in splits
    ]
    figure, axis = plt.subplots(figsize=(7.5, 4.8))
    axis.plot(splits, accuracy, marker="o")
    axis.set_ylim(0.0, 1.05)
    axis.set_ylabel("Graph accuracy")
    axis.set_title("PGQENN train / validation / held-out graph accuracy")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output / "plots" / "pgqenn_graph_accuracy.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(7.5, 4.8))
    axis.plot(splits, cross_entropy, marker="o")
    axis.set_ylabel("Graph cross-entropy")
    axis.set_title("PGQENN train / validation / held-out graph loss")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output / "plots" / "pgqenn_graph_cross_entropy.png", dpi=160)
    plt.close(figure)


def _plot_confusion(output: Path) -> None:
    test_rows = [row for row in _GRAPH_PREDICTIONS if row["split"] == "test"]
    classes = 1 + max(
        max(int(row["true_index"]), int(row["predicted_index"]))
        for row in test_rows
    )
    confusion = torch.zeros((classes, classes), dtype=torch.int64)
    for row in test_rows:
        confusion[int(row["true_index"]), int(row["predicted_index"])] += 1
    figure, axis = plt.subplots(figsize=(5.8, 5.2))
    image = axis.imshow(confusion.numpy(), interpolation="nearest")
    axis.set_xlabel("Predicted graph class")
    axis.set_ylabel("True graph class")
    axis.set_title("PGQENN held-out graph confusion")
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    figure.savefig(output / "plots" / "pgqenn_graph_confusion.png", dpi=160)
    plt.close(figure)


def finalize_pgqenn_graph_evidence(
    output_dir: str | Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    """Write graph evidence and refresh the comprehensive manifest."""

    output = Path(output_dir)
    plots = output / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    _write_csv(output / "pgqenn_graph_metrics.csv", _GRAPH_METRICS)
    _write_csv(output / "pgqenn_graph_predictions.csv", _GRAPH_PREDICTIONS)
    _write_csv(output / "pgqenn_graph_hyperparameters.csv", _HYPERPARAMETERS)
    _write_csv(output / "pgqenn_graph_source_removal.csv", _SOURCE_REMOVALS)
    _plot_split_metrics(output)
    _plot_confusion(output)

    test_rows = [row for row in _GRAPH_METRICS if row["split"] == "test"]
    summary = {
        "schema_version": "1.0",
        "training_status": "validation_selected_ridge_finetuned_all_seeds",
        "validation_status": "ridge_and_temperature_selected_on_validation_only",
        "test_status": "held_out_graphs_evaluated_all_seeds",
        "graph_semantics": "one_aligned_observation_with_named_modality_nodes",
        "mean_test_accuracy": mean(float(row["accuracy"]) for row in test_rows),
        "mean_test_macro_f1": mean(float(row["macro_f1"]) for row in test_rows),
        "mean_test_cross_entropy": mean(
            float(row["cross_entropy"]) for row in test_rows
        ),
        "mean_test_ece": mean(
            float(row["expected_calibration_error"]) for row in test_rows
        ),
        "source_removal_nondegenerate": all(
            int(row["nondegenerate_necessity_witness"]) == 1
            for row in _SOURCE_REMOVALS
        ),
        "closure_claim": "unchanged_open_or_numerical_candidate_as_declared",
    }
    (output / "pgqenn_graph_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    metrics_path = output / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["pgqenn_graph_evaluation"] = summary
    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    configuration_path = output / "configuration.json"
    configuration = json.loads(configuration_path.read_text(encoding="utf-8"))
    configuration["pgqenn_graph_protocol"] = {
        "graph_unit": "one observation",
        "nodes": "named modality tokens",
        "training": "validation-selected ridge graph readout",
        "calibration": "validation-selected temperature",
        "evaluation": "held-out graph classification",
    }
    configuration_path.write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report_path = output / "evaluation_report.md"
    with report_path.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## PGQENN graph training, validation, and evaluation\n\n"
            "Each aligned observation is evaluated as a graph of named modality "
            "nodes; metrics are graph-level rather than a relabelled batch scalar.\n\n"
            f"- Mean held-out graph accuracy: {summary['mean_test_accuracy']:.6f}\n"
            f"- Mean held-out graph macro F1: {summary['mean_test_macro_f1']:.6f}\n"
            f"- Mean held-out graph cross-entropy: {summary['mean_test_cross_entropy']:.6f}\n"
            f"- Mean held-out graph ECE: {summary['mean_test_ece']:.6f}\n"
            f"- Non-degenerate source-removal gates: {summary['source_removal_nondegenerate']}\n"
            "- The graph training evidence does not change PGQENN theorem closure status.\n"
        )

    artifact_paths = sorted(
        path
        for path in output.rglob("*")
        if path.is_file() and path.name != "artifact_manifest.json"
    )
    plot_files = sorted(plots.glob("*.png"))
    manifest = {
        "schema_version": "2.1",
        "artifact_count": len(artifact_paths),
        "plot_count": len(plot_files),
        "files": [
            {
                "path": str(path.relative_to(output)),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in artifact_paths
        ],
        "pgqenn_graph_evidence": summary,
        "claim_boundary": metrics["claim_boundary"],
    }
    (output / "artifact_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report.update(
        {
            "artifact_count": manifest["artifact_count"],
            "plot_count": manifest["plot_count"],
            "pgqenn_graph_training_status": summary["training_status"],
            "pgqenn_graph_validation_status": summary["validation_status"],
            "pgqenn_graph_test_status": summary["test_status"],
            "pgqenn_graph_mean_test_accuracy": summary["mean_test_accuracy"],
            "pgqenn_graph_mean_test_macro_f1": summary["mean_test_macro_f1"],
            "pgqenn_graph_source_removal_nondegenerate": summary[
                "source_removal_nondegenerate"
            ],
        }
    )
    return report
