"""Promote appendix-declared B/C products to exact product certificates."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from functools import partial
from typing import Any, Iterable

import numpy as np

from .contracts import ContractEvaluation, evaluate_contract
from .exact_product_carrier import (
    ExactProductInput,
    ExactProductResult,
    evaluate_exact_product,
    exact_product_predicate,
    exact_product_residual,
)
from .invariants import source_removal_result
from .types import (
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    SourceRemovalResult,
)


def _numeric_vector(value: Any) -> np.ndarray:
    """Deterministically flatten the numeric content of a typed result."""

    detach = getattr(value, "detach", None)
    if callable(detach):
        return _numeric_vector(detach().cpu().numpy())
    if isinstance(value, np.ndarray):
        array = np.asarray(value)
        if np.iscomplexobj(array):
            return np.concatenate((array.real.ravel(), array.imag.ravel())).astype(float)
        return np.asarray(array, dtype=float).ravel()
    if isinstance(value, (complex, np.complexfloating)):
        return np.asarray((float(value.real), float(value.imag)), dtype=float)
    if isinstance(value, (bool, int, float, np.number)):
        return np.asarray((float(value),), dtype=float)
    if isinstance(value, dict):
        parts = tuple(_numeric_vector(value[key]) for key in sorted(value))
    elif isinstance(value, (tuple, list)):
        parts = tuple(_numeric_vector(item) for item in value)
    elif is_dataclass(value):
        parts = tuple(_numeric_vector(getattr(value, item.name)) for item in fields(value))
    else:
        parts = ()
    nonempty = tuple(item for item in parts if item.size)
    if not nonempty:
        return np.asarray((0.0,), dtype=float)
    return np.concatenate(nonempty)


def _evaluation_states(
    evaluation: ContractEvaluation,
) -> tuple[np.ndarray, np.ndarray, float]:
    output = evaluation.output
    if isinstance(output, ExactProductResult):
        first = np.concatenate(tuple(_numeric_vector(item) for item in output.first_product))
        second = np.concatenate(tuple(_numeric_vector(item) for item in output.second_product))
        residual = max(output.first_product_residual, output.second_product_residual)
        return first, second, float(residual)

    first = _numeric_vector(output)
    residual_values: list[float] = []
    if evaluation.invariant is not None:
        residual_values.append(float(evaluation.invariant.residual))
    if evaluation.residual is not None:
        residual_values.extend(float(item) for item in evaluation.residual.vector)
    diagnostic = np.asarray(residual_values or (0.0,), dtype=float)
    second = np.concatenate((diagnostic, -first))
    passed = evaluation.status.value in {"satisfied", "closed"}
    return first, second, 0.0 if passed else float(np.linalg.norm(diagnostic))


def _product_input(
    value: Any,
    *,
    source_contracts: tuple[ComplexContract, ...],
) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    evaluations = tuple(evaluate_contract(contract, value) for contract in source_contracts)
    states = tuple(_evaluation_states(item) for item in evaluations)
    source_ids = tuple(str(contract.complex_id) for contract in source_contracts)
    return ExactProductInput(
        first_states={identifier: states[index][0] for index, identifier in enumerate(source_ids)},
        second_states={identifier: states[index][1] for index, identifier in enumerate(source_ids)},
        first_residuals={identifier: states[index][2] for index, identifier in enumerate(source_ids)},
        second_residuals={identifier: states[index][2] for index, identifier in enumerate(source_ids)},
        tolerance=float(getattr(value, "tolerance", 1e-8)),
    )


def _operator(value: Any, *, source_contracts: tuple[ComplexContract, ...]) -> ExactProductResult:
    product_input = _product_input(value, source_contracts=source_contracts)
    return evaluate_exact_product(
        product_input,
        source_ids=tuple(contract.complex_id for contract in source_contracts),
    )


def _vector(output: ExactProductResult) -> np.ndarray:
    return np.concatenate(
        tuple(_numeric_vector(item) for item in (*output.first_product, *output.second_product))
    )


def _remove(
    value: Any,
    *,
    source_contracts: tuple[ComplexContract, ...],
    position: int,
) -> SourceRemovalResult:
    product_input = _product_input(value, source_contracts=source_contracts)
    source_ids = tuple(str(contract.complex_id) for contract in source_contracts)
    baseline = evaluate_exact_product(product_input, source_ids=source_ids)
    source_id = source_ids[position]
    first = {key: np.asarray(item, dtype=float).copy() for key, item in product_input.first_states.items()}
    second = {key: np.asarray(item, dtype=float).copy() for key, item in product_input.second_states.items()}
    first[source_id] = np.zeros_like(first[source_id])
    second[source_id] = np.zeros_like(second[source_id])
    ablated_input = ExactProductInput(
        first,
        second,
        dict(product_input.first_residuals),
        dict(product_input.second_residuals),
        product_input.tolerance,
    )
    removed = evaluate_exact_product(ablated_input, source_ids=source_ids)
    return source_removal_result(
        ComplexId(source_id),
        _vector(baseline),
        _vector(removed),
        tolerance=1e-12,
    )


def _domain(original: DomainSpec) -> DomainSpec:
    validators = original.validator

    def validate(value: Any) -> bool:
        if isinstance(value, ExactProductInput):
            return True
        return True if validators is None else bool(validators(value))

    return DomainSpec(
        f"{original.name} exact declared product",
        f"{original.description}; explicit paired source states are also accepted",
        (*original.python_types, ExactProductInput),
        validator=validate,
    )


def promote_exact_products(
    contracts: Iterable[ComplexContract],
    target_ids: Iterable[str],
    *,
    implementation_path: str,
) -> tuple[ComplexContract, ...]:
    """Replace selected B/C carrier surrogates with exact source products."""

    original = tuple(contracts)
    by_id = {str(contract.complex_id): contract for contract in original}
    targets = frozenset(str(item) for item in target_ids)
    missing = targets - set(by_id)
    if missing:
        raise RuntimeError(f"exact product targets are missing: {sorted(missing)}")
    promoted: dict[str, ComplexContract] = {}

    def build(identifier: str) -> ComplexContract:
        if identifier in promoted:
            return promoted[identifier]
        contract = by_id[identifier]
        if identifier not in targets:
            promoted[identifier] = contract
            return contract
        if contract.level not in {ComplexLevel.B, ComplexLevel.C}:
            raise RuntimeError(f"exact declared product target is not B/C: {identifier}")
        sources = tuple(build(str(source_id)) for source_id in contract.source_ids)
        if not sources:
            raise RuntimeError(f"exact declared product has no sources: {identifier}")
        operator = partial(_operator, source_contracts=sources)
        input_builder = partial(_product_input, source_contracts=sources)
        def residual(
            value: Any,
            output: ExactProductResult,
            *,
            name: str = identifier,
            builder: Any = input_builder,
        ):
            return exact_product_residual(
                builder(value), output, name=f"{name} exact declared product"
            )
        removals = tuple(
            partial(_remove, source_contracts=sources, position=position)
            for position in range(len(sources))
        )
        promoted_contract = ComplexContract(
            contract.complex_id,
            contract.appendix,
            contract.appendix_source_sha256,
            contract.level,
            contract.source_ids,
            _domain(contract.domain),
            CodomainSpec(
                f"{identifier} exact declared product",
                "exact source projection recovery and coordinatewise involutive exchange",
                (ExactProductResult,),
            ),
            operator,
            residual=residual,
            closure_predicate=exact_product_predicate if contract.level is ComplexLevel.C else None,
            source_removal_checks=removals,
            artifact_spec=contract.artifact_spec,
            exact_semantics=True,
            implementation_path=implementation_path,
        )
        promoted[identifier] = promoted_contract
        return promoted_contract

    return tuple(build(str(contract.complex_id)) for contract in original)
