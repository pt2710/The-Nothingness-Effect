"""Authoritative finite L1 specialization of SOI finitization.

The witness implements relative simple-function approximation together with
its exact absolute SOI scaling.  It remains a finite certificate and does not
replace the appendix proof of density or non-finitization boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .canonical_contracts import (
    FinitizationInput,
    LawCertificate,
    _array,
    _positive,
    _tolerance,
)


@dataclass(frozen=True)
class ScaledFinitizationInput(FinitizationInput):
    """Backward-compatible finitization input with explicit SOI magnitude."""

    magnitude: float = 1.0


def soi_finitization_l1_law(
    value: FinitizationInput | ScaledFinitizationInput,
) -> LawCertificate:
    """Evaluate exact relative/absolute L1 approximation scaling."""

    _tolerance(value.tolerance)
    omega_soi = _positive(float(getattr(value, "magnitude", 1.0)), "Omega_SOI")
    target = _array(value.target, "target", 1)
    approximants = _array(value.approximants, "approximants", 2)
    if approximants.shape[1] != target.size:
        raise ValueError("approximants and target must share a dimension")

    relative_errors = np.sum(np.abs(approximants - target[None, :]), axis=1)
    absolute_errors = omega_soi * relative_errors
    monotonicity_defect = float(
        np.linalg.norm(np.maximum(np.diff(relative_errors), 0.0))
    )
    scaling_residual = float(
        np.linalg.norm(absolute_errors - omega_soi * relative_errors)
    )
    return LawCertificate(
        (
            target,
            approximants,
            relative_errors,
            absolute_errors,
            np.asarray((omega_soi,)),
        ),
        (
            monotonicity_defect,
            float(relative_errors[-1]),
            float(absolute_errors[-1]),
            scaling_residual,
        ),
    )


__all__ = ["ScaledFinitizationInput", "soi_finitization_l1_law"]
