"""Typed adapters used by generated 1X, 2X, and 1X2X theorem modules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Mapping

from .catalog import active_contracts
from .contracts import ContractEvaluation, evaluate_contract


class TheoremRole(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    CROSS = "cross"


class UnimplementedTheoremError(NotImplementedError):
    """Raised when a proxy or blocked component is evaluated as canonical."""


@dataclass(frozen=True)
class TheoremComponentResult:
    complex_id: str
    role: TheoremRole
    authoritative_title: str
    equation_labels: tuple[str, ...]
    evaluation: ContractEvaluation


@lru_cache(maxsize=1)
def _contract_map():
    return {str(contract.complex_id): contract for contract in active_contracts()}


@dataclass(frozen=True)
class TheoremComponent:
    complex_id: str
    role: TheoremRole
    authoritative_title: str
    authoritative_title_tex: str
    equation_labels: tuple[str, ...]
    implementation_status: str

    def evaluate(
        self,
        value: Any,
        *,
        parameters: Mapping[str, Any] | None = None,
    ) -> TheoremComponentResult:
        if self.implementation_status != "implemented":
            raise UnimplementedTheoremError(
                f"{self.complex_id}/{self.role.value} is {self.implementation_status}; "
                "no canonical numerical evaluation is permitted"
            )
        contract = _contract_map().get(self.complex_id)
        if contract is None:
            raise RuntimeError(f"active contract missing for {self.complex_id}")
        evaluation = evaluate_contract(contract, value, parameters=parameters)
        return TheoremComponentResult(
            complex_id=self.complex_id,
            role=self.role,
            authoritative_title=self.authoritative_title,
            equation_labels=self.equation_labels,
            evaluation=evaluation,
        )
