"""Canonical multimodal SOInet bridge over shared TNE source laws."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import torch
from torch import nn
from torch.nn import functional as functional

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate
from the_nothingness_effect.artificial_intelligence.shared.elastic_dubler import (
    ElasticDublerLayer,
    ElasticDublerState,
)
from the_nothingness_effect.artificial_intelligence.shared.entropy_gates import normalized_dfi
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
    TNEAIOutput,
    require_finite_tensor,
)

from .model import SOInetModel, SOInetOutput


MULTIMODAL_REFERENCE_SHA256 = (
    "EE6A04D89EBE5DA78D4F93950789A8833A904FF29A8F03DECDC97C621199ADB4"
)


@dataclass
class TNEMultimodalOutput(TNEAIOutput):
    modality_names: tuple[str, ...] = ()
    modality_tokens: torch.Tensor | None = None
    raw_observation_states: dict[str, ObservationCollapseState] | None = None
    modality_entropy: torch.Tensor | None = None
    modality_weights: torch.Tensor | None = None
    fused_state: torch.Tensor | None = None
    latent_collapse_gate: torch.Tensor | None = None
    elastic_dubler_state: ElasticDublerState | None = None
    soinet_output: SOInetOutput | None = None
    reconstructed_tokens: dict[str, torch.Tensor] | None = None


class TNEMultimodalSOInet(nn.Module):
    """Observe, encode, compare, fuse, and reconstruct named modalities.

    Every raw modality is mapped to the same finite energy-token domain and
    passed through the same encoder.  Named modalities supply the explicit
    domain map for the Elastic Dubler comparison.  The fused carriers then run
    through the canonical SOInet ensemble, which retains DTQC->QENN and
    QENN+MPL-TC->PGQENN provenance.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        *,
        K_D: float = 1.0,
        qenn_count: int = 1,
        pgqenn_count: int = 1,
        mpl_tc_repository: str | Path | None = None,
        raw_observation_collapse_enabled: bool = True,
        elastic_dubler_enabled: bool = True,
    ) -> None:
        super().__init__()
        if min(input_dim, hidden_dim, output_dim) <= 0:
            raise AIObstructionError("multimodal dimensions must be positive")
        if input_dim < 2:
            raise AIObstructionError("multimodal token dimension must be at least two")
        self.input_dim = int(input_dim)
        self.raw_observer = (
            ObservationCollapseReadout()
            if raw_observation_collapse_enabled
            else None
        )
        self.shared_encoder = nn.Sequential(
            nn.Linear(input_dim, input_dim, bias=False),
            nn.Softplus(),
        )
        self.elastic_dubler = (
            ElasticDublerLayer(K_D) if elastic_dubler_enabled else None
        )
        self.soinet = SOInetModel(
            input_dim,
            hidden_dim,
            output_dim,
            qenn_count=qenn_count,
            pgqenn_count=pgqenn_count,
            K_D=K_D,
            mpl_tc_repository=mpl_tc_repository,
        )
        self.shared_decoder = nn.Sequential(
            nn.Linear(hidden_dim, input_dim),
            nn.Softplus(),
        )

    def _tokenize(
        self,
        modalities: Mapping[str, torch.Tensor],
    ) -> tuple[tuple[str, ...], torch.Tensor, dict[str, ObservationCollapseState]]:
        if len(modalities) < 2:
            raise AIObstructionError("multimodal SOInet requires at least two modalities")
        names = tuple(sorted(str(name) for name in modalities))
        if len(names) != len(modalities) or any(not name for name in names):
            raise AIObstructionError("modality names must be unique non-empty strings")
        batches = {int(modalities[name].shape[0]) for name in names}
        if len(batches) != 1 or next(iter(batches)) < 2:
            raise AIObstructionError(
                "all modalities require the same batch dimension of at least two"
            )

        tokens: list[torch.Tensor] = []
        observations: dict[str, ObservationCollapseState] = {}
        for name in names:
            value = modalities[name]
            require_finite_tensor(value, f"raw modality {name}")
            if value.ndim < 2 or value.numel() == 0:
                raise AIObstructionError(
                    f"raw modality {name} must have a batch and non-empty content axes"
                )
            magnitude = torch.abs(value.reshape(value.shape[0], -1))
            pooled = functional.adaptive_avg_pool1d(
                magnitude.unsqueeze(1), self.input_dim
            ).squeeze(1)
            pooled = pooled + torch.finfo(pooled.dtype).eps * 32
            if self.raw_observer is not None:
                state = self.raw_observer(pooled)
                observations[name] = state
                observed = pooled * state.probabilities * self.input_dim
            else:
                observed = pooled
            token = require_finite_tensor(
                self.shared_encoder(observed), f"shared modality token {name}"
            )
            tokens.append(token)
        return names, torch.stack(tokens, dim=1), observations

    def forward(
        self,
        modalities: Mapping[str, torch.Tensor],
        *,
        tolerance: float = 1e-5,
    ) -> TNEMultimodalOutput:
        names, tokens, raw_observations = self._tokenize(modalities)
        batch, modality_count, feature_count = tokens.shape
        entropy_fields = []
        dfi_fields = []
        for index in range(modality_count):
            dfi = normalized_dfi(tokens[:, index, :], 1.0)
            dfi_fields.append(dfi)
            entropy_fields.append(torch.mean(torch.abs(dfi), dim=-1))
        modality_entropy = torch.stack(entropy_fields, dim=-1)

        dubler_state = (
            self.elastic_dubler(modality_entropy)
            if self.elastic_dubler is not None
            else None
        )
        weights = (
            dubler_state.precision
            if dubler_state is not None
            else torch.full(
                (batch, modality_count),
                1.0 / modality_count,
                dtype=tokens.dtype,
                device=tokens.device,
            )
        )
        fused = require_finite_tensor(
            torch.sum(weights.unsqueeze(-1) * tokens, dim=1),
            "Elastic Dubler multimodal fusion",
        )
        reference = torch.mean(tokens, dim=1)
        gate = (
            torch.mean(dubler_state.elastic_pi / torch.pi, dim=-1, keepdim=True)
            if dubler_state is not None
            else torch.full(
                (batch, 1), 0.5, dtype=tokens.dtype, device=tokens.device
            )
        )
        if not bool(((gate > 0) & (gate <= 1)).all()):
            raise AIObstructionError("multimodal latent collapse gate left (0, 1]")
        collapsed = require_finite_tensor(
            gate * fused + (1.0 - gate) * reference,
            "multimodal latent collapse",
        )
        soinet_output = self.soinet(collapsed, fused, tolerance=tolerance)
        reconstruction = require_finite_tensor(
            self.shared_decoder(soinet_output.hidden),
            "shared multimodal token reconstruction",
        )
        reconstruction_batch = reconstruction.unsqueeze(0).expand(batch, -1)
        reconstructed_tokens = {name: reconstruction_batch for name in names}

        residuals: dict[str, torch.Tensor] = {}
        for name, state in raw_observations.items():
            residuals.update(
                {
                    f"raw_{name}_{residual_name}": residual
                    for residual_name, residual in state.residuals.items()
                }
            )
        if dubler_state is not None:
            residuals.update(dubler_state.residuals)
        residuals.update(
            {
                "modality_weight_normalization": torch.max(
                    torch.abs(weights.sum(dim=-1) - 1.0)
                ),
                "latent_collapse_bounds": torch.max(
                    torch.relu(-gate) + torch.relu(gate - 1.0)
                ),
                "token_reconstruction": torch.sqrt(
                    torch.mean((reconstruction_batch.unsqueeze(1) - tokens) ** 2)
                ),
                "soinet_completeness": torch.stack(
                    tuple(soinet_output.residuals.values())
                ).sum(),
            }
        )
        for name, residual in residuals.items():
            require_finite_tensor(residual, f"multimodal residual {name}")
        status = arbitrate(residuals, tolerance)
        dfi_carrier = torch.stack(dfi_fields, dim=1)
        elastic_carrier = (
            dubler_state.elastic_pi
            if dubler_state is not None
            else torch.ones_like(modality_entropy) * torch.pi
        )
        metadata: dict[str, Any] = {
            **backend_metadata(),
            "architecture": "TNE Multimodal SOInet",
            "modality_names": names,
            "raw_observation_collapse_integration": (
                "canonical_runtime" if self.raw_observer is not None else "source_removal_ablation"
            ),
            "elastic_dubler_integration": (
                "named_modality_domain_bridge" if dubler_state is not None else "source_removal_ablation"
            ),
            "dependency_chain": soinet_output.metadata["dependency_chain"],
            "mpl_tc_commits": soinet_output.metadata["mpl_tc_commits"],
            "external_reference_context_sha256": MULTIMODAL_REFERENCE_SHA256,
            "external_reference_policy": "design context only; no source copied",
            "claim_boundary": "finite computational support; not a formal proof substitute",
        }
        return TNEMultimodalOutput(
            hidden=soinet_output.hidden,
            readout=soinet_output.readout,
            observation=soinet_output.observation,
            dfi=dfi_carrier,
            elastic_gain=elastic_carrier,
            residuals=residuals,
            closure_status=status,
            metadata=metadata,
            modality_names=names,
            modality_tokens=tokens,
            raw_observation_states=raw_observations,
            modality_entropy=modality_entropy,
            modality_weights=weights,
            fused_state=fused,
            latent_collapse_gate=gate,
            elastic_dubler_state=dubler_state,
            soinet_output=soinet_output,
            reconstructed_tokens=reconstructed_tokens,
        )
