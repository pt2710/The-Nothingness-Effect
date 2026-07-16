"""SOInet meta-network CPU training objective."""

from __future__ import annotations

import torch
import torch.nn.functional as functional

from .model import SOInetModel


def training_step(model: SOInetModel, qenn_features: torch.Tensor, pgqenn_features: torch.Tensor, target: torch.Tensor, *, closure_weight: float = 0.1) -> torch.Tensor:
    output = model(qenn_features, pgqenn_features)
    task = functional.cross_entropy(output.readout, target.reshape(1))
    closure = torch.stack(tuple(output.residuals.values())).sum()
    return task + float(closure_weight) * closure
