"""Data, metric and ablation helpers for comprehensive TNE AI evaluation."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

import torch

from .multimodal.data import MultimodalBatch, MultimodalDataset
from .multimodal.evaluation import (
    MultimodalEvaluation,
    classification_metrics_from_confusion,
    evaluate_multimodal_model,
)
from .multimodal.geometric_model import TNEGeometricMultimodalModel

CLAIM_BOUNDARY = (
    "deterministic synthetic multi-sample evidence with controlled variance; "
    "not real-world empirical validation and not a formal theorem proof"
)
STREAM_NAMES = (
    "pure_events",
    "odd_primes",
    "composite_odds",
    "composite_evens_of_odd",
)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(
            {key: "" if row.get(key) is None else row.get(key) for key in fieldnames}
            for row in rows
        )


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def status_value(value: object) -> str:
    return str(getattr(value, "value", value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def class_rows(
    seed: int,
    split: str,
    confusion: torch.Tensor,
    class_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    matrix = confusion.to(torch.float64)
    support = matrix.sum(dim=1)
    predicted = matrix.sum(dim=0)
    true_positive = torch.diagonal(matrix)
    precision = torch.where(
        predicted > 0,
        true_positive / predicted,
        torch.zeros_like(true_positive),
    )
    recall = torch.where(
        support > 0,
        true_positive / support,
        torch.zeros_like(true_positive),
    )
    f1 = torch.where(
        precision + recall > 0,
        2.0 * precision * recall / (precision + recall),
        torch.zeros_like(precision),
    )
    return [
        {
            "seed": seed,
            "split": split,
            "class_index": index,
            "class_name": name,
            "support": int(support[index]),
            "predicted_count": int(predicted[index]),
            "true_positive": int(true_positive[index]),
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1": float(f1[index]),
        }
        for index, name in enumerate(class_names)
    ]


def prediction_rows(
    seed: int,
    split: str,
    evaluation: MultimodalEvaluation,
    labels: torch.Tensor,
    class_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    probabilities = evaluation.output.observation.detach().cpu()
    predictions = probabilities.argmax(dim=-1)
    confidence = probabilities.max(dim=-1).values
    entropy = -torch.sum(
        probabilities * torch.log(probabilities.clamp_min(1e-9)),
        dim=-1,
    )
    rows: list[dict[str, Any]] = []
    for index in range(labels.numel()):
        row: dict[str, Any] = {
            "seed": seed,
            "split": split,
            "sample_index": index,
            "true_index": int(labels[index]),
            "true_class": class_names[int(labels[index])],
            "predicted_index": int(predictions[index]),
            "predicted_class": class_names[int(predictions[index])],
            "confidence": float(confidence[index]),
            "predictive_entropy": float(entropy[index]),
            "correct": int(predictions[index] == labels[index]),
        }
        for class_index, class_name in enumerate(class_names):
            row[f"probability_{class_name}"] = float(
                probabilities[index, class_index]
            )
        rows.append(row)
    return rows


def geometry_rows(
    seed: int,
    split: str,
    evaluation: MultimodalEvaluation,
    labels: torch.Tensor,
) -> list[dict[str, Any]]:
    axis = evaluation.output.axis_state
    if axis is None:
        raise RuntimeError("geometric evaluation requires axis state")
    coordinates = axis.geometric_coordinates.detach().cpu()
    duals = axis.dual_coordinates.detach().cpu()
    horizons = axis.observer_horizon.detach().cpu()
    streams = axis.mpl_tc_stream_weights.detach().cpu()
    growth = axis.mpl_tc_growth_vectors.detach().cpu()
    rows: list[dict[str, Any]] = []
    for sample_index in range(coordinates.shape[0]):
        for modality_index, modality in enumerate(axis.modality_names):
            row: dict[str, Any] = {
                "seed": seed,
                "split": split,
                "sample_index": sample_index,
                "label": int(labels[sample_index]),
                "modality": modality,
                "x": float(coordinates[sample_index, modality_index, 0]),
                "y": float(coordinates[sample_index, modality_index, 1]),
                "z": float(coordinates[sample_index, modality_index, 2]),
                "dual_x": float(duals[sample_index, modality_index, 0]),
                "dual_y": float(duals[sample_index, modality_index, 1]),
                "dual_z": float(duals[sample_index, modality_index, 2]),
                "observer_horizon": float(horizons[sample_index, modality_index]),
                "growth_x": float(growth[sample_index, modality_index, 0]),
                "growth_y": float(growth[sample_index, modality_index, 1]),
                "growth_z": float(growth[sample_index, modality_index, 2]),
            }
            for stream_index, stream_name in enumerate(STREAM_NAMES):
                row[f"stream_{stream_name}"] = float(
                    streams[sample_index, modality_index, stream_index]
                )
            rows.append(row)
    return rows


def dataset_rows(dataset: MultimodalDataset) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in ("train", "validation", "test"):
        batch = getattr(dataset, split)
        for sample_index in range(batch.labels.numel()):
            row: dict[str, Any] = {
                "split": split,
                "sample_index": sample_index,
                "label": int(batch.labels[sample_index]),
                "class_name": dataset.class_names[int(batch.labels[sample_index])],
            }
            for modality, value in sorted(batch.modalities.items()):
                flattened = value[sample_index].reshape(-1).to(torch.float64)
                row[f"{modality}_mean"] = float(flattened.mean())
                row[f"{modality}_std"] = float(torch.std(flattened, unbiased=False))
                row[f"{modality}_minimum"] = float(flattened.min())
                row[f"{modality}_maximum"] = float(flattened.max())
            rows.append(row)
    return rows


def module_rows(
    seed: int,
    evaluation: MultimodalEvaluation,
    labels: torch.Tensor,
) -> list[dict[str, Any]]:
    output = evaluation.output
    soinet = output.backbone_output.soinet_output
    rows: list[dict[str, Any]] = []
    for index, qenn in enumerate(soinet.qenn_outputs):
        probabilities = qenn.observation.detach()
        predictions = probabilities.argmax(dim=-1)
        confusion = torch.bincount(
            labels * probabilities.shape[-1] + predictions,
            minlength=probabilities.shape[-1] ** 2,
        ).reshape(probabilities.shape[-1], probabilities.shape[-1])
        metrics = classification_metrics_from_confusion(confusion)
        residual = math.sqrt(
            sum(float(torch.abs(value).detach()) ** 2 for value in qenn.residuals.values())
        )
        rows.append(
            {
                "seed": seed,
                "module": "QENN",
                "instance": index,
                "accuracy": float((predictions == labels).float().mean()),
                "macro_f1": metrics["macro_f1"],
                "mean_confidence": float(probabilities.max(dim=-1).values.mean()),
                "predictive_entropy": float(
                    torch.mean(
                        -torch.sum(
                            probabilities * torch.log(probabilities.clamp_min(1e-9)),
                            dim=-1,
                        )
                    )
                ),
                "residual_l2": residual,
                "closure_status": status_value(qenn.closure_status),
            }
        )
    for index, pgqenn in enumerate(soinet.pgqenn_outputs):
        probabilities = pgqenn.observation.detach()
        residual = math.sqrt(
            sum(float(torch.abs(value).detach()) ** 2 for value in pgqenn.residuals.values())
        )
        rows.append(
            {
                "seed": seed,
                "module": "PGQENN",
                "instance": index,
                "accuracy": None,
                "macro_f1": None,
                "mean_confidence": float(probabilities.max(dim=-1).values.mean()),
                "predictive_entropy": float(
                    torch.mean(
                        -torch.sum(
                            probabilities * torch.log(probabilities.clamp_min(1e-9)),
                            dim=-1,
                        )
                    )
                ),
                "residual_l2": residual,
                "triadic_source_removal_delta": float(
                    pgqenn.triadic_stream_source_removal_delta.detach()
                ),
                "signed_spectrum_source_removal_delta": float(
                    pgqenn.signed_spectrum_source_removal_delta.detach()
                ),
                "closure_status": status_value(pgqenn.closure_status),
            }
        )
    residual = math.sqrt(
        sum(float(torch.abs(value).detach()) ** 2 for value in soinet.residuals.values())
    )
    rows.append(
        {
            "seed": seed,
            "module": "SOInets",
            "instance": 0,
            "accuracy": evaluation.metrics["accuracy"],
            "macro_f1": evaluation.metrics["macro_f1"],
            "mean_confidence": evaluation.metrics["mean_confidence"],
            "predictive_entropy": evaluation.metrics["predictive_entropy"],
            "residual_l2": residual,
            "closure_status": status_value(soinet.closure_status),
        }
    )
    return rows


def extended_metrics(evaluation: MultimodalEvaluation) -> dict[str, float]:
    axis = evaluation.output.axis_state
    coordinates = axis.geometric_coordinates
    modality_means = coordinates.mean(dim=0)
    pairwise = (
        torch.pdist(modality_means)
        if modality_means.shape[0] > 1
        else torch.zeros(1, dtype=coordinates.dtype, device=coordinates.device)
    )
    stream_entropy = -torch.sum(
        axis.mpl_tc_stream_weights
        * torch.log(axis.mpl_tc_stream_weights.clamp_min(1e-9)),
        dim=-1,
    ).mean()
    return {
        "geometric_coordinate_spread": float(
            torch.std(coordinates.reshape(-1, 3), dim=0, unbiased=False).mean()
        ),
        "mean_modality_separation": float(pairwise.mean()),
        "minimum_modality_separation": float(pairwise.min()),
        "mean_observer_horizon": float(axis.observer_horizon.mean()),
        "negative_observer_horizon_fraction": float(
            (axis.observer_horizon < 0).float().mean()
        ),
        "mpl_tc_stream_entropy": float(stream_entropy),
        "dual_involution_residual": float(
            torch.max(torch.abs(axis.dual_coordinates + coordinates))
        ),
    }


def source_removals(
    model: TNEGeometricMultimodalModel,
    batch: MultimodalBatch,
    seed: int,
) -> list[dict[str, Any]]:
    original = {
        "observer": model.backbone.raw_observer,
        "dubler": model.backbone.elastic_dubler,
        "axes": model.axis_network_enabled,
        "energy": model.energy_regulation_enabled,
        "cluster": model.cluster_context_enabled,
        "geometry": model.geometric_context_enabled,
        "dual": model.dual_context_enabled,
        "horizon": model.observer_horizon_growth_enabled,
    }
    variants = (
        ("complete", {}),
        ("observation_removed", {"observer": None}),
        ("elastic_dubler_removed", {"dubler": None}),
        ("modality_axes_removed", {"axes": False}),
        ("rbm_regulator_removed", {"energy": False}),
        ("cluster_context_removed", {"cluster": False}),
        ("geometry_removed", {"geometry": False}),
        ("dual_context_removed", {"dual": False}),
        ("observer_horizon_growth_removed", {"horizon": False}),
        (
            "geometry_dual_horizon_removed",
            {"geometry": False, "dual": False, "horizon": False},
        ),
    )
    rows: list[dict[str, Any]] = []
    try:
        for name, changes in variants:
            state = {**original, **changes}
            model.backbone.raw_observer = state["observer"]
            model.backbone.elastic_dubler = state["dubler"]
            model.axis_network_enabled = state["axes"]
            model.energy_regulation_enabled = state["energy"]
            model.cluster_context_enabled = state["cluster"]
            model.geometric_context_enabled = state["geometry"]
            model.dual_context_enabled = state["dual"]
            model.observer_horizon_growth_enabled = state["horizon"]
            evaluation = evaluate_multimodal_model(model, batch)
            rows.append(
                {
                    "seed": seed,
                    "variant": name,
                    **evaluation.metrics,
                    **extended_metrics(evaluation),
                }
            )
    finally:
        model.backbone.raw_observer = original["observer"]
        model.backbone.elastic_dubler = original["dubler"]
        model.axis_network_enabled = original["axes"]
        model.energy_regulation_enabled = original["energy"]
        model.cluster_context_enabled = original["cluster"]
        model.geometric_context_enabled = original["geometry"]
        model.dual_context_enabled = original["dual"]
        model.observer_horizon_growth_enabled = original["horizon"]
    return rows


def aggregate_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = {}
    ignored = {"seed", "split", "closure_status"}
    for row in rows:
        for key, value in row.items():
            if key in ignored or value is None or isinstance(value, str):
                continue
            grouped.setdefault((str(row["split"]), key), []).append(float(value))
    return [
        {
            "split": split,
            "metric": metric,
            "count": len(values),
            "mean": mean(values),
            "population_std": pstdev(values),
            "minimum": min(values),
            "maximum": max(values),
        }
        for (split, metric), values in sorted(grouped.items())
    ]


def calibration_rows(
    predictions: list[dict[str, Any]],
    bins: int = 10,
) -> list[dict[str, Any]]:
    test_rows = [row for row in predictions if row["split"] == "test"]
    rows: list[dict[str, Any]] = []
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        selected = [
            row
            for row in test_rows
            if lower < float(row["confidence"]) <= upper
        ]
        rows.append(
            {
                "bin": index,
                "lower": lower,
                "upper": upper,
                "count": len(selected),
                "mean_confidence": (
                    mean(float(row["confidence"]) for row in selected)
                    if selected
                    else 0.0
                ),
                "accuracy": (
                    mean(float(row["correct"]) for row in selected)
                    if selected
                    else 0.0
                ),
            }
        )
    return rows
