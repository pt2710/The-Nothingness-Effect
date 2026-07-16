"""Batch-trainable multimodal model over the canonical SOInet backbone."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import (
    TNEAIOutput,
    require_finite_tensor,
)
from the_nothingness_effect.artificial_intelligence.soinets.multimodal import (
    TNEMultimodalOutput,
    TNEMultimodalSOInet,
)

from .axes import ModalityAxisNetwork, ModalityAxisState
from .growth import AdaptiveModalityClusterNetwork, ClusterGrowthState
from .rbm import GaussianBernoulliEnergyLayer, RBMEnergyState


@dataclass
class TNETrainableMultimodalOutput(TNEAIOutput):
    """Per-sample task output plus the complete TNE multimodal backbone state."""

    backbone_output: TNEMultimodalOutput | None = None
    sample_observation_state: ObservationCollapseState | None = None
    fused_hidden: torch.Tensor | None = None
    reconstructed_fused_tokens: torch.Tensor | None = None
    reconstructed_modality_tokens: dict[str, torch.Tensor] | None = None
    axis_state: ModalityAxisState | None = None
    local_rbm_state: RBMEnergyState | None = None
    global_rbm_state: RBMEnergyState | None = None
    cluster_state: ClusterGrowthState | None = None
    energy_precision: torch.Tensor | None = None
    regulated_modality_weights: torch.Tensor | None = None


class TNETrainableMultimodalModel(nn.Module):
    """Trainable color/sound/vision model with a canonical SOInet backbone.

    The backbone supplies raw observation/collapse, normalized DFI, exact
    Elastic-pi and Elastic Dubler fusion, QENN/DTQC, PGQENN/MPL-TC and SOInet
    meta-closure.  This class adds a per-sample task head and shared token
    decoder so training, validation and evaluation operate on batches rather
    than on one batch-aggregate meta-readout.
    """

    def __init__(
        self,
        input_dim: int = 6,
        hidden_dim: int = 12,
        output_dim: int = 4,
        *,
        K_D: float = 1.0,
        qenn_count: int = 1,
        pgqenn_count: int = 1,
        mpl_tc_repository: str | Path | None = None,
        raw_observation_collapse_enabled: bool = True,
        elastic_dubler_enabled: bool = True,
        modality_count: int = 3,
        axis_dim: int | None = None,
        local_rbm_hidden: int | None = None,
        max_clusters: int = 24,
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.hidden_dim = int(hidden_dim)
        self.output_dim = int(output_dim)
        self.modality_count = int(modality_count)
        if self.modality_count < 2:
            raise ValueError("multimodal model requires at least two modalities")
        resolved_axis_dim = int(axis_dim or hidden_dim)
        if resolved_axis_dim < 4:
            raise ValueError("multimodal axis_dim must be at least four")
        resolved_rbm_hidden = int(local_rbm_hidden or max(2, resolved_axis_dim // 2))
        self.backbone = TNEMultimodalSOInet(
            input_dim,
            hidden_dim,
            output_dim,
            K_D=K_D,
            qenn_count=qenn_count,
            pgqenn_count=pgqenn_count,
            mpl_tc_repository=mpl_tc_repository,
            raw_observation_collapse_enabled=raw_observation_collapse_enabled,
            elastic_dubler_enabled=elastic_dubler_enabled,
        )
        self.fused_projection = nn.Linear(input_dim, hidden_dim)
        self.meta_projection = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.axis_network = ModalityAxisNetwork(input_dim, resolved_axis_dim)
        self.local_energy = GaussianBernoulliEnergyLayer(
            resolved_axis_dim, resolved_rbm_hidden
        )
        self.global_energy = GaussianBernoulliEnergyLayer(
            self.modality_count * resolved_rbm_hidden, resolved_axis_dim
        )
        self.cluster_growth = AdaptiveModalityClusterNetwork(
            resolved_axis_dim, max_clusters=max_clusters
        )
        self.axis_projection = nn.Linear(resolved_axis_dim, hidden_dim, bias=False)
        self.energy_projection = nn.Linear(resolved_axis_dim, hidden_dim, bias=False)
        self.cluster_projection = nn.Linear(resolved_axis_dim, hidden_dim, bias=False)
        self.task_head = nn.Linear(hidden_dim, output_dim)
        self.shared_token_decoder = nn.Linear(hidden_dim, input_dim)
        self.sample_observation = ObservationCollapseReadout()
        self.axis_network_enabled = True
        self.energy_regulation_enabled = True
        self.cluster_context_enabled = True

    def forward(
        self,
        modalities: Mapping[str, torch.Tensor],
        *,
        tolerance: float = 1e-5,
    ) -> TNETrainableMultimodalOutput:
        backbone = self.backbone(modalities, tolerance=tolerance)
        if backbone.fused_state is None or backbone.soinet_output is None:
            raise RuntimeError("multimodal backbone did not return its typed fusion state")
        if backbone.modality_tokens is None or backbone.modality_weights is None:
            raise RuntimeError("multimodal backbone did not return modality carriers")
        if len(backbone.modality_names) != self.modality_count:
            raise ValueError(
                f"model expects {self.modality_count} modalities, got "
                f"{len(backbone.modality_names)}"
            )
        axis_state = self.axis_network(
            backbone.modality_tokens,
            backbone.modality_names,
            backbone.modality_weights,
        )
        batch, modality_count, axis_dim = axis_state.mapped_axes.shape
        local_visible = axis_state.mapped_axes.reshape(batch * modality_count, axis_dim)
        local_rbm = self.local_energy(local_visible, steps=1, stochastic=False)
        local_hidden = local_rbm.hidden_probability.reshape(batch, modality_count, -1)
        local_energy = local_rbm.free_energy.reshape(batch, modality_count)
        energy_precision = require_finite_tensor(
            torch.softmax(-local_energy, dim=-1), "RBM modality precision"
        )
        if self.energy_regulation_enabled:
            regulated_weights = backbone.modality_weights * energy_precision
            regulated_weights = regulated_weights / regulated_weights.sum(
                dim=-1, keepdim=True
            ).clamp_min(1e-8)
        else:
            regulated_weights = backbone.modality_weights
        global_visible = local_hidden.reshape(batch, -1)
        global_rbm = self.global_energy(global_visible, steps=1, stochastic=False)
        cluster_state = self.cluster_growth(
            axis_state.mapped_axes,
            backbone.modality_names,
            update=self.training,
        )
        regulated_axis = require_finite_tensor(
            torch.sum(regulated_weights.unsqueeze(-1) * axis_state.mapped_axes, dim=1),
            "energy-regulated modality-axis fusion",
        )
        cluster_context = require_finite_tensor(
            torch.sum(regulated_weights.unsqueeze(-1) * cluster_state.context, dim=1),
            "cluster-growth context",
        )
        meta_context = self.meta_projection(backbone.soinet_output.hidden).unsqueeze(0)
        axis_contribution = (
            self.axis_projection(regulated_axis)
            if self.axis_network_enabled
            else torch.zeros_like(meta_context.expand(batch, -1))
        )
        energy_contribution = (
            self.energy_projection(global_rbm.hidden_probability)
            if self.energy_regulation_enabled
            else torch.zeros_like(axis_contribution)
        )
        cluster_contribution = (
            self.cluster_projection(cluster_context)
            if self.cluster_context_enabled
            else torch.zeros_like(axis_contribution)
        )
        hidden = require_finite_tensor(
            torch.tanh(
                self.fused_projection(backbone.fused_state)
                + meta_context
                + axis_contribution
                + energy_contribution
                + cluster_contribution
            ),
            "trainable multimodal hidden state",
        )
        logits = require_finite_tensor(self.task_head(hidden), "multimodal task logits")
        observation_state = self.sample_observation(logits)
        reconstruction = require_finite_tensor(
            torch.nn.functional.softplus(self.shared_token_decoder(hidden)),
            "multimodal shared token reconstruction",
        )
        reconstructed = {
            name: reconstruction for name in backbone.modality_names
        }
        target_token = torch.mean(backbone.modality_tokens, dim=1)
        residuals = {
            **{
                f"backbone::{name}": residual
                for name, residual in backbone.residuals.items()
            },
            **{
                f"sample::{name}": residual
                for name, residual in observation_state.residuals.items()
            },
            "fused_token_reconstruction": torch.sqrt(
                torch.mean((reconstruction - target_token) ** 2)
            ),
            **{
                f"axis::{name}": residual
                for name, residual in axis_state.residuals.items()
            },
            "rbm::local_reconstruction": local_rbm.reconstruction_residual,
            "rbm::global_reconstruction": global_rbm.reconstruction_residual,
            "rbm::precision_normalization": torch.max(
                torch.abs(energy_precision.sum(dim=-1) - 1.0)
            ),
            "rbm::regulated_weight_normalization": torch.max(
                torch.abs(regulated_weights.sum(dim=-1) - 1.0)
            ),
            **{
                f"growth::{name}": residual
                for name, residual in cluster_state.residuals.items()
            },
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, f"trainable multimodal residual {name}")
        return TNETrainableMultimodalOutput(
            hidden=hidden,
            readout=logits,
            observation=observation_state.probabilities,
            dfi=backbone.dfi,
            elastic_gain=backbone.elastic_gain,
            residuals=residuals,
            closure_status=arbitrate(residuals, tolerance),
            metadata={
                **backend_metadata(),
                "architecture": "TNE Trainable Multimodal SOInet",
                "backbone": "TNEMultimodalSOInet",
                "dependency_chain": backbone.metadata["dependency_chain"],
                "batch_task_readout": "typed_per_sample",
                "modality_axes": "learned_shared_private_cycle_checked",
                "energy_realization": "local_and_global_gaussian_bernoulli_rbm",
                "energy_source_status": "external_numerical_realization_not_tne_source_law",
                "cluster_growth": "bounded_deterministic_modality_prototypes",
                "dynamic_K_D": float(
                    self.backbone.elastic_dubler.K_D.detach().cpu()
                ) if self.backbone.elastic_dubler is not None else None,
                "dynamic_K_D_semantics": (
                    "exact positive source-law parameter; no exponent clipping"
                ),
                "active_clusters": cluster_state.active_clusters,
                "external_reference_context_sha256": (
                    "EE6A04D89EBE5DA78D4F93950789A8833A904FF29A8F03DECDC97C621199ADB4"
                ),
                "claim_boundary": (
                    "finite trained computational model; not a formal proof substitute"
                ),
            },
            backbone_output=backbone,
            sample_observation_state=observation_state,
            fused_hidden=hidden,
            reconstructed_fused_tokens=reconstruction,
            reconstructed_modality_tokens=reconstructed,
            axis_state=axis_state,
            local_rbm_state=local_rbm,
            global_rbm_state=global_rbm,
            cluster_state=cluster_state,
            energy_precision=energy_precision,
            regulated_modality_weights=regulated_weights,
        )
