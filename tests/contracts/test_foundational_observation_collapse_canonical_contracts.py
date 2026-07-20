"""Executable tests for the Observation-and-Collapse 8A -> 4B -> 4C slice."""

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
from the_nothingness_effect.foundational_architecture.observation_and_collapse.canonical_contracts import (
    A1,
    A2,
    A3,
    A4,
    A5,
    A6,
    A7,
    A8,
    B1,
    B2,
    B3,
    B4,
    C1,
    C2,
    C3,
    C4,
    AttractorInput,
    ClosureInput,
    DimensionalBindingInput,
    HorizonInput,
    InstrumentInput,
    LocalityInput,
    MeanErgodicInput,
    OutcomeClosureInput,
    OutcomeFieldInput,
    SpectralCollapseInput,
    StabilizationInput,
    TemporalCompressionInput,
    UniquenessInput,
    contracts,
)

IDENTITY = np.eye(2)
INVOLUTION = np.diag((1.0, -1.0))
FIXED = np.asarray((1.0, 0.0))
MIXED = np.asarray((1.0, 1.0)) / np.sqrt(2.0)
P0 = np.diag((1.0, 0.0))
P1 = np.diag((0.0, 1.0))
PROJECTORS = (P0, P1)
RELATION = np.asarray(((1, 1), (0, 1)), dtype=int)
HISTORIES = np.asarray(
    (
        ((1.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)),
        ((1.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)),
    )
)
HORIZON_T = np.asarray(((1.0, 0.5, 0.0, 0.0), (0.5, 0.25, 0.0, 0.0)))
HORIZON_S = np.asarray(((0.5, 0.25, 0.0, 0.0), (0.25, 0.125, 0.0, 0.0)))
SAMPLES = {
    A1: MeanErgodicInput(IDENTITY, FIXED, 8),
    A2: AttractorInput(FIXED, np.asarray(((0.25, -0.25), (-0.25, 0.25)))),
    A3: UniquenessInput(HISTORIES),
    A4: MeanErgodicInput(INVOLUTION, MIXED, 8),
    A5: ClosureInput(RELATION, np.asarray((1, 0)), np.asarray((1, 1))),
    A6: StabilizationInput((0, 0, 2), (0, 1, 2)),
    A7: InstrumentInput(PROJECTORS, MIXED),
    A8: MeanErgodicInput(INVOLUTION, MIXED, 8),
    B1: OutcomeClosureInput(RELATION, np.asarray((0, 0)), PROJECTORS, MIXED, 0),
    B2: SpectralCollapseInput(INVOLUTION, MIXED, 8),
    B3: TemporalCompressionInput(HISTORIES),
    B4: SpectralCollapseInput(INVOLUTION, MIXED, 8),
    C1: DimensionalBindingInput(P0, P0, MIXED),
    C2: LocalityInput(FIXED, FIXED, P0),
    C3: HorizonInput(HORIZON_T, HORIZON_S, 0.0),
    C4: OutcomeFieldInput(RELATION, np.asarray((0, 0)), PROJECTORS, P0, FIXED),
}
IDS = (A1, A2, A3, A4, A5, A6, A7, A8, B1, B2, B3, B4, C1, C2, C3, C4)


def test_slice_has_exact_native_shape_and_dependencies():
    items = contracts()
    assert tuple(item.complex_id for item in items) == IDS
    assert tuple(item.level for item in items) == (
        *(ComplexLevel.A for _ in range(8)),
        *(ComplexLevel.B for _ in range(4)),
        *(ComplexLevel.C for _ in range(4)),
    )
    assert items[8].source_ids == (A5, A7)
    assert items[9].source_ids == (A4, A8, A6)
    assert items[10].source_ids == (A1, A2, A3)
    assert items[11].source_ids == (A4, A8, A6)
    assert items[12].source_ids == (B2, B4)
    assert items[13].source_ids == (B3, B4)
    assert items[14].source_ids == (B3, B4)
    assert items[15].source_ids == (B1, B2, B4)


@pytest.mark.parametrize("contract", contracts(), ids=lambda item: str(item.complex_id))
def test_each_contract_evaluates_with_finite_passing_residual(contract):
    evaluation = evaluate_contract(contract, SAMPLES[contract.complex_id])
    assert evaluation.residual is not None
    assert evaluation.residual.passed
    assert math.isfinite(evaluation.residual.norm)
    expected = ClosureStatus.CLOSED if contract.level is ComplexLevel.C else ClosureStatus.SATISFIED
    assert evaluation.status is expected


def test_mean_ergodic_projection_and_spectral_selection_agree():
    projection = evaluate_contract(contracts()[3], SAMPLES[A4]).output
    ergodic = evaluate_contract(contracts()[7], SAMPLES[A8]).output
    pinning = evaluate_contract(contracts()[9], SAMPLES[B2]).output
    selection = evaluate_contract(contracts()[11], SAMPLES[B4]).output
    assert np.allclose(projection.fixed_projector, P0)
    assert np.allclose(ergodic.algebraic_projector, P0)
    assert np.allclose(pinning.invariant_projector, P0)
    assert np.allclose(selection.invariant_projector, P0)
    assert np.allclose(pinning.pinned_state, selection.selected_state)


def test_outcome_conditioned_closure_is_idempotent_and_repeatable():
    output = evaluate_contract(contracts()[8], SAMPLES[B1]).output
    assert np.array_equal(output.closed_support, np.asarray((1, 1)))
    assert np.allclose(output.conditional_state, FIXED)
    assert output.probability == pytest.approx(0.5)
    assert output.idempotence_residual == 0.0
    assert output.repeatability_residual == 0.0


def test_temporal_compression_has_one_common_output():
    output = evaluate_contract(contracts()[10], SAMPLES[B3]).output
    assert np.allclose(output.preparation_limits, np.asarray(((1.0, 0.0), (1.0, 0.0))))
    assert np.allclose(output.common_output, FIXED)
    assert output.common_limit_residual == 0.0
    assert output.cauchy_residual == 0.0


def test_spatial_observation_fields_close_exactly():
    binding = evaluate_contract(contracts()[12], SAMPLES[C1]).output
    locality = evaluate_contract(contracts()[13], SAMPLES[C2]).output
    horizon = evaluate_contract(contracts()[14], SAMPLES[C3]).output
    field = evaluate_contract(contracts()[15], SAMPLES[C4]).output
    assert binding.bound_dimension == 1
    assert np.allclose(binding.common_projector, P0)
    assert np.allclose(locality.local_output, 2.0 * FIXED)
    assert horizon.common_radius == 2
    assert horizon.leakage_residual == 0.0
    assert np.allclose(sum(field.sector_projectors), P0)
    assert field.reconstruction_residual == 0.0


@pytest.mark.parametrize("contract", contracts()[8:], ids=lambda item: str(item.complex_id))
def test_every_higher_order_contract_requires_each_declared_source(contract):
    value = SAMPLES[contract.complex_id]
    removals = tuple(check(value) for check in contract.source_removal_checks)
    assert len(removals) == len(contract.source_ids)
    assert {result.source_id for result in removals} == set(contract.source_ids)
    assert all(result.necessary and result.necessity_residual > 0.0 for result in removals)


def test_observation_contracts_are_registered_in_canonical_catalog():
    pytest.importorskip("torch")
    catalog = {item.complex_id: item for item in all_contracts()}
    assert set(IDS) <= set(catalog)


@pytest.mark.parametrize(
    "contract,value",
    [
        (contracts()[0], MeanErgodicInput(np.eye(2), np.asarray((1.0,)), 8)),
        (contracts()[0], MeanErgodicInput(np.eye(2), FIXED, 1)),
        (contracts()[1], AttractorInput(FIXED, np.asarray((1.0, 2.0)))),
        (contracts()[2], UniquenessInput(np.asarray((1.0, 2.0)))),
        (contracts()[4], ClosureInput(np.asarray(((1, 2), (0, 1))), np.asarray((1, 0)), np.asarray((1, 1)))),
        (contracts()[5], StabilizationInput((0, 3), (0,))),
        (contracts()[6], InstrumentInput((np.eye(2),), np.zeros(2))),
        (contracts()[8], OutcomeClosureInput(RELATION, np.asarray((0, 0)), PROJECTORS, MIXED, 4)),
        (contracts()[10], TemporalCompressionInput(np.asarray(((1.0, 2.0),)))),
        (contracts()[14], HorizonInput(HORIZON_T, HORIZON_S, -1.0)),
        (contracts()[15], OutcomeFieldInput(RELATION, np.asarray((0, 0)), PROJECTORS, P0, FIXED, tolerance=float("nan"))),
    ],
)
def test_invalid_domains_fail_closed(contract, value):
    with pytest.raises(DomainViolationError):
        evaluate_contract(contract, value)
