"""Typed runtime primitives for the six observable TNE AI capabilities.

The capability layer composes the canonical Flowpoint, normalized DFI,
Elastic-pi, and observation/collapse primitives. Outputs remain numerical
candidates: a successful finite run is evidence of a bounded computation, not
a proof of an appendix theorem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Sequence

import torch
from torch import nn

from .closure_losses import arbitrate
from .elastic_pi_gates import ElasticPiGate
from .entropy_gates import normalized_dfi
from .flowpoint_layers import FlowpointLayer, anti_invariant_projector
from .provenance import backend_metadata
from .types import AIClosureStatus, AIObstructionError, require_finite_tensor


@dataclass(frozen=True)
class ClassificationOutput:
    """Typed class observation with source-law diagnostics."""

    class_indices: torch.Tensor
    labels: tuple[str, ...]
    scores: torch.Tensor
    observation: torch.Tensor
    dfi: torch.Tensor
    elastic_gain: torch.Tensor
    residuals: dict[str, torch.Tensor]
    closure_status: AIClosureStatus
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def predicted_labels(self) -> tuple[str, ...]:
        return tuple(self.labels[int(index)] for index in self.class_indices.detach().cpu())

    @property
    def confidence(self) -> torch.Tensor:
        return self.observation.max(dim=-1).values


@dataclass(frozen=True)
class BidirectionalOutput:
    """Forward classification and reverse prototype reconstruction evidence."""

    forward: ClassificationOutput
    reconstructed_modality: torch.Tensor
    roundtrip: ClassificationOutput
    label_closure_residual: torch.Tensor
    modality_reconstruction_residual: torch.Tensor
    closure_status: AIClosureStatus
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CloneOutput:
    """Reversible spectral clone with explicit reconstruction residuals."""

    clone: torch.Tensor
    latent: torch.Tensor
    dual_latent: torch.Tensor
    residuals: dict[str, torch.Tensor]
    closure_status: AIClosureStatus
    metadata: dict[str, Any] = field(default_factory=dict)


class TNEPrototypeClassifier(nn.Module):
    """Deterministic prototype observer composed from canonical TNE primitives."""

    def __init__(
        self,
        prototypes: torch.Tensor,
        labels: Sequence[str],
        *,
        K_D: float = 1.0,
        temperature: float = 0.08,
    ) -> None:
        super().__init__()
        prototypes = torch.as_tensor(prototypes, dtype=torch.float32)
        if prototypes.ndim != 2 or prototypes.shape[1] < 2:
            raise AIObstructionError("prototype classifier requires [classes, features] with at least two features")
        require_finite_tensor(prototypes, "prototype carrier")
        if len(labels) != prototypes.shape[0] or len(set(labels)) != len(labels):
            raise AIObstructionError("prototype labels must be unique and match the prototype count")
        if not math.isfinite(temperature) or temperature <= 0:
            raise AIObstructionError("classification temperature must be finite and positive")
        if prototypes.shape[0] > 1 and bool((torch.pdist(prototypes) == 0).any()):
            raise AIObstructionError("classification prototypes must be pairwise distinct")
        self.register_buffer("prototypes", prototypes)
        self.labels = tuple(str(label) for label in labels)
        self.flowpoint = FlowpointLayer()
        self.elastic_gate = ElasticPiGate(K_D)
        self.temperature = float(temperature)

    def forward(self, features: torch.Tensor, *, tolerance: float = 1e-6) -> ClassificationOutput:
        features = torch.as_tensor(features, dtype=self.prototypes.dtype, device=self.prototypes.device)
        require_finite_tensor(features, "classification features")
        if features.ndim != 2 or features.shape[1] != self.prototypes.shape[1]:
            raise AIObstructionError(
                f"classification features must have shape [samples, {self.prototypes.shape[1]}]"
            )
        anti = anti_invariant_projector(features, self.flowpoint)
        # A strictly positive analysis carrier prevents a zero-remainder DFI
        # obstruction without mutating the modality used for classification.
        analysis_carrier = torch.abs(anti) + torch.finfo(anti.dtype).eps * 32
        dfi = normalized_dfi(analysis_carrier, 1.0)
        elastic = self.elastic_gate(torch.abs(dfi))
        gain = torch.mean(elastic / torch.pi, dim=-1, keepdim=True)
        distances = torch.cdist(anti, self.prototypes)
        scores = require_finite_tensor(-(distances * gain) / self.temperature, "classification scores")
        observation = require_finite_tensor(torch.softmax(scores, dim=-1), "classification observation")
        indices = torch.argmax(observation, dim=-1)
        residuals = {
            "flowpoint_involution": self.flowpoint.involution_residual(features),
            "observation_normalization": torch.max(torch.abs(observation.sum(dim=-1) - 1.0)),
        }
        status = arbitrate(residuals, tolerance)
        return ClassificationOutput(
            indices,
            self.labels,
            scores,
            observation,
            dfi,
            elastic,
            residuals,
            status,
            {
                **backend_metadata(),
                "operator": "TNEPrototypeClassifier",
                "flowpoint": "F(x)=-x",
                "readout": "prototype observation/collapse",
                "temperature": self.temperature,
            },
        )

    def decode(self, class_indices: torch.Tensor) -> torch.Tensor:
        indices = torch.as_tensor(class_indices, dtype=torch.long, device=self.prototypes.device)
        if indices.ndim != 1 or bool((indices < 0).any()) or bool((indices >= len(self.labels)).any()):
            raise AIObstructionError("class indices must be a one-dimensional in-range integer carrier")
        return self.prototypes[indices]


def bidirectional_result(
    classifier: TNEPrototypeClassifier,
    features: torch.Tensor,
    *,
    tolerance: float = 1e-6,
) -> BidirectionalOutput:
    """Classify, decode the observed label, and classify the reconstruction."""

    forward = classifier(features, tolerance=tolerance)
    reconstruction = classifier.decode(forward.class_indices)
    roundtrip = classifier(reconstruction, tolerance=tolerance)
    label_residual = torch.count_nonzero(roundtrip.class_indices != forward.class_indices).to(features.dtype)
    modality_residual = torch.sqrt(torch.mean((features - reconstruction) ** 2))
    require_finite_tensor(modality_residual, "bidirectional modality residual")
    status = (
        AIClosureStatus.NUMERICAL_CANDIDATE
        if float(label_residual.detach()) <= tolerance
        else AIClosureStatus.OPEN
    )
    return BidirectionalOutput(
        forward,
        reconstruction,
        roundtrip,
        label_residual,
        modality_residual,
        status,
        {
            **backend_metadata(),
            "closure": "modality -> label -> prototype -> label",
            "modality_reconstruction_is_approximate": True,
        },
    )


def spectral_clone(value: torch.Tensor, *, dimensions: tuple[int, ...], tolerance: float = 1e-6) -> CloneOutput:
    """Clone a finite carrier through an exact FFT/Flowpoint round trip."""

    value = torch.as_tensor(value, dtype=torch.float32)
    require_finite_tensor(value, "clone input")
    if value.numel() == 0 or not dimensions:
        raise AIObstructionError("spectral cloning requires a non-empty carrier and transform dimensions")
    normalized_dimensions = tuple(dimension % value.ndim for dimension in dimensions)
    if len(set(normalized_dimensions)) != len(normalized_dimensions):
        raise AIObstructionError("spectral cloning dimensions must be unique")
    latent = torch.fft.fftn(value, dim=normalized_dimensions, norm="ortho")
    require_finite_tensor(latent, "clone latent")
    dual_latent = -latent
    restored_latent = -dual_latent
    decoded = torch.fft.ifftn(restored_latent, dim=normalized_dimensions, norm="ortho")
    clone = require_finite_tensor(decoded.real, "clone reconstruction")
    source_energy = torch.sum(value.square())
    spectral_energy = torch.sum(torch.abs(latent) ** 2)
    residuals = {
        "flowpoint_involution": torch.linalg.vector_norm(restored_latent - latent),
        "spectral_reconstruction": torch.sqrt(torch.mean((clone - value) ** 2)),
        "imaginary_leakage": torch.sqrt(torch.mean(decoded.imag.square())),
        "parseval": torch.abs(source_energy - spectral_energy) / torch.clamp(source_energy, min=1.0),
    }
    status = arbitrate(residuals, tolerance)
    return CloneOutput(
        clone,
        latent,
        dual_latent,
        residuals,
        status,
        {
            **backend_metadata(),
            "operator": "FFT -> Flowpoint dual -> inverse Flowpoint -> inverse FFT",
            "lossless_finite_roundtrip": status == AIClosureStatus.NUMERICAL_CANDIDATE,
        },
    )
