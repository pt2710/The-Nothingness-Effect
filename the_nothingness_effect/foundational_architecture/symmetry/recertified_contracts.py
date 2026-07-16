"""Recertified order-two symmetry recursion."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ContractResult, ContractStatus, scale_aware_tolerance


@dataclass(frozen=True)
class SymmetryRecursionResult:
    invariant_sector: np.ndarray
    anti_invariant_sector: np.ndarray
    evolved: np.ndarray


def evaluate_order_two_symmetry_recursion(state, symmetry, recursion) -> ContractResult[SymmetryRecursionResult]:
    x = np.asarray(state, dtype=float); sigma = np.asarray(symmetry, dtype=float); operator = np.asarray(recursion, dtype=float)
    if x.ndim != 1 or sigma.shape != operator.shape or sigma.shape != (x.size, x.size) or not all(np.all(np.isfinite(item)) for item in (x, sigma, operator)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_SYMMETRY_DOMAIN")
    identity = np.eye(x.size); tol = scale_aware_tolerance(*sigma.ravel(), *operator.ravel())
    involution = float(np.linalg.norm(sigma @ sigma - identity)); commutator = float(np.linalg.norm(operator @ sigma - sigma @ operator))
    plus = (identity + sigma) @ x / 2.0; minus = (identity - sigma) @ x / 2.0
    leakage = float(np.linalg.norm((identity - sigma) @ (operator @ plus)) + np.linalg.norm((identity + sigma) @ (operator @ minus))) / 2.0
    residuals = {"involution": involution, "commutator": commutator, "sector_leakage": leakage}
    failed = max(residuals.values()) > tol
    return ContractResult(SymmetryRecursionResult(plus, minus, operator @ x), ContractStatus.FALSIFIED if failed else ContractStatus.NUMERICAL_CANDIDATE, "SYMMETRY_BROKEN" if failed else "SYMMETRY_RECURSION_CERTIFIED", residuals, {name: tol for name in residuals}, provenance={"source_contract": "order_two_symmetry_recursion"})
