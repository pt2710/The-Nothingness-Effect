from __future__ import annotations

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIClosureStatus,
    AIObstructionError,
)
from the_nothingness_effect.artificial_intelligence.soinets.multimodal import (
    TNEMultimodalSOInet,
)


def _modalities() -> dict[str, torch.Tensor]:
    time = torch.linspace(0.0, 1.0, 64)
    return {
        "color": torch.rand(8, 3) + 0.1,
        "sound": (
            torch.sin(2.0 * torch.pi * 5.0 * time)
            .repeat(8, 1)
            .unsqueeze(1)
        ),
        "vision": torch.rand(8, 1, 8, 8),
    }


def test_multimodal_soinet_runs_shared_encoder_dubler_and_dependency_chain():
    torch.manual_seed(0)
    model = TNEMultimodalSOInet(6, 8, 4)
    modalities = {
        name: value.requires_grad_() for name, value in _modalities().items()
    }
    output = model(modalities)

    assert output.modality_names == ("color", "sound", "vision")
    assert output.modality_tokens is not None
    assert output.modality_tokens.shape == (8, 3, 6)
    assert output.elastic_dubler_state is not None
    assert output.soinet_output is not None
    assert output.raw_observation_states is not None
    assert set(output.raw_observation_states) == set(output.modality_names)
    assert torch.allclose(output.modality_weights.sum(dim=-1), torch.ones(8))
    assert output.metadata["dependency_chain"] == (
        "DTQC->QENN",
        "QENN+MPL-TC->PGQENN",
        "QENN+PGQENN->SOInet",
    )
    assert output.metadata["elastic_dubler_integration"] == "named_modality_domain_bridge"
    assert output.closure_status is AIClosureStatus.OPEN

    loss = output.readout.square().mean() + sum(
        value.square().mean() for value in output.reconstructed_tokens.values()
    )
    loss.backward()
    assert all(value.grad is not None for value in modalities.values())
    assert all(
        parameter.grad is not None
        for parameter in model.parameters()
        if parameter.requires_grad
    )


def test_multimodal_soinet_fails_closed_for_non_finite_modality():
    modalities = _modalities()
    modalities["color"][0, 0] = float("nan")
    with pytest.raises(AIObstructionError):
        TNEMultimodalSOInet(6, 8, 4)(modalities)
