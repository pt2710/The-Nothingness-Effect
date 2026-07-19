"""Typed evaluation and source-removal diagnostics for multimodal TNE models."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import torch
from torch.nn import functional
from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel

from .data import MultimodalBatch
from .model import TNETrainableMultimodalModel, TNETrainableMultimodalOutput


@dataclass(frozen=True)
class MultimodalEvaluation:
    metrics: dict[str, float]
    confusion_matrix: torch.Tensor
    residuals: dict[str, float]
    modality_similarity: torch.Tensor
    reconstruction_rmse: dict[str, float]
    output: TNETrainableMultimodalOutput


def _confusion(labels: torch.Tensor, predictions: torch.Tensor, classes: int) -> torch.Tensor:
    encoded = labels * classes + predictions
    return torch.bincount(encoded, minlength=classes * classes).reshape(classes, classes)


def classification_metrics_from_confusion(confusion: torch.Tensor) -> dict[str, float]:
    """Return zero-safe macro, micro, weighted and balanced metrics."""
    matrix = confusion.to(dtype=torch.float64)
    true_positive = torch.diagonal(matrix)
    support = matrix.sum(dim=1)
    predicted = matrix.sum(dim=0)
    precision = torch.where(predicted > 0, true_positive / predicted, torch.zeros_like(true_positive))
    recall = torch.where(support > 0, true_positive / support, torch.zeros_like(true_positive))
    f1 = torch.where(
        precision + recall > 0,
        2.0 * precision * recall / (precision + recall),
        torch.zeros_like(precision),
    )
    total = matrix.sum().clamp_min(1.0)
    micro = true_positive.sum() / total
    weights = support / total
    return {
        "macro_precision": float(precision.mean()),
        "macro_recall": float(recall.mean()),
        "macro_f1": float(f1.mean()),
        "micro_precision": float(micro),
        "micro_recall": float(micro),
        "micro_f1": float(micro),
        "weighted_f1": float(torch.sum(weights * f1)),
        "balanced_accuracy": float(recall.mean()),
    }


def _expected_calibration_error(
    probabilities: torch.Tensor,
    labels: torch.Tensor,
    bins: int = 5,
) -> float:
    confidence, predictions = probabilities.max(dim=-1)
    total = max(1, labels.numel())
    error = torch.zeros((), dtype=probabilities.dtype)
    edges = torch.linspace(0.0, 1.0, bins + 1)
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if bool(mask.any()):
            accuracy = (predictions[mask] == labels[mask]).float().mean()
            error = error + mask.float().sum() / total * torch.abs(
                accuracy - confidence[mask].mean()
            )
    return float(error)


def _precision_metrics(output: TNETrainableMultimodalOutput) -> dict[str, float]:
    precision = output.energy_precision
    if precision is None:
        return {}
    normalizer = math.log(float(precision.shape[-1])) if precision.shape[-1] > 1 else 1.0
    entropy = -torch.sum(
        precision * torch.log(precision.clamp_min(1e-9)), dim=-1
    ) / normalizer
    return {
        "mean_modality_precision_entropy": float(entropy.mean()),
        "minimum_modality_precision": float(precision.min()),
        "maximum_modality_precision": float(precision.max()),
    }


def _qenn_metrics(
    output: TNETrainableMultimodalOutput,
    labels: torch.Tensor,
) -> dict[str, float]:
    soinet = output.backbone_output.soinet_output
    if soinet is None or not soinet.qenn_outputs:
        return {
            "mean_qenn_accuracy": 0.0,
            "mean_qenn_cross_entropy": 0.0,
        }
    accuracies: list[torch.Tensor] = []
    losses: list[torch.Tensor] = []
    for qenn in soinet.qenn_outputs:
        if qenn.readout.ndim != 2 or qenn.readout.shape[0] != labels.shape[0]:
            raise RuntimeError("QENN evaluation readout must be per-sample")
        losses.append(functional.cross_entropy(qenn.readout, labels))
        accuracies.append((qenn.readout.argmax(dim=-1) == labels).float().mean())
    return {
        "mean_qenn_accuracy": float(torch.stack(accuracies).mean()),
        "mean_qenn_cross_entropy": float(torch.stack(losses).mean()),
    }


def _calibration_temperature(model: TNETrainableMultimodalModel) -> float:
    value = getattr(model, "calibration_temperature", 1.0)
    if isinstance(value, torch.Tensor):
        value = float(value.detach().cpu())
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise RuntimeError("calibration temperature must be finite and positive")
    return value


def evaluate_multimodal_model(
    model: TNETrainableMultimodalModel,
    batch: MultimodalBatch,
) -> MultimodalEvaluation:
    batch.validate()
    model.eval()
    with torch.no_grad():
        output = model(batch.modalities)
    temperature = _calibration_temperature(model)
    if temperature != 1.0:
        output.readout = output.readout / temperature
        output.observation = torch.softmax(output.readout, dim=-1)
    probabilities = output.observation
    predictions = probabilities.argmax(dim=-1)
    classes = output.readout.shape[-1]
    confusion = _confusion(batch.labels, predictions, classes)
    targets = output.backbone_output.modality_tokens
    reconstruction = output.reconstructed_fused_tokens
    reconstruction_rmse = {
        name: float(torch.sqrt(torch.mean((reconstruction - targets[:, index, :]) ** 2)))
        for index, name in enumerate(output.backbone_output.modality_names)
    }
    modality_means = targets.mean(dim=0)
    normalized = functional.normalize(modality_means, dim=-1)
    similarity = normalized @ normalized.T
    one_hot = functional.one_hot(batch.labels, num_classes=classes).to(probabilities.dtype)
    if output.global_rbm_state is None:
        raise RuntimeError("multimodal evaluation requires the global energy state")
    metrics = {
        "accuracy": float((predictions == batch.labels).float().mean()),
        "cross_entropy": float(functional.cross_entropy(output.readout, batch.labels)),
        "brier_score": float(torch.mean((probabilities - one_hot) ** 2)),
        "mean_confidence": float(probabilities.max(dim=-1).values.mean()),
        "predictive_entropy": float(
            torch.mean(-torch.sum(probabilities * torch.log(probabilities.clamp_min(1e-9)), dim=-1))
        ),
        "expected_calibration_error": _expected_calibration_error(probabilities, batch.labels),
        "calibration_temperature": temperature,
        "mean_reconstruction_rmse": sum(reconstruction_rmse.values()) / len(reconstruction_rmse),
        "mean_global_rbm_free_energy": float(output.global_rbm_state.free_energy.mean()),
        "global_rbm_reconstruction_rmse": float(output.global_rbm_state.reconstruction_residual),
        "active_clusters": float(output.cluster_state.active_clusters),
        **_qenn_metrics(output, batch.labels),
        **_precision_metrics(output),
        **classification_metrics_from_confusion(confusion),
    }
    if output.local_rbm_state is not None:
        metrics.update(
            {
                "mean_local_rbm_free_energy": float(output.local_rbm_state.free_energy.mean()),
                "local_rbm_reconstruction_rmse": float(output.local_rbm_state.reconstruction_residual),
            }
        )
    return MultimodalEvaluation(
        metrics,
        confusion,
        {name: float(value.detach().cpu()) for name, value in output.residuals.items()},
        similarity,
        reconstruction_rmse,
        output,
    )


def evaluate_source_removals(
    model: TNETrainableMultimodalModel,
    batch: MultimodalBatch,
) -> list[dict[str, Any]]:
    """Evaluate named ablations without redefining the canonical implementation."""
    rows: list[dict[str, Any]] = []
    raw_observer = model.backbone.raw_observer
    elastic_dubler = model.backbone.elastic_dubler
    axis_enabled = model.axis_network_enabled
    energy_enabled = model.energy_regulation_enabled
    cluster_enabled = model.cluster_context_enabled
    pgqenn_models = tuple(module for module in model.modules() if isinstance(module, PGQENNModel))
    signed_states = tuple(module.signed_spectrum_enabled for module in pgqenn_models)
    variants = (
        ("complete", raw_observer, elastic_dubler, True, True, True, True),
        ("observation_removed", None, elastic_dubler, True, True, True, True),
        ("elastic_dubler_removed", raw_observer, None, True, True, True, True),
        ("modality_axes_removed", raw_observer, elastic_dubler, False, True, True, True),
        ("precision_regulator_removed", raw_observer, elastic_dubler, True, False, True, True),
        ("cluster_context_removed", raw_observer, elastic_dubler, True, True, False, True),
        ("signed_spectrum_removed", raw_observer, elastic_dubler, True, True, True, False),
        ("observation_and_dubler_removed", None, None, True, True, True, True),
    )
    try:
        for name, observer, dubler, axes, energy, clusters, signed in variants:
            model.backbone.raw_observer = observer
            model.backbone.elastic_dubler = dubler
            model.axis_network_enabled = axes
            model.energy_regulation_enabled = energy
            model.cluster_context_enabled = clusters
            for pgqenn in pgqenn_models:
                pgqenn.signed_spectrum_enabled = signed
            evaluation = evaluate_multimodal_model(model, batch)
            rows.append({"variant": name, **evaluation.metrics})
    finally:
        model.backbone.raw_observer = raw_observer
        model.backbone.elastic_dubler = elastic_dubler
        model.axis_network_enabled = axis_enabled
        model.energy_regulation_enabled = energy_enabled
        model.cluster_context_enabled = cluster_enabled
        for pgqenn, signed in zip(pgqenn_models, signed_states, strict=True):
            pgqenn.signed_spectrum_enabled = signed
    return rows
