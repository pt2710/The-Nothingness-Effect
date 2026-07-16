"""Canonical orbit-level pDFI and parity recurrence."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite


@dataclass(frozen=True)
class ParityDFIResult:
    trajectory: np.ndarray
    parity_labels: np.ndarray
    parity_transitions: np.ndarray
    relative_increments: np.ndarray
    weighted_increments: np.ndarray
    value: float
    normalization: int


def _integer_trajectory(trajectory) -> np.ndarray:
    raw = np.asarray(trajectory)
    if raw.ndim != 1 or raw.size < 2:
        raise DomainViolationError("pDFI requires a one-dimensional trajectory with at least two states")
    ensure_finite(raw, name="pDFI trajectory")
    if not np.all(np.equal(raw, np.round(raw))):
        raise DomainViolationError("the orbit-level parity label x mod 2 requires integer-valued states")
    return raw.astype(np.int64)


def parity_dfi(trajectory) -> ParityDFIResult:
    r"""Evaluate N^-1 sum |P(x_n)-P(x_n-1)| |(x_n-x_n-1)/x_n-1|."""

    values = _integer_trajectory(trajectory)
    predecessors = values[:-1]
    zero_indices = tuple(int(item) for item in np.flatnonzero(predecessors == 0))
    if zero_indices:
        raise DomainViolationError(
            "pDFI relative increments are undefined at zero predecessors; "
            f"transition indices={zero_indices}"
        )
    parity = np.mod(values, 2)
    parity_transitions = np.abs(np.diff(parity)).astype(float)
    relative = np.abs(np.diff(values) / predecessors.astype(float))
    weighted = parity_transitions * relative
    ensure_finite((relative, weighted), name="pDFI increments")
    return ParityDFIResult(
        values,
        parity,
        parity_transitions,
        relative,
        weighted,
        float(np.sum(weighted) / weighted.size),
        int(weighted.size),
    )


def parity_inverse_recurrence(initial_response: float, steps: int) -> np.ndarray:
    """Return the declared positive inverse recurrence F_(n+1)=F_n^-1."""

    response = float(initial_response)
    if not np.isfinite(response) or response <= 0:
        raise DomainViolationError("pDFI recurrence requires a finite strictly positive response")
    if not isinstance(steps, int) or steps < 2:
        raise DomainViolationError("pDFI recurrence requires at least two integer steps")
    result = np.empty(steps, dtype=float)
    result[0] = response
    for index in range(1, steps):
        result[index] = 1.0 / result[index - 1]
    ensure_finite(result, name="pDFI inverse recurrence")
    return result
