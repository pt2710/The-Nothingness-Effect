"""Typed, fail-closed runtime for appendix theorem-complex implementations."""

from .contracts import ContractEvaluation, evaluate_contract
from .contract_protocol import ContractResult, ContractStatus, scale_aware_tolerance
from .generated import (
    TheoremComponent,
    TheoremComponentResult,
    TheoremRole,
    UnimplementedTheoremError,
)
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
    "ContractResult",
    "ContractStatus",
    "DomainSpec",
    "InvariantResult",
    "NonFiniteValueError",
    "ParameterConstraint",
    "ResidualResult",
    "SimulationResult",
    "SourceRemovalResult",
    "TNEContractError",
    "TheoremComplexRegistry",
    "TheoremComponent",
    "TheoremComponentResult",
    "TheoremRole",
    "UnimplementedTheoremError",
    "evaluate_contract",
    "scale_aware_tolerance",
]
