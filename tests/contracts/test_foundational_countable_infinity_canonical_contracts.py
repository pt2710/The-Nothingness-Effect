"""Executable contract tests for the Countable-Infinity 3A -> 2B -> 1C slice."""

from __future__ import annotations

import math

import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    all_contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    ComplexLevel,
    DomainViolationError,
)
from the_nothingness_effect.foundational_architecture.countable_infinity.canonical_contracts import (
    A1,
    A2,
    A3,
    B1,
    B2,
    C1,
    CountableEnumerationInput,
    CoverDynamicsInput,
    CubicAccessibilityInput,
    FinitaryRecurrenceInput,
    ReflectedAddressInput,
    SignedCubicTransductionInput,
    contracts,
    shortlex_code,
    shortlex_decode,
)

SAMPLES = {
    A1: CountableEnumerationInput(7, (0, 5, 2)),
    A2: CubicAccessibilityInput(
        (0, 0, 0),
        (0, 2, 1, 2),
        (0.2, 0.3, 0.5),
    ),
    A3: FinitaryRecurrenceInput(1, 4, 8),
    B1: SignedCubicTransductionInput((0, 0, 0), (3, 1, 5)),
    B2: CoverDynamicsInput((0, 0, 0), 0, (1, 1, 1), 3),
    C1: ReflectedAddressInput((0, 0, 0), (0, 4, 5)),
}


def test_contract_slice_has_exact_dependency_closed_shape():
    items = contracts()
    assert [item.complex_id for item in items] == [A1, A2, A3, B1, B2, C1]
    assert [item.level for item in items] == [
        ComplexLevel.A,
        ComplexLevel.A,
        ComplexLevel.A,
        ComplexLevel.B,
        ComplexLevel.B,
        ComplexLevel.C,
    ]
    assert items[3].source_ids == (A1, A2)
    assert items[4].source_ids == (A2, A3)
    assert items[5].source_ids == (B1, B2)
    assert all(
        item.implementation_path.endswith("canonical_contracts.py")
        for item in items
    )


def test_shortlex_code_is_an_exact_bijection_on_finite_words():
    words = [(), (0,), (5,), (0, 5, 2), (5, 5, 5, 5)]
    codes = [shortlex_code(word) for word in words]
    assert len(codes) == len(set(codes))
    assert [shortlex_decode(code) for code in codes] == words


@pytest.mark.parametrize("contract", contracts(), ids=lambda item: str(item.complex_id))
def test_each_countable_contract_evaluates_with_zero_residual(contract):
    evaluation = evaluate_contract(contract, SAMPLES[contract.complex_id])
    assert evaluation.residual is not None
    assert evaluation.residual.passed
    assert evaluation.residual.norm == 0.0
    expected = (
        ClosureStatus.CLOSED
        if contract.level is ComplexLevel.C
        else ClosureStatus.SATISFIED
    )
    assert evaluation.status is expected


def test_cubic_accessibility_uses_positive_word_probability_and_full_orbit():
    evaluation = evaluate_contract(contracts()[1], SAMPLES[A2])
    output = evaluation.output
    assert output.endpoint == (1, 1, 0)
    assert output.parity_vector == (1, 1, 0)
    assert output.reachable_vertex_count == 8
    assert output.path_probability > 0.0
    assert math.isfinite(output.path_probability)


def test_finitary_flip_path_and_lazy_reflected_kernel_are_exact():
    evaluation = evaluate_contract(contracts()[2], SAMPLES[A3])
    output = evaluation.output
    assert output.transformed_state == 4
    assert output.inverse_state == 1
    assert output.boundary_row_sum == 1.0
    assert output.interior_row_sum == 1.0
    assert output.resistance_partial_sum == 4.0


def test_signed_transduction_has_parity_lock_and_canonical_section():
    evaluation = evaluate_contract(contracts()[3], SAMPLES[B1])
    output = evaluation.output
    assert output.displacement == 1
    assert output.endpoint == (1, 1, 1)
    assert shortlex_decode(output.canonical_address) == output.canonical_word
    assert output.parity_lock_residual == 0.0
    assert output.section_residual == 0.0


def test_cover_support_path_is_positive_reversible_and_parity_locked():
    evaluation = evaluate_contract(contracts()[4], SAMPLES[B2])
    output = evaluation.output
    assert output.path[0] == (0, (0, 0, 0))
    assert output.path[-1] == (3, (1, 1, 1))
    assert output.path_probability > 0.0
    assert output.detailed_balance_residual == 0.0
    assert output.parity_residual == 0.0


def test_reflected_address_closes_graph_quotient_and_orientation_reconstruction():
    evaluation = evaluate_contract(contracts()[5], SAMPLES[C1])
    output = evaluation.output
    assert output.local_degree == 6
    assert output.quotient_vertex[0] == abs(output.signed_vertex[0])
    assert output.full_expectation == output.quotient_expectation
    assert output.quotient_kernel_residual == 0.0
    assert output.reconstruction_residual == 0.0


@pytest.mark.parametrize("contract", contracts()[3:], ids=lambda item: str(item.complex_id))
def test_every_higher_order_contract_requires_each_declared_source(contract):
    value = SAMPLES[contract.complex_id]
    removals = tuple(check(value) for check in contract.source_removal_checks)
    assert len(removals) == len(contract.source_ids)
    assert {item.source_id for item in removals} == set(contract.source_ids)
    assert all(
        item.necessary and item.necessity_residual > 0.0 for item in removals
    )


def test_countable_contracts_are_registered_in_the_canonical_catalog():
    catalog = {item.complex_id: item for item in all_contracts()}
    assert {A1, A2, A3, B1, B2, C1} <= set(catalog)


@pytest.mark.parametrize(
    "contract,value",
    [
        (contracts()[0], CountableEnumerationInput(-1, (0,))),
        (contracts()[0], CountableEnumerationInput(1, (6,))),
        (
            contracts()[1],
            CubicAccessibilityInput((0, 0, 2), (0,), (0.2, 0.3, 0.5)),
        ),
        (
            contracts()[1],
            CubicAccessibilityInput((0, 0, 0), (0,), (0.2, 0.3, 0.4)),
        ),
        (contracts()[2], FinitaryRecurrenceInput(0, 1, 0)),
        (
            contracts()[3],
            SignedCubicTransductionInput((0, 0, 0), (7,)),
        ),
        (
            contracts()[4],
            CoverDynamicsInput((0, 0, 0), 0, (1, 0, 0), 0),
        ),
        (
            contracts()[5],
            ReflectedAddressInput((0, 0, 0), (0,), tolerance=float("nan")),
        ),
    ],
)
def test_invalid_domains_fail_closed(contract, value):
    with pytest.raises(DomainViolationError):
        evaluate_contract(contract, value)
