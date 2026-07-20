"""Executable tests for the Uncountable-Infinity 10A -> 5B -> 2C slice."""

from __future__ import annotations

import math

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    ComplexLevel,
    DomainViolationError,
)
from the_nothingness_effect.foundational_architecture.uncountable_infinity.canonical_contracts import (
    A1,
    A2,
    A3,
    A4,
    A5,
    A6,
    A7,
    A8,
    A9,
    A10,
    B1,
    B2,
    B3,
    B4,
    B5,
    C1,
    C2,
    AdicRepairInput,
    BooleanInput,
    CoverageFieldInput,
    CoverageInput,
    DenseTraceInput,
    DualRepairInput,
    OperationalInput,
    PowerSetInput,
    PrefixInput,
    SuperpositionInput,
    TrajectoryInput,
    contracts,
)

AXES = ((1, 0, 1), (0, 1, 0), (1, 1, 0))
PREFIX = PrefixInput((1, 0, 1, 1, 0, 1), 4)
SAMPLES = {
    A1: TrajectoryInput((1, 0, 1, 1, 0, 1, 0, 1, 1)),
    A2: PowerSetInput((0, 1, 0, 1, 1, 0)),
    A3: DenseTraceInput((1.25, -0.5, 2.0), (1, 0, 1, 0, 1)),
    A4: PREFIX,
    A5: PREFIX,
    A6: PREFIX,
    A7: BooleanInput((1, 0, 1, 0), (0, 1, 1, 0)),
    A8: OperationalInput((1, 0, 1, 1), 2, ((1, 0),), (1,)),
    A9: CoverageInput((1, -2, 0), AXES, (0.0, 0.0, 0.0)),
    A10: DualRepairInput((0, 1, 3, -1)),
    B1: SuperpositionInput((1, 0, 1, 1, 0), (0, 1, 1, 0, 1)),
    B2: PREFIX,
    B3: PREFIX,
    B4: OperationalInput((1, 1, 0, 1), 2, ((0, 0),), (1,)),
    B5: AdicRepairInput(
        (1, -2, 0),
        ((1, 0, 1), (0, 1, 0), (1, 1, 1)),
        (0, 1, 3, -1),
    ),
    C1: PrefixInput((1, 0, 1, 1, 0, 1, 1, 0), 5),
    C2: CoverageFieldInput((1, -2, 0), AXES, 3, ((0, 0, 0),), (1,)),
}
IDS = (
    A1,
    A2,
    A3,
    A4,
    A5,
    A6,
    A7,
    A8,
    A9,
    A10,
    B1,
    B2,
    B3,
    B4,
    B5,
    C1,
    C2,
)


def test_contract_slice_has_exact_dependency_closed_shape():
    items = contracts()
    assert tuple(item.complex_id for item in items) == IDS
    assert tuple(item.level for item in items) == (
        *(ComplexLevel.A for _ in range(10)),
        *(ComplexLevel.B for _ in range(5)),
        ComplexLevel.C,
        ComplexLevel.C,
    )
    assert items[10].source_ids == (A1, A2)
    assert items[11].source_ids == (A3, A4)
    assert items[12].source_ids == (A5, A6)
    assert items[13].source_ids == (A7, A8)
    assert items[14].source_ids == (A9, A10)
    assert items[15].source_ids == (B1, B2)
    assert items[16].source_ids == (B3, B4, B5)
    assert all(item.implementation_path.endswith("canonical_contracts.py") for item in items)


@pytest.mark.parametrize("contract", contracts(), ids=lambda item: str(item.complex_id))
def test_each_contract_has_finite_passing_residual(contract):
    evaluation = evaluate_contract(contract, SAMPLES[contract.complex_id])
    assert evaluation.residual is not None
    assert evaluation.residual.passed
    assert math.isfinite(evaluation.residual.norm)
    assert evaluation.residual.norm <= SAMPLES[contract.complex_id].tolerance
    expected = (
        ClosureStatus.CLOSED
        if contract.level is ComplexLevel.C
        else ClosureStatus.SATISFIED
    )
    assert evaluation.status is expected


def test_binary_superposition_satisfies_valuation_peak_and_translation_laws():
    output = evaluate_contract(contracts()[10], SAMPLES[B1]).output
    assert np.allclose(
        output.union_coefficients + output.intersection_coefficients,
        output.left_coefficients + output.right_coefficients,
    )
    assert output.atom_index == 0
    assert output.valuation_residual == 0.0
    assert output.peak_decoder_residual == 0.0
    assert output.translation_residual == 0.0


def test_prefix_tree_reconstruction_is_coherent_and_within_tail_bound():
    output = evaluate_contract(contracts()[11], SAMPLES[B2]).output
    assert output.prefix_codes[-1] == SAMPLES[B2].bits[: SAMPLES[B2].depth]
    assert output.convergence_residual == 0.0
    assert output.tower_coherence_residual == 0.0
    assert output.decoder_residual == 0.0


def test_complement_skeleton_completion_is_reflection_invariant():
    output = evaluate_contract(contracts()[12], SAMPLES[B3]).output
    assert np.allclose(output.complement_skeleton, 1.0 - output.skeleton)
    assert output.exchange_residual == 0.0


def test_unresolved_boolean_decision_retains_both_extensions():
    output = evaluate_contract(contracts()[13], SAMPLES[B4]).output
    assert not output.resolved
    assert set(output.extension_labels) == {-1, 1}
    assert output.consensus_size == 2
    assert output.consensus_residual == 0.0


def test_adic_domain_repair_is_canonical_and_dually_closed():
    output = evaluate_contract(contracts()[14], SAMPLES[B5]).output
    assert output.repaired_axis_bits[2][-1] == 0
    assert output.canonical_residual == 0.0
    assert output.coverage_residual == 0.0
    assert output.dual_repair_residual == 0.0


def test_end_field_recovers_center_and_binary_tail_with_uniform_bound():
    output = evaluate_contract(contracts()[15], SAMPLES[C1]).output
    assert np.allclose(output.field, output.center + output.binary_tail)
    assert output.uniform_error <= output.error_bound + SAMPLES[C1].tolerance
    assert output.center_residual <= SAMPLES[C1].tolerance
    assert output.tail_residual <= SAMPLES[C1].tolerance


def test_complex_coverage_field_has_exact_real_projection_and_klein_orbit():
    output = evaluate_contract(contracts()[16], SAMPLES[C2]).output
    assert np.allclose(np.real(output.complex_field), output.real_coverage)
    assert output.reflected_fields.shape == (4, 3)
    assert output.consensus_size == 2
    assert output.real_coverage_residual == 0.0
    assert output.klein_group_residual == 0.0
    assert output.repair_residual == 0.0


@pytest.mark.parametrize("contract", contracts()[10:], ids=lambda item: str(item.complex_id))
def test_every_higher_order_contract_requires_every_declared_source(contract):
    value = SAMPLES[contract.complex_id]
    removals = tuple(check(value) for check in contract.source_removal_checks)
    assert len(removals) == len(contract.source_ids)
    assert {result.source_id for result in removals} == set(contract.source_ids)
    assert all(result.necessary and result.necessity_residual > 0.0 for result in removals)


def test_uncountable_contracts_are_registered_in_canonical_catalog():
    pytest.importorskip("torch")
    catalog = {item.complex_id: item for item in all_contracts()}
    assert set(IDS) <= set(catalog)


@pytest.mark.parametrize(
    "contract,value",
    [
        (contracts()[0], TrajectoryInput(())),
        (contracts()[0], TrajectoryInput((1, 0), time=1.5)),
        (contracts()[1], PowerSetInput((0, 2))),
        (contracts()[2], DenseTraceInput((1.0, 2.0), (1, 0))),
        (contracts()[3], PrefixInput((1, 0), 3)),
        (contracts()[6], BooleanInput((1, 0), (1,))),
        (contracts()[7], OperationalInput((1, 0), 1, ((0, 0),), (1,))),
        (
            contracts()[8],
            CoverageInput((1, 2, 3), ((1,), (0,)), (0.0, 0.0, 0.0)),
        ),
        (contracts()[9], DualRepairInput(())),
        (contracts()[10], SuperpositionInput((1, 0), (1,))),
        (
            contracts()[14],
            AdicRepairInput(
                (0, 0, 0),
                ((1,), (0,), (1,)),
                (1,),
                tolerance=float("nan"),
            ),
        ),
        (contracts()[16], CoverageFieldInput((0, 0, 0), AXES, 0, (), ())),
    ],
)
def test_invalid_domains_fail_closed(contract, value):
    with pytest.raises(DomainViolationError):
        evaluate_contract(contract, value)
