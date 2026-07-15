from __future__ import annotations

from pathlib import Path

from tne_runtime.theorem_complex_runtime import ComplexContract, TheoremComplexRegistry

from .a_level import contracts as a_contracts
from .b_level import contracts as b_contracts
from .c_level import contracts as c_contracts


def mathematical_closure_contracts() -> tuple[ComplexContract, ...]:
    return a_contracts() + b_contracts() + c_contracts()


def registered_mathematical_closure_registry(
    matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv",
) -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in mathematical_closure_contracts():
        registry.register(contract)
    return registry
