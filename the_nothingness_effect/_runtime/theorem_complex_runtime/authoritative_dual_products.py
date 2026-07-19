"""Exact finite certificates for appendix theorem/failure duals and products.

The AI appendix states each A complex as a positive law paired with its
complementary failure dual.  B and C complexes then form declared products of
those complete source carriers.  This module preserves the native source
operator and defect field, certifies the exhaustive/exclusive branch split,
and realizes every higher-order product by exact coordinate projections and
the coordinatewise involutive exchange.

These certificates close the declared finite executable semantics.  They are
not proof-assistant certificates and do not assert empirical validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Sequence

import numpy as np

from .exact_product_carrier import (
    ExactProductInput,
    ExactProductResult,
    evaluate_exact_product,
    exact_product_predicate,
    exact_product_residual,
)
from .invariants import source_removal_result
from .types import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
    SourceRemovalResult,
)


SourceLaw = Callable[[int, Any], Any]


@dataclass(frozen=True)
class ExactDualBranchCertificate:
    """Native source result plus an exact theorem/failure-dual partition."""

    law_name: str
    response: Any
    defect_field: Any
    defect_norm: float
    positive_branch: bool
    failure_dual_branch: bool
    branch_name: str
    failure_condition: str
    exhaustiveness_residual: float
    exclusivity_residual: float
    threshold_classification_residual: float


def _array(value: Any) -> np.ndarray:
    detach = getattr(value, "detach", None)
    if callable(detach):
        value = detach().cpu().numpy()
    return np.asarray(value, dtype=float).ravel().copy()


def evaluate_dual_source(
    index: int,
    value: Any,
    *,
    source_ids: tuple[str, ...],
    source_law: SourceLaw,
) -> ExactDualBranchCertificate:
    law = source_law(index, value)
    tolerance = float(value.tolerance)
    defect_norm = float(law.invariant_residual)
    positive = defect_norm <= tolerance
    failure = not positive
    return ExactDualBranchCertificate(
        law_name=str(source_ids[index]),
        response=law.response,
        defect_field=law.residual_field,
        defect_norm=defect_norm,
        positive_branch=positive,
        failure_dual_branch=failure,
        branch_name="positive" if positive else "failure_dual",
        failure_condition=str(law.failure_condition),
        exhaustiveness_residual=abs(float(positive) + float(failure) - 1.0),
        exclusivity_residual=float(positive and failure),
        threshold_classification_residual=float(
            positive != (defect_norm <= tolerance)
        ),
    )


def dual_source_residual(value: Any, output: ExactDualBranchCertificate) -> ResidualResult:
    vector = (
        output.exhaustiveness_residual,
        output.exclusivity_residual,
        output.threshold_classification_residual,
    )
    tolerance = float(value.tolerance)
    passed = max(vector) <= tolerance
    return ResidualResult(
        f"{output.law_name} theorem/failure-dual partition",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "branch": output.branch_name,
            "defect_norm": output.defect_norm,
            "failure_condition": output.failure_condition,
        },
    )


def _branch_states(
    certificate: ExactDualBranchCertificate,
) -> tuple[np.ndarray, np.ndarray]:
    diagnostic = np.asarray((certificate.defect_norm,), dtype=float)
    positive = np.concatenate(
        (
            np.asarray((float(certificate.positive_branch),), dtype=float),
            diagnostic,
            _array(certificate.response),
        )
    )
    failure = np.concatenate(
        (
            np.asarray((float(certificate.failure_dual_branch),), dtype=float),
            diagnostic,
            _array(certificate.defect_field),
        )
    )
    return positive, failure


def _dual_partition_residual(certificate: ExactDualBranchCertificate) -> float:
    return max(
        certificate.exhaustiveness_residual,
        certificate.exclusivity_residual,
        certificate.threshold_classification_residual,
    )


def _b_input(
    index: int,
    value: Any,
    *,
    source_ids: tuple[str, ...],
    b_source_groups: tuple[tuple[str, ...], ...],
    source_law: SourceLaw,
) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    group = b_source_groups[index]
    source_index = {identifier: position for position, identifier in enumerate(source_ids)}
    certificates = tuple(
        evaluate_dual_source(
            source_index[identifier],
            value,
            source_ids=source_ids,
            source_law=source_law,
        )
        for identifier in group
    )
    states = tuple(_branch_states(item) for item in certificates)
    residuals = tuple(_dual_partition_residual(item) for item in certificates)
    return ExactProductInput(
        first_states={identifier: states[position][0] for position, identifier in enumerate(group)},
        second_states={identifier: states[position][1] for position, identifier in enumerate(group)},
        first_residuals={identifier: residuals[position] for position, identifier in enumerate(group)},
        second_residuals={identifier: residuals[position] for position, identifier in enumerate(group)},
        tolerance=float(value.tolerance),
    )


def evaluate_b_product(
    index: int,
    value: Any,
    *,
    source_ids: tuple[str, ...],
    b_source_groups: tuple[tuple[str, ...], ...],
    source_law: SourceLaw,
) -> ExactProductResult:
    product_input = _b_input(
        index,
        value,
        source_ids=source_ids,
        b_source_groups=b_source_groups,
        source_law=source_law,
    )
    return evaluate_exact_product(product_input, source_ids=b_source_groups[index])


def _flatten_product(product: tuple[np.ndarray, ...]) -> np.ndarray:
    return np.concatenate(tuple(_array(item) for item in product))


def _c_input(
    index: int,
    value: Any,
    *,
    source_ids: tuple[str, ...],
    b_ids: tuple[str, ...],
    b_source_groups: tuple[tuple[str, ...], ...],
    c_source_groups: tuple[tuple[str, ...], ...],
    source_law: SourceLaw,
) -> ExactProductInput:
    if isinstance(value, ExactProductInput):
        return value
    group = c_source_groups[index]
    b_index = {identifier: position for position, identifier in enumerate(b_ids)}
    outputs = tuple(
        evaluate_b_product(
            b_index[identifier],
            value,
            source_ids=source_ids,
            b_source_groups=b_source_groups,
            source_law=source_law,
        )
        for identifier in group
    )
    return ExactProductInput(
        first_states={identifier: _flatten_product(outputs[position].first_product) for position, identifier in enumerate(group)},
        second_states={identifier: _flatten_product(outputs[position].second_product) for position, identifier in enumerate(group)},
        first_residuals={identifier: outputs[position].first_product_residual for position, identifier in enumerate(group)},
        second_residuals={identifier: outputs[position].second_product_residual for position, identifier in enumerate(group)},
        tolerance=float(value.tolerance),
    )


def evaluate_c_product(
    index: int,
    value: Any,
    *,
    source_ids: tuple[str, ...],
    b_ids: tuple[str, ...],
    b_source_groups: tuple[tuple[str, ...], ...],
    c_source_groups: tuple[tuple[str, ...], ...],
    source_law: SourceLaw,
) -> ExactProductResult:
    product_input = _c_input(
        index,
        value,
        source_ids=source_ids,
        b_ids=b_ids,
        b_source_groups=b_source_groups,
        c_source_groups=c_source_groups,
        source_law=source_law,
    )
    return evaluate_exact_product(product_input, source_ids=c_source_groups[index])


def _product_residual(value: Any, output: ExactProductResult, *, name: str) -> ResidualResult:
    if not isinstance(value, ExactProductInput):
        value = ExactProductInput(
            first_states={identifier: array for identifier, array in zip(output.source_ids, output.first_product)},
            second_states={identifier: array for identifier, array in zip(output.source_ids, output.second_product)},
            first_residuals={identifier: residual for identifier, residual in zip(output.source_ids, output.first_source_residuals)},
            second_residuals={identifier: residual for identifier, residual in zip(output.source_ids, output.second_source_residuals)},
            tolerance=float(value.tolerance),
        )
    return exact_product_residual(value, output, name=name)


def _product_vector(output: ExactProductResult) -> np.ndarray:
    return np.concatenate(
        tuple(_array(item) for item in (*output.first_product, *output.second_product))
    )


def _ablated(value: ExactProductInput, source_id: str) -> ExactProductInput:
    first = {key: _array(item) for key, item in value.first_states.items()}
    second = {key: _array(item) for key, item in value.second_states.items()}
    first[source_id] = np.zeros_like(first[source_id])
    second[source_id] = np.zeros_like(second[source_id])
    return ExactProductInput(
        first,
        second,
        dict(value.first_residuals),
        dict(value.second_residuals),
        value.tolerance,
    )


def _remove_product_source(
    product_input: ExactProductInput,
    source_ids: tuple[str, ...],
    position: int,
) -> SourceRemovalResult:
    baseline = evaluate_exact_product(product_input, source_ids=source_ids)
    source_id = source_ids[position]
    removed = evaluate_exact_product(
        _ablated(product_input, source_id),
        source_ids=source_ids,
    )
    return source_removal_result(
        ComplexId(source_id),
        _product_vector(baseline),
        _product_vector(removed),
        tolerance=1e-12,
    )


def build_contracts(
    *,
    appendix: str,
    appendix_sha256: str,
    implementation_path: str,
    input_type: type,
    input_name: str,
    input_description: str,
    source_ids: Sequence[str | ComplexId],
    b_ids: Sequence[str | ComplexId],
    c_ids: Sequence[str | ComplexId],
    b_source_groups: Sequence[Sequence[str | ComplexId]],
    c_source_groups: Sequence[Sequence[str | ComplexId]],
    source_law: SourceLaw,
    artifact_spec: ArtifactSpec,
) -> tuple[ComplexContract, ...]:
    """Build one exact A/B/C catalogue from native appendix source laws."""

    a_names = tuple(str(item) for item in source_ids)
    b_names = tuple(str(item) for item in b_ids)
    c_names = tuple(str(item) for item in c_ids)
    b_groups = tuple(tuple(str(item) for item in group) for group in b_source_groups)
    c_groups = tuple(tuple(str(item) for item in group) for group in c_source_groups)
    if len(b_names) != len(b_groups) or len(c_names) != len(c_groups):
        raise RuntimeError("authoritative product IDs and source groups must be bijective")
    if set(item for group in b_groups for item in group) - set(a_names):
        raise RuntimeError("B product references an undeclared A source")
    if set(item for group in c_groups for item in group) - set(b_names):
        raise RuntimeError("C product references an undeclared B source")

    source_domain = DomainSpec(input_name, input_description, (input_type,))
    product_domain = DomainSpec(
        f"{input_name} authoritative product carrier",
        "native finite input or explicit paired source-carrier states",
        (input_type, ExactProductInput),
    )
    result: list[ComplexContract] = []
    for index, identifier in enumerate(a_names):
        result.append(
            ComplexContract(
                ComplexId(identifier),
                appendix,
                appendix_sha256,
                ComplexLevel.A,
                (),
                source_domain,
                CodomainSpec(
                    f"{identifier} complete theorem/failure dual",
                    "native response and defect with an exhaustive, exclusive branch certificate",
                    (ExactDualBranchCertificate,),
                ),
                partial(
                    evaluate_dual_source,
                    index,
                    source_ids=a_names,
                    source_law=source_law,
                ),
                residual=dual_source_residual,
                exact_semantics=True,
                implementation_path=implementation_path,
            )
        )
    for index, identifier in enumerate(b_names):
        group = b_groups[index]
        operator = partial(
            evaluate_b_product,
            index,
            source_ids=a_names,
            b_source_groups=b_groups,
            source_law=source_law,
        )
        input_builder = partial(
            _b_input,
            index,
            source_ids=a_names,
            b_source_groups=b_groups,
            source_law=source_law,
        )
        result.append(
            ComplexContract(
                ComplexId(identifier),
                appendix,
                appendix_sha256,
                ComplexLevel.B,
                tuple(ComplexId(item) for item in group),
                product_domain,
                CodomainSpec(
                    f"{identifier} exact source product",
                    "coordinate recovery, localized source predicates, and involutive branch exchange",
                    (ExactProductResult,),
                ),
                operator,
                residual=lambda value, output, name=identifier, builder=input_builder: _product_residual(
                    builder(value), output, name=f"{name} exact product"
                ),
                source_removal_checks=tuple(
                    lambda value, position=position, group=group, builder=input_builder: _remove_product_source(
                        builder(value), group, position
                    )
                    for position in range(len(group))
                ),
                artifact_spec=artifact_spec,
                exact_semantics=True,
                implementation_path=implementation_path,
            )
        )
    for index, identifier in enumerate(c_names):
        group = c_groups[index]
        operator = partial(
            evaluate_c_product,
            index,
            source_ids=a_names,
            b_ids=b_names,
            b_source_groups=b_groups,
            c_source_groups=c_groups,
            source_law=source_law,
        )
        input_builder = partial(
            _c_input,
            index,
            source_ids=a_names,
            b_ids=b_names,
            b_source_groups=b_groups,
            c_source_groups=c_groups,
            source_law=source_law,
        )
        result.append(
            ComplexContract(
                ComplexId(identifier),
                appendix,
                appendix_sha256,
                ComplexLevel.C,
                tuple(ComplexId(item) for item in group),
                product_domain,
                CodomainSpec(
                    f"{identifier} exact product-field closure",
                    "exact coordinate recovery and coordinatewise involutive exchange",
                    (ExactProductResult,),
                ),
                operator,
                residual=lambda value, output, name=identifier, builder=input_builder: _product_residual(
                    builder(value), output, name=f"{name} exact product field"
                ),
                closure_predicate=exact_product_predicate,
                source_removal_checks=tuple(
                    lambda value, position=position, group=group, builder=input_builder: _remove_product_source(
                        builder(value), group, position
                    )
                    for position in range(len(group))
                ),
                artifact_spec=artifact_spec,
                exact_semantics=True,
                implementation_path=implementation_path,
            )
        )
    return tuple(result)
