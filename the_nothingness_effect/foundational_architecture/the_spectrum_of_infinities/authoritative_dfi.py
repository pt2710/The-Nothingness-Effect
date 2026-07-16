"""Authoritative finite Spectrum--DFI regularity witness.

The appendix law is

    V_0 = Omega_SOI / n,
    V_i = V_0 sigma_i,
    S_i = V_0 (sigma_i - 1),

with exact Lp scaling.  The executable witness uses the finite Euclidean
(L2) sector and treats non-finite multipliers, non-positive normalization, and
exponential overflow as fail-closed domain/codomain failures.  It does not
represent finite arrays as a proof of infinite-space integrability.
"""

from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    NonFiniteValueError,
)

from .canonical_contracts import (
    DFIInput,
    LawCertificate,
    _array,
    _positive,
    _tolerance,
)


def spectrum_dfi_regularity_law(value: DFIInput) -> LawCertificate:
    """Evaluate the exact finite L2 specialization of the SOI--DFI law."""

    _tolerance(value.tolerance)
    omega_soi = _positive(value.magnitude, "Omega_SOI")
    multipliers = _array(value.trajectory, "DFI multipliers", 1)
    n = multipliers.size
    baseline = omega_soi / n
    volumes = baseline * multipliers
    fluctuations = volumes - baseline
    centered = multipliers - 1.0

    multiplier_norm = float(np.linalg.norm(centered, ord=2))
    fluctuation_norm = float(np.linalg.norm(fluctuations, ord=2))
    expected_norm = baseline * multiplier_norm

    try:
        exponential_response = np.exp(fluctuations)
    except FloatingPointError as exc:
        raise NonFiniteValueError("SOI--DFI exponential response overflow") from exc
    if not np.isfinite(exponential_response).all():
        raise NonFiniteValueError("SOI--DFI exponential response is non-finite")

    residuals = (
        abs(n * baseline - omega_soi),
        float(np.linalg.norm(volumes - baseline * multipliers)),
        float(np.linalg.norm(fluctuations - baseline * centered)),
        abs(fluctuation_norm - expected_norm),
    )
    return LawCertificate(
        (
            multipliers,
            np.asarray((baseline,)),
            volumes,
            fluctuations,
            np.asarray((multiplier_norm, fluctuation_norm)),
            exponential_response,
        ),
        residuals,
    )


__all__ = ["spectrum_dfi_regularity_law"]
