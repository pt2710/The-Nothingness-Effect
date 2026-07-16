"""SOInet-coupled evaluation for the six observable AI capabilities.

Task heads are fitted on meta-states emitted by the real QENN -> PGQENN ->
SOInet chain.  Train, validation, and test fixtures use distinct seeds or held
out coordinates.  No nearest-prototype classifier is used to produce the
reported classification scores.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import torch
import torch.nn.functional as functional

from the_nothingness_effect.artificial_intelligence.shared.capability_fixtures import (
    COLOR_LABELS,
    COLOR_PROTOTYPES,
    SOUND_LABELS,
    SOUND_PROTOTYPE_FREQUENCIES,
    color_clone_image,
    color_images,
    sound_clone_waveform,
    tone_batch,
)
from the_nothingness_effect.artificial_intelligence.soinets.model import SOInetModel


CLASSIFICATION_CAPABILITIES = {
    "color_classification",
    "sound_classification",
    "bidirectional_color_classification",
    "bidirectional_sound_classification",
}


@dataclass(frozen=True)
class CapabilityDataset:
    train_samples: torch.Tensor
    train_targets: torch.Tensor
    validation_samples: torch.Tensor
    validation_targets: torch.Tensor
    test_samples: torch.Tensor
    test_targets: torch.Tensor
    task_type: str
    labels: tuple[str, ...] = ()
    reconstruction_shape: tuple[int, ...] = ()


@dataclass(frozen=True)
class SOInetCapabilityEvaluation:
    rows: list[dict[str, Any]]
    metrics: dict[str, float]
    residuals: list[float]
    closure_status: str
    payload: dict[str, Any]
    checkpoint: dict[str, Any]


def _classification_dataset(
    capability: str, *, seed: int, simulation: bool
) -> CapabilityDataset:
    color = "color" in capability
    train_per_class = 2 if simulation else 1
    test_per_class = 2 if simulation else 1
    if color:
        train, train_targets = color_images(
            seed=seed, samples_per_class=train_per_class, image_size=12
        )
        validation, validation_targets = color_images(
            seed=seed + 10_003, samples_per_class=1, image_size=13
        )
        test, test_targets = color_images(
            seed=seed + 20_011,
            samples_per_class=test_per_class,
            image_size=14,
        )
        return CapabilityDataset(
            train,
            train_targets,
            validation,
            validation_targets,
            test,
            test_targets,
            "classification",
            COLOR_LABELS,
        )
    train, train_targets = tone_batch(
        seed=seed,
        samples_per_class=train_per_class,
        sample_count=512,
    )
    validation, validation_targets = tone_batch(
        seed=seed + 10_003, samples_per_class=1, sample_count=640
    )
    test, test_targets = tone_batch(
        seed=seed + 20_011,
        samples_per_class=test_per_class,
        sample_count=768,
    )
    return CapabilityDataset(
        train,
        train_targets,
        validation,
        validation_targets,
        test,
        test_targets,
        "classification",
        SOUND_LABELS,
    )


def _regression_dataset(
    capability: str, *, seed: int, simulation: bool
) -> CapabilityDataset:
    generator = torch.Generator().manual_seed(seed)
    train_count = 16 if simulation else 8
    validation_count = 8 if simulation else 4
    test_count = 8 if simulation else 4
    total = train_count + validation_count + test_count
    if capability == "color_cloning":
        image = color_clone_image(image_size=18 if simulation else 12)
        height, width, _ = image.shape
        x, y = torch.meshgrid(
            torch.linspace(0.0, 1.0, height),
            torch.linspace(0.0, 1.0, width),
            indexing="ij",
        )
        samples = torch.cat(
            (
                x.reshape(-1, 1),
                y.reshape(-1, 1),
                image.reshape(-1, 3),
            ),
            dim=1,
        )
        order = torch.randperm(len(samples), generator=generator)[:total]
        selected = samples[order]
        targets = selected[:, 2:]
        return CapabilityDataset(
            selected[:train_count],
            targets[:train_count],
            selected[train_count : train_count + validation_count],
            targets[train_count : train_count + validation_count],
            selected[-test_count:],
            targets[-test_count:],
            "regression",
            reconstruction_shape=tuple(image.shape),
        )
    waveform = sound_clone_waveform(sample_count=512 if simulation else 256)
    time = torch.linspace(0.0, 1.0, len(waveform))
    derivative = torch.gradient(waveform)[0]
    samples = torch.stack((time, waveform, derivative), dim=-1)
    order = torch.randperm(len(samples), generator=generator)[:total]
    selected = samples[order]
    targets = selected[:, 1:2]
    return CapabilityDataset(
        selected[:train_count],
        targets[:train_count],
        selected[train_count : train_count + validation_count],
        targets[train_count : train_count + validation_count],
        selected[-test_count:],
        targets[-test_count:],
        "regression",
        reconstruction_shape=(len(waveform),),
    )


def capability_dataset(
    capability: str, *, seed: int, simulation: bool
) -> CapabilityDataset:
    if capability in CLASSIFICATION_CAPABILITIES:
        return _classification_dataset(capability, seed=seed, simulation=simulation)
    if capability in {"color_cloning", "sound_cloning"}:
        return _regression_dataset(capability, seed=seed, simulation=simulation)
    raise ValueError(f"unknown SOInet capability {capability!r}")


def _normalize(vector: torch.Tensor) -> torch.Tensor:
    vector = vector.to(dtype=torch.float32).reshape(-1)
    minimum = vector.min()
    maximum = vector.max()
    return (vector - minimum) / (maximum - minimum).clamp_min(1e-6)


def _color_summary(image: torch.Tensor) -> torch.Tensor:
    pixels = image.reshape(-1, 3)
    mean = pixels.mean(dim=0)
    std = pixels.std(dim=0, unbiased=False)
    luminance = (pixels * torch.tensor((0.2126, 0.7152, 0.0722))).sum(dim=-1)
    chroma = pixels.max(dim=-1).values - pixels.min(dim=-1).values
    return torch.cat((mean, std, luminance.mean().reshape(1), chroma.mean().reshape(1)))


def _sound_summary(waveform: torch.Tensor) -> torch.Tensor:
    spectrum = torch.fft.rfft(waveform, norm="ortho").abs()
    edges = torch.linspace(0, spectrum.numel(), 7, dtype=torch.long)
    bands = []
    for start, end in zip(edges[:-1], edges[1:], strict=True):
        segment = spectrum[int(start) : max(int(end), int(start) + 1)]
        bands.append(segment.square().mean().sqrt())
    rms = waveform.square().mean().sqrt()
    zero_crossing = (waveform[:-1] * waveform[1:] < 0).float().mean()
    return torch.stack((*bands, rms, zero_crossing))


def _sample_summary(capability: str, sample: torch.Tensor) -> torch.Tensor:
    if "color" in capability and "cloning" not in capability:
        return _color_summary(sample)
    if "sound" in capability and "cloning" not in capability:
        return _sound_summary(sample)
    if capability == "color_cloning":
        x, y, r, g, b = sample
        return torch.stack((x, y, r, g, b, x * y, x.square(), y.square()))
    time, amplitude, derivative = sample
    return torch.stack(
        (
            time,
            amplitude.abs(),
            derivative.abs(),
            torch.sin(2.0 * torch.pi * time).abs(),
            torch.cos(2.0 * torch.pi * time).abs(),
            time.square(),
            amplitude.square(),
            derivative.square(),
        )
    )


def _graphs(capability: str, sample: torch.Tensor, *, nodes: int = 4) -> tuple[torch.Tensor, torch.Tensor]:
    base = 0.15 + 0.85 * _normalize(_sample_summary(capability, sample))
    rows = []
    for index in range(nodes):
        rolled = torch.roll(base, shifts=index)
        position = (index + 1.0) / nodes
        rows.append(
            torch.clamp(
                rolled * (0.85 + 0.1 * position)
                + 0.03 * torch.sin(torch.arange(8) + position).abs(),
                min=1e-4,
            )
        )
    qenn = torch.stack(rows)
    pgqenn = torch.clamp(
        0.88 * qenn.flip(0) + 0.12 * qenn.mean(dim=0, keepdim=True),
        min=1e-4,
    )
    return qenn, pgqenn


def _extract_split(
    model: SOInetModel,
    capability: str,
    samples: torch.Tensor,
) -> tuple[torch.Tensor, tuple[Any, ...]]:
    outputs = []
    features = []
    model.eval()
    with torch.no_grad():
        for sample in samples:
            qenn, pgqenn = _graphs(capability, sample)
            output = model(qenn, pgqenn)
            outputs.append(output)
            features.append(output.meta_state)
    return torch.stack(features), tuple(outputs)


def _design(features: torch.Tensor) -> torch.Tensor:
    ones = torch.ones((features.shape[0], 1), dtype=features.dtype)
    return torch.cat((features, ones), dim=1)


def _ridge_head(
    features: torch.Tensor, targets: torch.Tensor, *, output_dim: int, ridge: float = 1e-3
) -> torch.Tensor:
    design = _design(features)
    if targets.ndim == 1:
        target_matrix = functional.one_hot(targets, output_dim).to(dtype=features.dtype)
    else:
        target_matrix = targets.to(dtype=features.dtype)
    identity = torch.eye(design.shape[1], dtype=features.dtype)
    identity[-1, -1] = 0.0
    return torch.linalg.solve(
        design.T @ design + ridge * identity,
        design.T @ target_matrix,
    )


def _classification_metrics(
    features: torch.Tensor, targets: torch.Tensor, head: torch.Tensor
) -> tuple[dict[str, float], torch.Tensor, torch.Tensor, torch.Tensor]:
    logits = _design(features) @ head
    probabilities = torch.softmax(logits, dim=-1)
    predictions = probabilities.argmax(dim=-1)
    accuracy = (predictions == targets).float().mean()
    loss = functional.cross_entropy(logits, targets)
    confidence = probabilities.max(dim=-1).values.mean()
    return (
        {
            "accuracy": float(accuracy),
            "loss": float(loss),
            "mean_confidence": float(confidence),
        },
        logits,
        probabilities,
        predictions,
    )


def _regression_metrics(
    features: torch.Tensor, targets: torch.Tensor, head: torch.Tensor
) -> tuple[dict[str, float], torch.Tensor]:
    prediction = _design(features) @ head
    error = prediction - targets
    rmse = error.square().mean().sqrt()
    mae = error.abs().mean()
    signal_energy = targets.square().sum()
    error_energy = error.square().sum().clamp_min(1e-30)
    snr = 10.0 * torch.log10(signal_energy.clamp_min(1e-30) / error_energy)
    return {"rmse": float(rmse), "mae": float(mae), "snr_db": float(snr)}, prediction


def _closure_summary(outputs: tuple[Any, ...]) -> tuple[list[float], str, tuple[str, ...]]:
    norms = [
        float(torch.linalg.vector_norm(torch.stack(tuple(output.residuals.values()))))
        for output in outputs
    ]
    statuses = tuple(output.closure_status.value for output in outputs)
    status = "numerical_candidate" if all(item == "numerical_candidate" for item in statuses) else "open"
    return norms, status, statuses


def _bidirectional_payload(
    capability: str,
    probabilities: torch.Tensor,
    samples: torch.Tensor,
) -> dict[str, Any]:
    if capability == "bidirectional_color_classification":
        reconstructed = probabilities @ COLOR_PROTOTYPES
        source = samples.reshape(samples.shape[0], -1, 3).mean(dim=1)
        rmse = (reconstructed - source).square().mean().sqrt()
        roundtrip = torch.cdist(reconstructed, COLOR_PROTOTYPES).argmin(dim=-1)
        return {
            "reconstructed_modality": reconstructed,
            "modality_rmse": float(rmse),
            "roundtrip_predictions": roundtrip,
        }
    frequencies = probabilities @ SOUND_PROTOTYPE_FREQUENCIES
    sample_count = samples.shape[-1]
    time = torch.arange(sample_count, dtype=torch.float32) / 8000.0
    reconstructed = 0.6 * torch.sin(2.0 * torch.pi * frequencies[:, None] * time)
    rmse = (reconstructed - samples).square().mean().sqrt()
    roundtrip = torch.cdist(frequencies[:, None], SOUND_PROTOTYPE_FREQUENCIES[:, None]).argmin(dim=-1)
    return {
        "reconstructed_modality": reconstructed,
        "reconstructed_frequencies": frequencies,
        "modality_rmse": float(rmse),
        "roundtrip_predictions": roundtrip,
    }


def evaluate_capability_with_soinet(
    capability: str,
    *,
    seed: int,
    simulation: bool,
) -> SOInetCapabilityEvaluation:
    dataset = capability_dataset(capability, seed=seed, simulation=simulation)
    torch.manual_seed(seed + 50_021)
    model = SOInetModel(8, 6, 6, qenn_count=1, pgqenn_count=1)
    train_features, train_outputs = _extract_split(
        model, capability, dataset.train_samples
    )
    validation_features, validation_outputs = _extract_split(
        model, capability, dataset.validation_samples
    )
    test_features, test_outputs = _extract_split(
        model, capability, dataset.test_samples
    )
    all_outputs = (*train_outputs, *validation_outputs, *test_outputs)
    residuals, closure_status, statuses = _closure_summary(all_outputs)

    if dataset.task_type == "classification":
        output_dim = len(dataset.labels)
        head = _ridge_head(
            train_features, dataset.train_targets, output_dim=output_dim
        )
        train_metrics, _, _, _ = _classification_metrics(
            train_features, dataset.train_targets, head
        )
        validation_metrics, _, _, _ = _classification_metrics(
            validation_features, dataset.validation_targets, head
        )
        test_metrics, logits, probabilities, predictions = _classification_metrics(
            test_features, dataset.test_targets, head
        )
        metrics = {
            "train_accuracy": train_metrics["accuracy"],
            "validation_accuracy": validation_metrics["accuracy"],
            "accuracy": test_metrics["accuracy"],
            "test_loss": test_metrics["loss"],
            "mean_confidence": test_metrics["mean_confidence"],
            "generalization_gap": train_metrics["accuracy"] - test_metrics["accuracy"],
        }
        payload: dict[str, Any] = {
            "metric_producer": "SOInet",
            "labels": dataset.labels,
            "targets": dataset.test_targets,
            "predictions": predictions,
            "probabilities": probabilities,
            "logits": logits,
            "samples": dataset.test_samples,
            "closure_statuses": statuses,
        }
        if capability.startswith("bidirectional"):
            bidirectional = _bidirectional_payload(
                capability, probabilities, dataset.test_samples
            )
            payload.update(bidirectional)
            roundtrip_accuracy = (
                bidirectional["roundtrip_predictions"] == predictions
            ).float().mean()
            metrics["roundtrip_accuracy"] = float(roundtrip_accuracy)
            metrics["modality_rmse"] = float(bidirectional["modality_rmse"])
        rows = [
            {
                "sample": index,
                "true_index": int(target),
                "true_label": dataset.labels[int(target)],
                "predicted_index": int(prediction),
                "predicted_label": dataset.labels[int(prediction)],
                "confidence": float(probabilities[index].max()),
                "correct": bool(target == prediction),
                "metric_producer": "SOInet",
            }
            for index, (target, prediction) in enumerate(
                zip(dataset.test_targets, predictions, strict=True)
            )
        ]
    else:
        output_dim = dataset.train_targets.shape[-1]
        head = _ridge_head(
            train_features, dataset.train_targets, output_dim=output_dim
        )
        train_metrics, _ = _regression_metrics(
            train_features, dataset.train_targets, head
        )
        validation_metrics, _ = _regression_metrics(
            validation_features, dataset.validation_targets, head
        )
        test_metrics, prediction = _regression_metrics(
            test_features, dataset.test_targets, head
        )
        metrics = {
            "train_rmse": train_metrics["rmse"],
            "validation_rmse": validation_metrics["rmse"],
            "rmse": test_metrics["rmse"],
            "mae": test_metrics["mae"],
            "snr_db": test_metrics["snr_db"],
            "generalization_gap": test_metrics["rmse"] - train_metrics["rmse"],
        }
        payload = {
            "metric_producer": "SOInet",
            "source": dataset.test_targets,
            "clone": prediction,
            "samples": dataset.test_samples,
            "reconstruction_shape": dataset.reconstruction_shape,
            "closure_statuses": statuses,
        }
        rows = [
            {
                "sample": index,
                "target": tuple(float(item) for item in target),
                "prediction": tuple(float(item) for item in estimate),
                "absolute_error": float((estimate - target).abs().mean()),
                "metric_producer": "SOInet",
            }
            for index, (target, estimate) in enumerate(
                zip(dataset.test_targets, prediction, strict=True)
            )
        ]

    checkpoint = {
        "format_version": 1,
        "capability": capability,
        "seed": seed,
        "simulation": simulation,
        "metric_producer": "SOInet",
        "model_state_dict": model.state_dict(),
        "task_head": head,
        "train_samples": len(dataset.train_samples),
        "validation_samples": len(dataset.validation_samples),
        "test_samples": len(dataset.test_samples),
        "metrics": metrics,
        "claim_boundary": (
            "finite synthetic train/validation/test benchmark; not a formal proof "
            "or real-world generalization claim"
        ),
    }
    return SOInetCapabilityEvaluation(
        rows=rows,
        metrics=metrics,
        residuals=residuals,
        closure_status=closure_status,
        payload=payload,
        checkpoint=checkpoint,
    )


def multi_seed_benchmark(
    capabilities: tuple[str, ...],
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    simulation: bool = False,
) -> list[dict[str, Any]]:
    if len(seeds) < 2:
        raise ValueError("multi-seed benchmark requires at least two seeds")
    rows: list[dict[str, Any]] = []
    for capability in capabilities:
        for seed in seeds:
            evaluation = evaluate_capability_with_soinet(
                capability, seed=seed, simulation=simulation
            )
            rows.append(
                {
                    "capability": capability,
                    "seed": seed,
                    "metric_producer": "SOInet",
                    "closure_status": evaluation.closure_status,
                    **evaluation.metrics,
                }
            )
    return rows
