"""Contract evaluation without proof-status inflation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .types import (
    ClosureStatus,
    ComplexContract,
    ComplexLevel,
    InvariantResult,
    ResidualResult,
)
from .validation import ensure_finite


@dataclass(frozen=True)
class ContractEvaluation:
    complex_id: str
    output: Any
    status: ClosureStatus
    invariant: InvariantResult | None
    residual: ResidualResult | None
    exact_semantics: bool
    detail: str


def evaluate_contract(
    contract: ComplexContract,
    value: Any,
    *,
    parameters: Mapping[str, Any] | None = None,
) -> ContractEvaluation:
    params = dict(parameters or {})
    contract.domain.validate(value)
    for constraint in contract.parameter_constraints:
        constraint.validate(params)
    output = contract.operator(value, **params)
    ensure_finite(output, name=f"{contract.complex_id} output")
    contract.codomain.validate(output)

    invariant = contract.invariant(value, output) if contract.invariant else None
    residual = contract.residual(value, output) if contract.residual else None

    if invariant is not None and not invariant.passed:
        status = ClosureStatus.OPEN
        detail = "declared invariant failed"
    elif residual is not None and not residual.passed:
        status = residual.status
        detail = "residual exceeds tolerance"
    elif contract.level is ComplexLevel.C:
        predicate = bool(contract.closure_predicate(output, residual))
        if not predicate:
            status = ClosureStatus.OPEN
            detail = "closure predicate failed"
        elif contract.exact_semantics:
            status = ClosureStatus.CLOSED
            detail = "exact closure predicate and residual satisfied"
        else:
            status = ClosureStatus.NUMERICAL_CANDIDATE
            detail = "finite numerical candidate; not promoted to a mathematical minimizer"
    else:
        status = ClosureStatus.SATISFIED
        detail = "typed source law and declared residuals satisfied"

    return ContractEvaluation(
        complex_id=str(contract.complex_id),
        output=output,
        status=status,
        invariant=invariant,
        residual=residual,
        exact_semantics=contract.exact_semantics,
        detail=detail,
    )
