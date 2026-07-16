"""Fail-closed result envelope for recertified theorem source contracts.

The status vocabulary is deliberately independent of numerical closure status:
an estimator may be a numerical candidate, but it is never silently promoted
to an exact theorem statement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Generic, Mapping, TypeVar

from .types import NonFiniteValueError


class ContractStatus(str, Enum):
    EXACT = "exact"
    NUMERICAL_CANDIDATE = "numerical_candidate"
    UNDECIDED = "undecided"
    FALSIFIED = "falsified"
    INVALID_INPUT = "invalid_input"


T = TypeVar("T")


@dataclass(frozen=True)
class ContractResult(Generic[T]):
    """Typed result plus explicit evidence and claim boundary."""

    value: T | None
    status: ContractStatus
    reason_code: str
    residuals: Mapping[str, float] = field(default_factory=dict)
    tolerances: Mapping[str, float] = field(default_factory=dict)
    witnesses: Mapping[str, object] = field(default_factory=dict)
    provenance: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for collection_name, values in (
            ("residuals", self.residuals),
            ("tolerances", self.tolerances),
        ):
            for name, raw in values.items():
                value = float(raw)
                if not math.isfinite(value):
                    raise NonFiniteValueError(
                        f"{collection_name}.{name} contains NaN or infinity"
                    )
                if collection_name == "tolerances" and value < 0.0:
                    raise ValueError(f"tolerance {name!r} must be non-negative")

    @property
    def is_exact(self) -> bool:
        return self.status is ContractStatus.EXACT

    @property
    def accepted_candidate(self) -> bool:
        return self.status in {
            ContractStatus.EXACT,
            ContractStatus.NUMERICAL_CANDIDATE,
        }


def scale_aware_tolerance(*values: float, absolute: float = 1e-12, relative: float = 1e-10) -> float:
    """Return a finite tolerance without changing exact semantics."""

    numeric = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in numeric):
        raise NonFiniteValueError("scale-aware tolerance received NaN or infinity")
    scale = max((abs(value) for value in numeric), default=1.0)
    return max(float(absolute), float(relative) * max(1.0, scale))

