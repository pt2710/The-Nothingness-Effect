from __future__ import annotations

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.shared.observation_collapse import (
    ObservationCollapseReadout,
)
from the_nothingness_effect.artificial_intelligence.shared.types import AIObstructionError


def test_observation_collapse_is_normalized_and_idempotent():
    readout = ObservationCollapseReadout(temperature=0.75)
    state = readout(torch.tensor([[2.0, -1.0, 0.5], [-0.5, 3.0, 0.0]]))

    assert torch.allclose(state.probabilities.sum(dim=-1), torch.ones(2))
    assert torch.equal(state.selected_indices, torch.tensor([0, 1]))
    assert torch.equal(state.collapsed_outcome.sum(dim=-1), torch.ones(2))
    assert all(float(residual) <= 1e-6 for residual in state.residuals.values())


@pytest.mark.parametrize(
    "logits",
    [torch.tensor([[float("nan"), 0.0]]), torch.tensor([[float("inf"), 0.0]])],
)
def test_observation_collapse_fails_closed_for_non_finite_logits(logits: torch.Tensor):
    with pytest.raises(AIObstructionError):
        ObservationCollapseReadout()(logits)
