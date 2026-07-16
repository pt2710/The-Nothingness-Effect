"""Executable obligations from the recertified Completeness appendix.

These laws isolate the six source corrections that cannot be represented by the
legacy generic array-combination contract. They are finite typed witnesses;
they do not replace the appendix proofs or promote numerical candidates to
formal attainment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)

APPENDIX = "appendix_the_completeness_theorem.tex"
APPENDIX_SHA256 = "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3"


@dataclass(frozen=True)
class NoetherTypeSeparation:
    operator_value: np.ndarray
    residual_value: np.ndarray
    types_separated: bool


def separate_noether_operator_and_residual(
    operator_value: np.ndarray,
    residual_value: np.ndarray,
) -> NoetherTypeSeparation:
    """Keep the Noether B-operator and its defect in distinct codomains."""
    operator = np.asarray(operator_value, dtype=float)
    residual = np.asarray(residual_value, dtype=float)
    if operator.ndim == 0 or residual.ndim == 0:
        raise DomainViolationError("Noether operator and residual require typed arrays")
    ensure_finite((operator, residual), name="Noether operator/residual")
    return NoetherTypeSeparation(operator, residual, operator.shape != residual.shape)


@dataclass(frozen=True)
class TypedAdmissibilityDecoding:
    output: np.ndarray
    decoded_orientation: int | None
    null_gate_detected: bool
    reconstructive_domain: bool


def decode_typed_admissibility(
    *,
    gate: float,
    orientation_bit: int,
    observed_phase_bit: int,
    infinity_state: np.ndarray,
    involution: Callable[[np.ndarray], np.ndarray],
    free_orbit: bool,
    tolerance: float = 1e-12,
) -> TypedAdmissibilityDecoding:
    """Decode Complex 07 only on the open-gate free-orbit domain."""
    if orientation_bit not in (0, 1) or observed_phase_bit not in (0, 1):
        raise DomainViolationError("orientation and observed phase lie in C2")
    state = np.asarray(infinity_state, dtype=float)
    ensure_finite((gate, state), name="typed admissibility input")
    null_gate = abs(float(gate)) <= tolerance
    exponent = orientation_bit ^ observed_phase_bit
    transformed = state if exponent == 0 else np.asarray(involution(state), dtype=float)
    output = float(gate) * transformed
    ensure_finite(output, name="typed admissibility output")
    reconstructive = (not null_gate) and free_orbit
    decoded = exponent ^ observed_phase_bit if reconstructive else None
    return TypedAdmissibilityDecoding(output, decoded, null_gate, reconstructive)


@dataclass(frozen=True)
class SplittingAttainment:
    splitting_residual: float
    infimum_attained: bool
    exact_splitting: bool


def certify_splitting_attainment(
    splitting_residual: float,
    *,
    infimum_attained: bool,
    tolerance: float = 1e-12,
) -> SplittingAttainment:
    """A zero infimum yields an exact splitting only with an attainment witness."""
    ensure_finite(splitting_residual, name="splitting residual")
    if splitting_residual < 0:
        raise DomainViolationError("splitting residual is nonnegative")
    exact = splitting_residual <= tolerance and infimum_attained
    return SplittingAttainment(float(splitting_residual), infimum_attained, exact)


@dataclass(frozen=True)
class NoetherTransgression:
    local_codomain_value: np.ndarray
    global_codomain_value: np.ndarray
    boundary_flux: float
    intertwining_residual: np.ndarray
    commutation_domain_satisfied: bool


def noether_transgression_common_codomain(
    local_value: np.ndarray,
    global_value: np.ndarray,
    *,
    boundary_flux: float,
    tolerance: float = 1e-12,
) -> NoetherTransgression:
    """Compare local and global Noether images only in a common codomain."""
    local = np.asarray(local_value, dtype=float)
    global_ = np.asarray(global_value, dtype=float)
    if local.shape != global_.shape:
        raise DomainViolationError("Noether transgression requires a common codomain")
    ensure_finite((local, global_, boundary_flux), name="Noether transgression")
    zero_flux = abs(float(boundary_flux)) <= tolerance
    residual = global_ - local
    return NoetherTransgression(local, global_, float(boundary_flux), residual, zero_flux)


@dataclass(frozen=True)
class SheafDescentCertificate:
    pairwise_residuals: tuple[float, float, float]
    cocycle_residual: float
    fixed_descent_data: bool
    overlap_isomorphisms: bool
    gluable: bool


def certify_sheaf_descent(
    pairwise_residuals: tuple[float, float, float],
    cocycle_residual: float,
    *,
    fixed_descent_data: bool,
    overlap_isomorphisms: bool,
    tolerance: float = 1e-12,
) -> SheafDescentCertificate:
    """Require fixed overlap isomorphisms and the pairwise/cocycle laws."""
    if len(pairwise_residuals) != 3:
        raise DomainViolationError("three pairwise overlap residuals are required")
    ensure_finite((*pairwise_residuals, cocycle_residual), name="sheaf descent")
    nonnegative = all(value >= 0 for value in (*pairwise_residuals, cocycle_residual))
    if not nonnegative:
        raise DomainViolationError("descent residuals are nonnegative")
    gluable = (
        fixed_descent_data
        and overlap_isomorphisms
        and max(*pairwise_residuals, cocycle_residual) <= tolerance
    )
    return SheafDescentCertificate(
        tuple(float(value) for value in pairwise_residuals),
        float(cocycle_residual),
        fixed_descent_data,
        overlap_isomorphisms,
        gluable,
    )


@dataclass(frozen=True)
class TerminalObservableFactorization:
    observable_values: np.ndarray
    terminal_value: float
    factorized_values: np.ndarray
    factorization_residual: float
    factors_through_unique_terminal_map: bool


def factor_terminal_observable(
    observable_values: np.ndarray,
    *,
    terminal_value: float,
    tolerance: float = 1e-12,
) -> TerminalObservableFactorization:
    """Test f = const_{f(*)} o ! on a realized terminal carrier."""
    values = np.asarray(observable_values, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise DomainViolationError("terminal observable requires a nonempty finite carrier")
    ensure_finite((values, terminal_value), name="terminal observable")
    factorized = np.full_like(values, float(terminal_value))
    residual = float(np.linalg.norm(values - factorized))
    return TerminalObservableFactorization(
        values,
        float(terminal_value),
        factorized,
        residual,
        residual <= tolerance,
    )
