"""Larger held-out SOInet benchmark profile.

The normal capability runs remain small deterministic smoke tests.  This module
provides a distinct, reproducible profile with materially larger disjoint
train, validation, and test splits.  Metrics are still produced only from
SOInet meta-states and a fitted finite task head.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch

from the_nothingness_effect.artificial_intelligence.shared.capability_fixtures import (
    COLOR_LABELS,
    SOUND_LABELS,
    color_clone_image,
    color_images,
    sound_clone_waveform,
    tone_batch,
)
from the_nothingness_effect.artificial_intelligence.shared.soinet_capability_runtime import (
    CLASSIFICATION_CAPABILITIES,
    CapabilityDataset,
    _bidirectional_payload,
    _classification_metrics,
    _closure_summary,
    _extract_split,
    _regression_metrics,
    _ridge_head,
)
from the_nothingness_effect.artificial_intelligence.soinets.model import SOInetModel


PROFILE_NAME = "larger_generalization_benchmark_v1"
CLAIM_BOUNDARY = (
    "larger finite synthetic held-out benchmark; not a real-world "
    "generalization claim or formal proof"
)


@dataclass(frozen=True)
class LargeBenchmarkEvaluation:
    row: dict[str, Any]
    checkpoint: dict[str, Any]


def large_capability_dataset(capability: str, *, seed: int) -> CapabilityDataset:
    """Build larger disjoint splits than the regular smoke capability suite."""

    if capability in CLASSIFICATION_CAPABILITIES:
        if "color" in capability:
            train, train_targets = color_images(
                seed=seed,
                samples_per_class=4,
                image_size=16,
            )
            validation, validation_targets = color_images(
                seed=seed + 10_003,
                samples_per_class=2,
                image_size=18,
            )
            test, test_targets = color_images(
                seed=seed + 20_011,
                samples_per_class=2,
                image_size=20,
            )
            labels = COLOR_LABELS
        else:
            train, train_targets = tone_batch(
                seed=seed,
                samples_per_class=4,
                sample_count=1024,
            )
            validation, validation_targets = tone_batch(
                seed=seed + 10_003,
                samples_per_class=2,
                sample_count=1280,
            )
            test, test_targets = tone_batch(
                seed=seed + 20_011,
                samples_per_class=2,
                sample_count=1536,
            )
            labels = SOUND_LABELS
        return CapabilityDataset(
            train,
            train_targets,
            validation,
            validation_targets,
            test,
            test_targets,
            "classification",
            labels,
        )

    generator = torch.Generator().manual_seed(seed)
    train_count = 24
    validation_count = 8
    test_count = 8
    total = train_count + validation_count + test_count
    if capability == "color_cloning":
        image = color_clone_image(image_size=24)
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
        reconstruction_shape = tuple(image.shape)
    elif capability == "sound_cloning":
        waveform = sound_clone_waveform(sample_count=1024)
        time = torch.linspace(0.0, 1.0, len(waveform))
        derivative = torch.gradient(waveform)[0]
        samples = torch.stack((time, waveform, derivative), dim=-1)
        order = torch.randperm(len(samples), generator=generator)[:total]
        selected = samples[order]
        targets = selected[:, 1:2]
        reconstruction_shape = (len(waveform),)
    else:
        raise ValueError(f"unknown large SOInet benchmark capability {capability!r}")

    return CapabilityDataset(
        selected[:train_count],
        targets[:train_count],
        selected[train_count : train_count + validation_count],
        targets[train_count : train_count + validation_count],
        selected[-test_count:],
        targets[-test_count:],
        "regression",
        reconstruction_shape=reconstruction_shape,
    )


def split_profile(capability: str, *, seed: int = 0) -> dict[str, int | str]:
    dataset = large_capability_dataset(capability, seed=seed)
    return {
        "profile": PROFILE_NAME,
        "train_samples": len(dataset.train_samples),
        "validation_samples": len(dataset.validation_samples),
        "test_samples": len(dataset.test_samples),
    }


def evaluate_large_capability(
    capability: str,
    *,
    seed: int,
) -> LargeBenchmarkEvaluation:
    dataset = large_capability_dataset(capability, seed=seed)
    torch.manual_seed(seed + 90_001)
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
    residuals, closure_status, statuses = _closure_summary(
        (*train_outputs, *validation_outputs, *test_outputs)
    )

    if dataset.task_type == "classification":
        head = _ridge_head(
            train_features,
            dataset.train_targets,
            output_dim=len(dataset.labels),
        )
        train_metrics, _, _, _ = _classification_metrics(
            train_features, dataset.train_targets, head
        )
        validation_metrics, _, _, _ = _classification_metrics(
            validation_features, dataset.validation_targets, head
        )
        test_metrics, _, probabilities, predictions = _classification_metrics(
            test_features, dataset.test_targets, head
        )
        metrics: dict[str, float] = {
            "train_accuracy": train_metrics["accuracy"],
            "validation_accuracy": validation_metrics["accuracy"],
            "accuracy": test_metrics["accuracy"],
            "test_loss": test_metrics["loss"],
            "mean_confidence": test_metrics["mean_confidence"],
            "generalization_gap": (
                train_metrics["accuracy"] - test_metrics["accuracy"]
            ),
        }
        if capability.startswith("bidirectional"):
            decoded = _bidirectional_payload(
                capability,
                probabilities,
                dataset.test_samples,
            )
            roundtrip = (
                decoded["roundtrip_predictions"] == predictions
            ).float().mean()
            metrics["roundtrip_accuracy"] = float(roundtrip)
            metrics["modality_rmse"] = float(decoded["modality_rmse"])
    else:
        head = _ridge_head(
            train_features,
            dataset.train_targets,
            output_dim=dataset.train_targets.shape[-1],
        )
        train_metrics, _ = _regression_metrics(
            train_features, dataset.train_targets, head
        )
        validation_metrics, _ = _regression_metrics(
            validation_features, dataset.validation_targets, head
        )
        test_metrics, _ = _regression_metrics(
            test_features, dataset.test_targets, head
        )
        metrics = {
            "train_rmse": train_metrics["rmse"],
            "validation_rmse": validation_metrics["rmse"],
            "rmse": test_metrics["rmse"],
            "mae": test_metrics["mae"],
            "snr_db": test_metrics["snr_db"],
            "generalization_gap": (
                test_metrics["rmse"] - train_metrics["rmse"]
            ),
        }

    profile = split_profile(capability, seed=seed)
    row = {
        "capability": capability,
        "seed": seed,
        "profile": PROFILE_NAME,
        "metric_producer": "SOInet",
        "closure_status": closure_status,
        "closure_status_count": len(statuses),
        "mean_residual_norm": sum(residuals) / len(residuals),
        **profile,
        **metrics,
    }
    checkpoint = {
        "format_version": 1,
        "capability": capability,
        "seed": seed,
        "profile": PROFILE_NAME,
        "metric_producer": "SOInet",
        "model_state_dict": model.state_dict(),
        "task_head": head,
        "split_profile": profile,
        "metrics": metrics,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return LargeBenchmarkEvaluation(row=row, checkpoint=checkpoint)


def large_multi_seed_benchmark(
    capabilities: tuple[str, ...],
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
) -> tuple[LargeBenchmarkEvaluation, ...]:
    if len(seeds) < 2:
        raise ValueError("large multi-seed benchmark requires at least two seeds")
    return tuple(
        evaluate_large_capability(capability, seed=seed)
        for capability in capabilities
        for seed in seeds
    )
