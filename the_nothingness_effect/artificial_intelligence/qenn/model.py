"""Differentiable CPU-testable QENN model."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.shared.closure_losses import arbitrate, parseval_residual
from the_nothingness_effect.artificial_intelligence.shared.elastic_pi_gates import ElasticPiGate
from the_nothingness_effect.artificial_intelligence.shared.entropy_gates import normalized_dfi
from the_nothingness_effect.artificial_intelligence.shared.equivariant_layers import C2EquivariantLinear, SpectralMemory
from the_nothingness_effect.artificial_intelligence.shared.flowpoint_layers import FlowpointLayer, anti_invariant_projector, invariant_projector
from the_nothingness_effect.artificial_intelligence.shared.provenance import backend_metadata
from the_nothingness_effect.artificial_intelligence.shared.types import TNEAIOutput, require_finite_tensor


@dataclass
class QENNOutput(TNEAIOutput):
    invariant_state: torch.Tensor | None = None
    anti_invariant_state: torch.Tensor | None = None
    spectral_reconstruction: torch.Tensor | None = None


class QENNModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, *, K_D: float = 1.0, soi_scale: float = 1.0):
        super().__init__()
        if min(input_dim, hidden_dim, output_dim) <= 0:
            raise ValueError("QENN dimensions must be positive")
        self.flowpoint = FlowpointLayer()
        self.equivariant = C2EquivariantLinear(input_dim, hidden_dim)
        self.memory = SpectralMemory()
        self.elastic_gate = ElasticPiGate(K_D)
        self.readout_layer = nn.Linear(hidden_dim, output_dim)
        self.register_buffer("soi_scale", torch.tensor(float(soi_scale)))

    def forward(self, value: torch.Tensor, *, tolerance: float = 1e-5) -> QENNOutput:
        require_finite_tensor(value, "QENN input")
        if value.ndim != 2 or value.shape[1] != self.equivariant.linear.in_features:
            raise ValueError("QENN input must have shape [batch, input_dim]")
        invariant = invariant_projector(value, self.flowpoint)
        anti = anti_invariant_projector(value, self.flowpoint)
        equivariant = torch.tanh(self.equivariant(anti))
        dfi = normalized_dfi(value, self.soi_scale)
        elastic = self.elastic_gate(dfi)
        gain = torch.mean(elastic / torch.pi, dim=-1, keepdim=True)
        hidden = require_finite_tensor(equivariant * gain, "QENN hidden state")
        reconstruction, spectral_residual = self.memory(hidden)
        logits = self.readout_layer(reconstruction)
        observation = torch.softmax(logits, dim=-1)
        residuals = {
            "flowpoint_involution": self.flowpoint.involution_residual(value),
            "c2_equivariance": self.equivariant.equivariance_residual(anti),
            "spectral_reconstruction": spectral_residual,
            "parseval": parseval_residual(hidden),
        }
        status = arbitrate(residuals, tolerance)
        return QENNOutput(
            hidden,
            logits,
            observation,
            dfi,
            elastic,
            residuals,
            status,
            {**backend_metadata(), "architecture": "QENN", "soi_scale": float(self.soi_scale)},
            invariant,
            anti,
            reconstruction,
        )
