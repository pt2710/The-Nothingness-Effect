"""Core theorem-complex data types.

The types deliberately keep exact source-law semantics separate from numerical
approximations. Non-finite numerical values are never converted to neutral
values; callers must raise a domain-specific exception or return an explicit
singular/blocked status with a finite diagnostic residual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
import re
from typing import Any, Callable, Mapping


CLAIM_BOUNDARY = "finite computational support; not a formal proof substitute"
_COMPLEX_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")


class TNEContractError(ValueError):
    """Base exception for theorem-contract failures."""


class DomainViolationError(TNEContractError):
    """Raised when an input lies outside a declared domain."""


class CodomainViolationError(TNEContractError):
    """Raised when an operator result lies outside its declared codomain."""


class ParameterViolationError(TNEContractError):
    """Raised when a parameter condition is not satisfied."""


class NonFiniteValueError(TNEContractError):
    """Raised when NaN or infinity reaches a canonical source-law path."""


class SingularEvaluationError(TNEContractError):
    """Raised for an explicitly detected singularity or obstruction."""


@dataclass(frozen=True, order=True)
class ComplexId:
    """Stable theorem-complex identifier."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _COMPLEX_ID_PATTERN.fullmatch(normalized):
            raise ValueError(f"Invalid theorem-complex ID: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


class ComplexLevel(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class ClosureStatus(str, Enum):
    SATISFIED = "satisfied"
    OPEN = "open"
    BLOCKED = "blocked"
    CLOSED = "closed"
    NUMERICAL_CANDIDATE = "numerical_candidate"
    SINGULAR = "singular"
    INVALID_DOMAIN = "invalid_domain"
    INVALID_CODOMAIN = "invalid_codomain"
    NOT_IMPLEMENTED = "not_implemented"
    PROXY_ONLY = "proxy_only"


Validator = Callable[[Any], bool]


@dataclass(frozen=True)
class DomainSpec:
    name: str
    description: str
    python_types: tuple[type, ...] = ()
    shape: tuple[int | None, ...] | None = None
    validator: Validator | None = field(default=None, repr=False, compare=False)

    def validate(self, value: Any) -> None:
        if self.python_types and not isinstance(value, self.python_types):
            expected = ", ".join(item.__name__ for item in self.python_types)
            raise DomainViolationError(
                f"{self.name} expects ({expected}); received {type(value).__name__}"
            )
        if self.validator is not None and not bool(self.validator(value)):
            raise DomainViolationError(f"Value violates domain {self.name}: {self.description}")


@dataclass(frozen=True)
class CodomainSpec:
    name: str
    description: str
    python_types: tuple[type, ...] = ()
    validator: Validator | None = field(default=None, repr=False, compare=False)

    def validate(self, value: Any) -> None:
        if self.python_types and not isinstance(value, self.python_types):
            expected = ", ".join(item.__name__ for item in self.python_types)
            raise CodomainViolationError(
                f"{self.name} expects ({expected}); received {type(value).__name__}"
            )
        if self.validator is not None and not bool(self.validator(value)):
            raise CodomainViolationError(
                f"Value violates codomain {self.name}: {self.description}"
            )


@dataclass(frozen=True)
class ParameterConstraint:
    name: str
    description: str
    validator: Callable[[Any], bool] = field(repr=False, compare=False)

    def validate(self, parameters: Mapping[str, Any]) -> None:
        if self.name not in parameters:
            raise ParameterViolationError(f"Required parameter {self.name!r} is missing")
        if not bool(self.validator(parameters[self.name])):
            raise ParameterViolationError(
                f"Parameter {self.name!r} violates: {self.description}"
            )


def _finite_tuple(values: tuple[float, ...], label: str) -> None:
    if any(not math.isfinite(float(value)) for value in values):
        raise NonFiniteValueError(f"{label} contains NaN or infinity")


@dataclass(frozen=True)
class ResidualResult:
    name: str
    vector: tuple[float, ...]
    tolerance: float
    passed: bool
    status: ClosureStatus
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _finite_tuple(self.vector, self.name)
        if not math.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("Residual tolerance must be finite and non-negative")

    @property
    def norm(self) -> float:
        return math.sqrt(sum(float(value) ** 2 for value in self.vector))


@dataclass(frozen=True)
class InvariantResult:
    name: str
    passed: bool
    residual: float
    tolerance: float
    detail: str = ""

    def __post_init__(self) -> None:
        _finite_tuple((self.residual, self.tolerance), self.name)
        if self.tolerance < 0:
            raise ValueError("Invariant tolerance must be non-negative")


@dataclass(frozen=True)
class SourceRemovalResult:
    source_id: ComplexId
    baseline_response: float
    removed_response: float
    necessity_residual: float
    necessary: bool

    def __post_init__(self) -> None:
        _finite_tuple(
            (self.baseline_response, self.removed_response, self.necessity_residual),
            f"source removal {self.source_id}",
        )


@dataclass(frozen=True)
class ArtifactSpec:
    artifact_types: tuple[str, ...]
    regeneration_command: str
    tracked_policy: str = "compact deterministic outputs only"


@dataclass(frozen=True)
class SimulationResult:
    complex_id: ComplexId
    closure_status: ClosureStatus
    parameters: Mapping[str, Any]
    seed: int
    numeric_tolerances: Mapping[str, float]
    residual_vector: tuple[float, ...]
    generated_files: tuple[str, ...] = ()
    approximation_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _finite_tuple(self.residual_vector, f"simulation {self.complex_id}")


@dataclass(frozen=True)
class ArtifactManifest:
    theorem_complex_id: str
    appendix_filename: str
    appendix_source_sha256: str
    repository_start_commit: str
    repository_result_commit: str
    parameters: Mapping[str, Any]
    parameter_hash: str
    seed: int
    numeric_tolerances: Mapping[str, float]
    residual_vector: tuple[float, ...]
    closure_status: str
    generated_files: tuple[str, ...]
    regeneration_command: str
    claim_boundary: str = CLAIM_BOUNDARY
    approximation_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _finite_tuple(self.residual_vector, self.theorem_complex_id)
        if len(self.appendix_source_sha256) != 64:
            raise ValueError("appendix_source_sha256 must be a SHA-256 hex digest")

    def to_dict(self) -> dict[str, Any]:
        return {
            "theorem_complex_id": self.theorem_complex_id,
            "appendix_filename": self.appendix_filename,
            "appendix_source_sha256": self.appendix_source_sha256,
            "repository_start_commit": self.repository_start_commit,
            "repository_result_commit": self.repository_result_commit,
            "parameters": dict(self.parameters),
            "parameter_hash": self.parameter_hash,
            "seed": self.seed,
            "numeric_tolerances": dict(self.numeric_tolerances),
            "residual_vector": list(self.residual_vector),
            "closure_status": self.closure_status,
            "generated_files": list(self.generated_files),
            "regeneration_command": self.regeneration_command,
            "claim_boundary": self.claim_boundary,
            "approximation_metadata": dict(self.approximation_metadata),
        }


ContractOperator = Callable[..., Any]
InvariantCallable = Callable[[Any, Any], InvariantResult]
ResidualCallable = Callable[[Any, Any], ResidualResult]
ClosureCallable = Callable[[Any, ResidualResult | None], bool]
SourceRemovalCallable = Callable[..., SourceRemovalResult]
SimulationCallable = Callable[..., SimulationResult]


@dataclass(frozen=True)
class ComplexContract:
    complex_id: ComplexId
    appendix: str
    appendix_source_sha256: str
    level: ComplexLevel
    source_ids: tuple[ComplexId, ...]
    domain: DomainSpec
    codomain: CodomainSpec
    operator: ContractOperator = field(repr=False, compare=False)
    invariant: InvariantCallable | None = field(default=None, repr=False, compare=False)
    residual: ResidualCallable | None = field(default=None, repr=False, compare=False)
    closure_predicate: ClosureCallable | None = field(
        default=None, repr=False, compare=False
    )
    source_removal_checks: tuple[SourceRemovalCallable, ...] = field(
        default=(), repr=False, compare=False
    )
    simulation_runner: SimulationCallable | None = field(
        default=None, repr=False, compare=False
    )
    artifact_spec: ArtifactSpec | None = None
    parameter_constraints: tuple[ParameterConstraint, ...] = ()
    exact_semantics: bool = True
    implementation_path: str = ""

    def __post_init__(self) -> None:
        if len(self.appendix_source_sha256) != 64:
            raise ValueError("appendix_source_sha256 must be a SHA-256 hex digest")
        if self.level in (ComplexLevel.B, ComplexLevel.C) and len(self.source_ids) < 2:
            raise ValueError(f"{self.level.value}-level contracts require at least two sources")
        if self.level is ComplexLevel.C and self.closure_predicate is None:
            raise ValueError("C-level contracts require an explicit closure predicate")
