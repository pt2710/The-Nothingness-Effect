"""Recertified kernel-recursion contract."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import ContractResult, ContractStatus, scale_aware_tolerance


@dataclass(frozen=True)
class KernelRecursionInput:
    initial: np.ndarray
    update: np.ndarray
    steps: int
    balance_vector: np.ndarray | None = None
    convergence_bound: float | None = None


@dataclass(frozen=True)
class KernelRecursionResult:
    history: np.ndarray
    balance_trace: np.ndarray
    terminal_increment: float


def evaluate_kernel_recursion(value: KernelRecursionInput) -> ContractResult[KernelRecursionResult]:
    x = np.asarray(value.initial, dtype=float)
    update = np.asarray(value.update, dtype=float)
    balance = np.ones_like(x) if value.balance_vector is None else np.asarray(value.balance_vector, dtype=float)
    if x.ndim != 1 or update.shape != (x.size, x.size) or balance.shape != x.shape or value.steps < 1 or not all(np.all(np.isfinite(item)) for item in (x, update, balance)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_RECURSION_DOMAIN")
    history = [x]
    for _ in range(value.steps):
        history.append(update @ history[-1])
    stacked = np.stack(history)
    trace = stacked @ balance
    tol = scale_aware_tolerance(*stacked.ravel())
    preservation = float(np.max(np.abs(trace - trace[0])))
    increment = float(np.linalg.norm(stacked[-1] - stacked[-2]))
    broken = preservation > tol
    decided = value.convergence_bound is not None
    status = ContractStatus.FALSIFIED if broken else (ContractStatus.NUMERICAL_CANDIDATE if decided else ContractStatus.UNDECIDED)
    reason = "BALANCE_OR_KERNEL_BREAKDOWN" if broken else ("BOUNDED_CONVERGENCE_CANDIDATE" if decided else "LIMIT_EVIDENCE_MISSING")
    return ContractResult(KernelRecursionResult(stacked, trace, increment), status, reason, {"balance": preservation, "terminal_increment": increment}, {"balance": tol, "terminal_increment": value.convergence_bound or tol}, {"steps": value.steps}, {"source_contract": "kernel_recursion"})
