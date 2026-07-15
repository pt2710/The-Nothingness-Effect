"""Minimal QENN CPU training step with closure residual regularization."""

from __future__ import annotations

import torch
from torch.nn import functional as F

from .model import QENNModel


def training_step(model: QENNModel, features: torch.Tensor, targets: torch.Tensor, *, closure_weight: float = 0.1) -> torch.Tensor:
    output = model(features)
    task_loss = F.cross_entropy(output.readout, targets)
    closure_loss = torch.stack(tuple(output.residuals.values())).sum()
    return task_loss + float(closure_weight) * closure_loss
