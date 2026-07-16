"""Exact differentiable Elastic Dubler ratios with explicit bridge metadata."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn

from .elastic_pi_gates import ElasticPiGate
from .types import AIObstructionError, require_finite_tensor


ELASTIC_DUBLER_SOURCE_IDS = (
    "elastic_dubler_duality_closure",
)


@dataclass(frozen=True)
class ElasticDublerState:
    elastic_pi: torch.Tensor
    ratio: torch.Tensor
    log_shift: torch.Tensor
    mismatch: torch.Tensor
    precision: torch.Tensor
    residuals: dict[str, torch.Tensor]
    source_ids: tuple[str, ...] = ELASTIC_DUBLER_SOURCE_IDS


class ElasticDublerLayer(nn.Module):
    """Evaluate pairwise Dubler laws on a declared final-axis domain family.

    The caller owns the bridge that interprets the final axis as QENN weight
    windows or named modalities.  This layer does not reinterpret a ratio as a
    physical frequency, learning rate, or proof of cross-domain equivalence.
    """

    def __init__(self, K_D: float = 1.0) -> None:
        super().__init__()
        if not math.isfinite(K_D) or K_D <= 0:
            raise AIObstructionError("Elastic Dubler K_D must be finite and positive")
        self.elastic_pi = ElasticPiGate(K_D)
        self.register_buffer("K_D", torch.tensor(float(K_D)))

    def forward(self, entropy: torch.Tensor) -> ElasticDublerState:
        require_finite_tensor(entropy, "Elastic Dubler entropy field")
        if entropy.ndim != 2 or entropy.shape[-1] < 2:
            raise AIObstructionError(
                "Elastic Dubler requires [samples, domains] with at least two domains"
            )
        elastic = self.elastic_pi(entropy)
        ratio = elastic.unsqueeze(-1) / elastic.unsqueeze(-2)
        require_finite_tensor(ratio, "Elastic Dubler ratio")
        if bool((ratio <= 0).any()):
            raise AIObstructionError("Elastic Dubler ratio left the positive domain")

        scale = self.K_D.to(dtype=entropy.dtype, device=entropy.device)
        expected_log_shift = -(
            entropy.unsqueeze(-1) - entropy.unsqueeze(-2)
        ) / scale
        expected_ratio = torch.exp(expected_log_shift)
        require_finite_tensor(expected_ratio, "Elastic Dubler exact ratio")
        if bool((expected_ratio == 0).any()):
            raise AIObstructionError("Elastic Dubler exact ratio underflowed")
        log_shift = require_finite_tensor(
            torch.log(ratio), "Elastic Dubler log-shift"
        )

        cocycle = (
            log_shift[:, :, None, :]
            - log_shift[:, :, :, None]
            - log_shift[:, None, :, :]
        )
        identity = torch.eye(
            entropy.shape[-1], dtype=entropy.dtype, device=entropy.device
        ).unsqueeze(0)
        residuals = {
            "elastic_dubler_ratio_identity": torch.linalg.vector_norm(
                ratio - expected_ratio
            ),
            "elastic_dubler_log_shift": torch.linalg.vector_norm(
                log_shift - expected_log_shift
            ),
            "elastic_dubler_endpoint_exchange": torch.linalg.vector_norm(
                log_shift + log_shift.transpose(-1, -2)
            ),
            "elastic_dubler_cocycle": torch.linalg.vector_norm(cocycle),
            "elastic_dubler_diagonal": torch.linalg.vector_norm(
                ratio * identity - identity
            ),
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, f"Elastic Dubler residual {name}")
        mismatch = torch.mean(torch.abs(log_shift), dim=-1)
        precision = require_finite_tensor(
            elastic / torch.sum(elastic, dim=-1, keepdim=True),
            "Elastic Dubler bridge precision",
        )
        precision_ratio = precision.unsqueeze(-1) / precision.unsqueeze(-2)
        residuals["elastic_dubler_precision_ratio"] = torch.linalg.vector_norm(
            precision_ratio - ratio
        )
        residuals["elastic_dubler_precision_normalization"] = torch.max(
            torch.abs(precision.sum(dim=-1) - 1.0)
        )
        return ElasticDublerState(
            elastic, ratio, log_shift, mismatch, precision, residuals
        )
