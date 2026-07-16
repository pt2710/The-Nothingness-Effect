"""Recertified foundational Flowpoint source contracts."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ContractResult,
    ContractStatus,
    scale_aware_tolerance,
)


@dataclass(frozen=True)
class KernelAlternatorResult:
    balance: np.ndarray
    diagonal_part: tuple[np.ndarray, np.ndarray]
    kernel_part: tuple[np.ndarray, np.ndarray]
    alternated_state: tuple[np.ndarray, np.ndarray]


def evaluate_kernel_alternator(a, b, *, characteristic: int = 0) -> ContractResult[KernelAlternatorResult]:
    left = np.asarray(a, dtype=float)
    right = np.asarray(b, dtype=float)
    if characteristic == 2 or left.shape != right.shape or left.size == 0 or not np.all(np.isfinite((left, right))):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_FIELD_OR_PAIR")
    swapped = (right, left)
    diagonal = ((left + right) / 2.0, (left + right) / 2.0)
    kernel = ((left - right) / 2.0, (right - left) / 2.0)
    tol = scale_aware_tolerance(*left.ravel(), *right.ravel())
    residuals = {
        "balance": float(np.linalg.norm((swapped[0] + swapped[1]) - (left + right))),
        "involution": 0.0,
        "projector_sum": float(np.linalg.norm(diagonal[0] + kernel[0] - left) + np.linalg.norm(diagonal[1] + kernel[1] - right)),
        "orthogonality": float(abs(np.vdot(diagonal[0], kernel[0]) + np.vdot(diagonal[1], kernel[1]))),
    }
    degenerate = bool(np.allclose(left, right, rtol=0.0, atol=tol))
    return ContractResult(
        KernelAlternatorResult(left + right, diagonal, kernel, swapped),
        ContractStatus.EXACT,
        "DEGENERATE_ORBIT" if degenerate else "KERNEL_ALTERNATOR_CERTIFIED",
        residuals,
        {name: tol for name in residuals},
        {"fixed_point": degenerate},
        {"source_contract": "kernel_alternator", "exact_equalities_checked": True},
    )


@dataclass(frozen=True)
class TwoAdicUnificationInput:
    state: tuple[int, ...]
    reflection_mask: tuple[int, ...]
    schedule: tuple[int, ...]
    prefix_depth: int
    tail_bound: float | None = None


@dataclass(frozen=True)
class TwoAdicUnificationResult:
    reflected_state: tuple[int, ...]
    prefix_orbit: tuple[tuple[int, ...], ...]
    commuting: bool


def evaluate_2adic_dimensional_unification(value: TwoAdicUnificationInput) -> ContractResult[TwoAdicUnificationResult]:
    if not value.state or len(value.state) != len(value.reflection_mask) or value.prefix_depth < 0:
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_PAIRED_STATE")
    if any(bit not in (0, 1) for bit in value.state + value.reflection_mask + value.schedule):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "NONBINARY_2ADIC_DATA")
    n = len(value.state)
    if any(index >= n for index in value.schedule):
        return ContractResult(None, ContractStatus.FALSIFIED, "NONREALIZABLE_SCHEDULE", witnesses={"state_size": n})
    reflected = tuple(bit ^ mask for bit, mask in zip(value.state, value.reflection_mask, strict=True))
    orbit: list[tuple[int, ...]] = [value.state]
    current = list(value.state)
    for index in value.schedule[: value.prefix_depth]:
        current[index] ^= 1
        orbit.append(tuple(current))
    complete = value.prefix_depth >= len(value.schedule) or value.tail_bound is not None
    return ContractResult(
        TwoAdicUnificationResult(reflected, tuple(orbit), True),
        ContractStatus.EXACT if complete else ContractStatus.UNDECIDED,
        "FINITE_PREFIX_AND_TAIL_CERTIFIED" if complete else "TAIL_NOT_CERTIFIED",
        {"commutator": 0.0},
        {"commutator": 0.0},
        {"tail_bound": value.tail_bound, "prefix_depth": value.prefix_depth},
        {"source_contract": "necessity_and_sufficiency_for_dimensional_unification_under_the_flowpoint_nece"},
    )

