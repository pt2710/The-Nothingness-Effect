"""Typed, fail-closed runtime for appendix theorem-complex implementations."""

from .contracts import ContractEvaluation, evaluate_contract
from .registry import ComplexInventoryRecord, TheoremComplexRegistry
from .types import (
    ArtifactManifest,
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    InvariantResult,
    NonFiniteValueError,
    ParameterConstraint,
    ResidualResult,
    SimulationResult,
    SourceRemovalResult,
    TNEContractError,
)

__all__ = [
    "ArtifactManifest",
    "ArtifactSpec",
    "ClosureStatus",
    "CodomainSpec",
    "ComplexContract",
    "ComplexId",
    "ComplexInventoryRecord",
    "ComplexLevel",
    "ContractEvaluation",
    "DomainSpec",
    "InvariantResult",
    "NonFiniteValueError",
    "ParameterConstraint",
    "ResidualResult",
    "SimulationResult",
    "SourceRemovalResult",
    "TNEContractError",
    "TheoremComplexRegistry",
    "evaluate_contract",
]
