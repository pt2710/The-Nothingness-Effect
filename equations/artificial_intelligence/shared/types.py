"""Shared typed outputs and fail-closed AI statuses."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import torch


class AIClosureStatus(str, Enum):
    SATISFIED = "satisfied"
    NUMERICAL_CANDIDATE = "numerical_candidate"
    OPEN = "open"
    BLOCKED = "blocked"


class AIObstructionError(RuntimeError):
    """Raised when an AI source law leaves its finite typed domain."""


@dataclass
class TNEAIOutput:
    hidden: torch.Tensor
    readout: torch.Tensor
    observation: torch.Tensor
    dfi: torch.Tensor
    elastic_gain: torch.Tensor
    residuals: dict[str, torch.Tensor]
    closure_status: AIClosureStatus
    metadata: dict[str, Any] = field(default_factory=dict)


def require_finite_tensor(value: torch.Tensor, name: str) -> torch.Tensor:
    if not bool(torch.isfinite(value).all()):
        raise AIObstructionError(f"{name} contains NaN or infinity")
    return value
