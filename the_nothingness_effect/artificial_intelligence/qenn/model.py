"""Differentiable CPU-testable QENN model."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate, parseval_residual
from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_gates import ElasticPiGate
from the_nothingness_effect.artificial_intelligence.shared.elastic_dubler import (
    ElasticDublerLayer,
    ElasticDublerState,
)
from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_norm import (
    ElasticPiNormState,
    elastic_pi_transition_norm,
)
from the_nothingness_effect.artificial_intelligence.shared.entropy_gates import (
    batch_parity_conditioned_dfi,
    normalized_dfi,
)
from the_nothingness_effect.artificial_intelligence.shared.equivariant_layers import C2EquivariantLinear, SpectralMemory
from the_nothingness_effect.artificial_intelligence.shared.flowpoint_layers import FlowpointLayer, anti_invariant_projector, invariant_projector
from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
    ObservationCollapseState,
)
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import TNEAIOutput, require_finite_tensor
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.neural_operator import (
    DTQCInflationLayer,
    DTQCNeuralState,
)


@dataclass
class QENNOutput(TNEAIOutput):
    invariant_state: torch.Tensor | None = None
    anti_invariant_state: torch.Tensor | None = None
    spectral_reconstruction: torch.Tensor | None = None
    dtqc_state: DTQCNeuralState | None = None
    pdfi: torch.Tensor | None = None
    observation_collapse_state: ObservationCollapseState | None = None
    elastic_dubler_state: ElasticDublerState | None = None
    elastic_pi_norm_state: ElasticPiNormState | None = None


class QENNModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        *,
        K_D: float = 1.0,
        soi_scale: float = 1.0,
        dtqc_enabled: bool = True,
        dtqc_strength: float = 0.25,
        dtqc_support_fraction: float = 0.5,
        observation_collapse_enabled: bool = True,
        observation_temperature: float = 1.0,
        elastic_dubler_enabled: bool = True,
    ):
        super().__init__()
        if min(input_dim, hidden_dim, output_dim) <= 0:
            raise ValueError("QENN dimensions must be positive")
        self.flowpoint = FlowpointLayer()
        self.equivariant = C2EquivariantLinear(input_dim, hidden_dim)
        self.memory = SpectralMemory()
        self.dtqc = (
            DTQCInflationLayer(strength=dtqc_strength, support_fraction=dtqc_support_fraction)
            if dtqc_enabled
            else None
        )
        self.elastic_gate = ElasticPiGate(K_D)
        self.elastic_dubler = ElasticDublerLayer(K_D) if elastic_dubler_enabled else None
        self.readout_layer = nn.Linear(hidden_dim, output_dim)
        self.observation_collapse = (
            ObservationCollapseReadout(temperature=observation_temperature)
            if observation_collapse_enabled
            else None
        )
        self.register_buffer("soi_scale", torch.tensor(float(soi_scale)))

    def forward(self, value: torch.Tensor, *, tolerance: float = 1e-5) -> QENNOutput:
        require_finite_tensor(value, "QENN input")
        if value.ndim != 2 or value.shape[1] != self.equivariant.linear.in_features:
            raise ValueError("QENN input must have shape [batch, input_dim]")
        invariant = invariant_projector(value, self.flowpoint)
        anti = anti_invariant_projector(value, self.flowpoint)
        dfi = normalized_dfi(value, self.soi_scale)
        pdfi = batch_parity_conditioned_dfi(value)
        entropy = torch.abs(dfi) + pdfi
        elastic = self.elastic_gate(entropy)
        dubler_state = self.elastic_dubler(entropy) if self.elastic_dubler is not None else None
        feature_precision = (
            dubler_state.precision * value.shape[-1]
            if dubler_state is not None
            else torch.ones_like(value)
        )
        bridged_anti = require_finite_tensor(
            anti * feature_precision, "QENN Elastic Dubler feature bridge"
        )
        equivariant = torch.tanh(self.equivariant(bridged_anti))
        elastic_norm_state = elastic_pi_transition_norm(value, elastic)
        gain = torch.mean(elastic / torch.pi, dim=-1, keepdim=True)
        gated = require_finite_tensor(equivariant * gain, "QENN gated state")
        dtqc_state = self.dtqc(gated, elastic_gain=gain) if self.dtqc is not None else None
        hidden = require_finite_tensor(
            dtqc_state.reconstruction if dtqc_state is not None else gated,
            "QENN DTQC hidden state",
        )
        reconstruction, spectral_residual = self.memory(hidden)
        logits = self.readout_layer(reconstruction)
        observation_state = (
            self.observation_collapse(logits)
            if self.observation_collapse is not None
            else None
        )
        observation = (
            observation_state.probabilities
            if observation_state is not None
            else torch.full_like(logits, 1.0 / logits.shape[-1])
        )
        residuals = {
            "flowpoint_involution": self.flowpoint.involution_residual(value),
            "c2_equivariance": self.equivariant.equivariance_residual(bridged_anti),
            "projector_reconstruction": torch.linalg.vector_norm(invariant + anti - value),
            "invariant_fixed_sector": torch.linalg.vector_norm(self.flowpoint(invariant) - invariant),
            "anti_invariant_sector": torch.linalg.vector_norm(self.flowpoint(anti) + anti),
            "spectral_reconstruction": spectral_residual,
            "parseval": parseval_residual(hidden),
        }
        if observation_state is not None:
            residuals.update(observation_state.residuals)
        if dubler_state is not None:
            residuals.update(dubler_state.residuals)
        if dtqc_state is not None:
            residuals.update(dtqc_state.residuals)
        residuals["completeness"] = torch.max(torch.stack(tuple(residuals.values())))
        status = arbitrate(residuals, tolerance)
        metadata = {
            **backend_metadata(),
            "architecture": "QENN",
            "soi_scale": float(self.soi_scale),
            "dtqc_integration": "canonical_runtime" if dtqc_state is not None else "source_removal_ablation",
            "observation_collapse_integration": (
                "canonical_runtime" if observation_state is not None else "source_removal_ablation"
            ),
            "elastic_dubler_integration": (
                "feature_weight_window_bridge" if dubler_state is not None else "source_removal_ablation"
            ),
            "elastic_pi_norm_integration": "weighted_feature_transition_diagnostic",
            "source_dependencies": (
                "Flowpoint involution and invariant/anti-invariant projectors",
                "normalized DFI and parity-conditioned pDFI",
                "exact unclipped Elastic-pi",
                "Elastic-pi weighted transition norm",
                "exact Elastic Dubler ratio and log-shift",
                "discrete-time quasicrystal inflation and spectral support",
                "observation and collapse",
                "spectral memory, Parseval, and completeness residual",
            ),
        }
        if dtqc_state is not None:
            metadata.update(
                {
                    "dtqc_complex_ids": dtqc_state.complex_ids,
                    "dtqc_closure_status": dtqc_state.closure_status,
                    "dtqc_input_leakage": float(dtqc_state.input_leakage.detach().cpu()),
                }
            )
        if observation_state is not None:
            metadata["observation_collapse_source_ids"] = observation_state.source_ids
        if dubler_state is not None:
            metadata["elastic_dubler_source_ids"] = dubler_state.source_ids
        metadata["elastic_pi_norm_source_ids"] = elastic_norm_state.source_ids
        return QENNOutput(
            hidden=hidden,
            readout=logits,
            observation=observation,
            dfi=dfi,
            elastic_gain=elastic,
            residuals=residuals,
            closure_status=status,
            metadata=metadata,
            invariant_state=invariant,
            anti_invariant_state=anti,
            spectral_reconstruction=reconstruction,
            dtqc_state=dtqc_state,
            pdfi=pdfi,
            observation_collapse_state=observation_state,
            elastic_dubler_state=dubler_state,
            elastic_pi_norm_state=elastic_norm_state,
        )
