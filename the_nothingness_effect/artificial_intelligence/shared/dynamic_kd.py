"""Synchronized, fail-closed control of the dynamic Elastic constant ``K_D``."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn

from .types import AIObstructionError


@dataclass(frozen=True)
class DynamicKDState:
    """A model-wide snapshot of the exact positive Elastic scale."""

    value: float
    buffer_names: tuple[str, ...]


def _validate_kd(value: float) -> float:
    resolved = float(value)
    if not math.isfinite(resolved) or resolved <= 0.0:
        raise AIObstructionError("dynamic K_D must be finite and strictly positive")
    return resolved


def dynamic_kd_state(model: nn.Module, *, tolerance: float = 1e-10) -> DynamicKDState:
    """Return the synchronized K_D value or fail on a split model state."""

    entries = tuple(
        (name, buffer)
        for name, buffer in model.named_buffers()
        if name == "K_D" or name.endswith(".K_D")
    )
    if not entries:
        raise AIObstructionError("model does not expose a dynamic K_D buffer")
    values = tuple(_validate_kd(float(buffer.detach().cpu())) for _, buffer in entries)
    reference = values[0]
    if any(abs(value - reference) > tolerance for value in values[1:]):
        details = ", ".join(
            f"{name}={value:.12g}" for (name, _), value in zip(entries, values, strict=True)
        )
        raise AIObstructionError(f"model contains inconsistent K_D buffers: {details}")
    return DynamicKDState(reference, tuple(name for name, _ in entries))


def set_dynamic_kd(model: nn.Module, value: float) -> DynamicKDState:
    """Set every Elastic-pi/Dubler K_D buffer to one exact positive value.

    This operation changes the source-law parameter only.  It does not clip an
    exponent, mask a singularity, or reinterpret a numerical residual as proof.
    """

    resolved = _validate_kd(value)
    entries = tuple(
        (name, buffer)
        for name, buffer in model.named_buffers()
        if name == "K_D" or name.endswith(".K_D")
    )
    if not entries:
        raise AIObstructionError("model does not expose a dynamic K_D buffer")
    with torch.no_grad():
        for _, buffer in entries:
            buffer.fill_(resolved)
    return dynamic_kd_state(model)
