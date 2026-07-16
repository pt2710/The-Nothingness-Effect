"""Synchronized, fail-closed control of the SOI normalization gain."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn

from .types import AIObstructionError


@dataclass(frozen=True)
class DynamicSOIState:
    """A model-wide snapshot of the positive SOI normalization gain."""

    value: float
    buffer_names: tuple[str, ...]


def _validate_soi(value: float) -> float:
    resolved = float(value)
    if not math.isfinite(resolved) or resolved <= 0.0:
        raise AIObstructionError(
            "dynamic SOI normalization must be finite and strictly positive"
        )
    return resolved


def dynamic_soi_state(
    model: nn.Module, *, tolerance: float = 1e-10
) -> DynamicSOIState:
    """Return the synchronized normalization gain or fail on a split state."""

    entries = tuple(
        (name, buffer)
        for name, buffer in model.named_buffers()
        if name == "soi_scale" or name.endswith(".soi_scale")
    )
    if not entries:
        raise AIObstructionError("model does not expose a dynamic SOI buffer")
    values = tuple(_validate_soi(float(buffer.detach().cpu())) for _, buffer in entries)
    reference = values[0]
    if any(abs(value - reference) > tolerance for value in values[1:]):
        details = ", ".join(
            f"{name}={value:.12g}"
            for (name, _), value in zip(entries, values, strict=True)
        )
        raise AIObstructionError(
            f"model contains inconsistent SOI normalization buffers: {details}"
        )
    return DynamicSOIState(reference, tuple(name for name, _ in entries))


def set_dynamic_soi(model: nn.Module, value: float) -> DynamicSOIState:
    """Set every QENN normalization gain atomically.

    The gain realizes the appendix carrier ``W_tilde = gamma_t**-1 W_t``.
    It does not alter the scale-invariant canonical DFI source law.
    """

    resolved = _validate_soi(value)
    entries = tuple(
        (name, buffer)
        for name, buffer in model.named_buffers()
        if name == "soi_scale" or name.endswith(".soi_scale")
    )
    if not entries:
        raise AIObstructionError("model does not expose a dynamic SOI buffer")
    with torch.no_grad():
        for _, buffer in entries:
            buffer.fill_(resolved)
    return dynamic_soi_state(model)
