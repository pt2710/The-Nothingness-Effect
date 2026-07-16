"""Executable tests for the Spectrum-of-Infinities 10A -> 3B -> 3C slice."""

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
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.canonical_contracts import (
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
    C1,
    C2,
    C3,
    OBS_ERGODIC,
    OBS_SPECTRAL,
    OBS_TEMPORAL,
    SYMMETRY_SCHEDULE,
    AddressInput,
    CosmicLedgerInput,
    DFIInput,
    DecompositionInput,
    DualRealizabilityInput,
    ElasticProbeInput,
    EntropyInput,
    FactorMapInput,
    FinitizationInput,
    HistoryAccessibilityInput,
    LpInput,
    MeasurableScopeInput,
    MeasureTransferInput,
    MetricDeformationInput,
    NormalizationInput,
    ObservableLocalityInput,
    contracts,
)

IDENTITY_2 = np.eye(2)
IDENTITY_3 = np.eye(3)
PARTITION = np.eye(2)
HISTORIES_2 = np.asarray(((0, 0), (0, 1), (1, 0), (1, 1)), dtype=int)
ADDRESSES_2 = np.asarray((0.0, 0.25, 0.5, 0.75))
SCHEDULES = HISTORIES_2.copy()
INITIAL_BITS = np.zeros(4, dtype=int)
EXPECTED_HISTORIES = np.asarray(
    tuple(
        tuple(
            [0]
            + [
                int(np.bitwise_xor.reduce(schedule[: index + 1]))
                for index in range(schedule.size)
            ]
        )
        for schedule in SCHEDULES
    ),
    dtype=int,
)
PROJECTOR_MIDDLE = np.diag((0.0, 1.0, 0.0))

SAMPLES = {
    A1: NormalizationInput(np.asarray((1.0, 1.0)), 2.0),
    A2: DFIInput(np.asarray((1.0, 2.0, 4.0)), 3.0),
    A3: DecompositionInput(np.asarray((1.0, 2.0)), PARTITION),
    A4: LpInput(np.asarray((3.0, 4.0)), 4.0, 2.0),
    A5: EntropyInput(np.asarray((0.5, 0.5)), 2.0),
    A6: FinitizationInput(
        np.asarray((1.0, 2.0)),
        np.asarray(((0.0, 0.0), (0.5, 1.0), (1.0, 2.0))),
    ),
    A7: DualRealizabilityInput(IDENTITY_2, np.asarray((1.0, 2.0))),
    A8: MeasureTransferInput(
        np.asarray((0.5, 0.5)),
        np.asarray((0, 1)),
        np.asarray((0.5, 0.5)),
        2.0,
    ),
    A9: MeasurableScopeInput(
        np.asarray((1.0, 2.0)),
        np.asarray((True, True)),
        np.asarray((True, True)),
    ),
    A10: FactorMapInput(
        IDENTITY_2,
        IDENTITY_2,
        IDENTITY_2,
        np.asarray((1.0, 2.0)),
    ),
    B1: AddressInput(HISTORIES_2, ADDRESSES_2, np.full(4, 0.25), 4.0),
    B2: MetricDeformationInput(
        np.asarray(((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),
        IDENTITY_2,
        np.full(3, 1.0 / 3.0),
        np.asarray((1.0, 2.0, 3.0)),
        IDENTITY_3,
    ),
    B3: HistoryAccessibilityInput(
        INITIAL_BITS,
        SCHEDULES,
        EXPECTED_HISTORIES,
        4.0,
    ),
    C1: CosmicLedgerInput(ADDRESSES_2, HISTORIES_2, np.zeros((4, 1))),
    C2: ObservableLocalityInput(
        np.asarray((0.0, 1.0, 0.0)),
        np.asarray((0.0, 1.0, 0.0)),
        IDENTITY_3,
    ),
    C3: ElasticProbeInput(
        np.zeros(3),
        PROJECTOR_MIDDLE,
        PROJECTOR_MIDDLE,
        1.0,
    ),
}
IDS = (A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, B1, B2, B3, C1, C2, C3)


def test_slice_has_exact_native_shape_and_dependencies():
    items = contracts()
    assert tuple(item.complex_id for item in items) == IDS
    assert tuple(item.level for item in items) == (
        *(ComplexLevel.A for _ in range(10)),
        *(ComplexLevel.B for _ in range(3)),
        *(ComplexLevel.C for _ in range(3)),
    )
    assert items[10].source_ids == (A1, A9, A7)
    assert items[11].source_ids == (A1, A4, A5, A10, A7)
    assert items[12].source_ids == (
        SYMMETRY_SCHEDULE,
        A1,
        A9,
        A10,
        OBS_ERGODIC,
        A7,
    )
    assert items[13].source_ids == (B1, B3)
    assert items[14].source_ids == (OBS_TEMPORAL, OBS_SPECTRAL)
    assert items[15].source_ids == (B2, OBS_SPECTRAL)


@pytest.mark.parametrize("contract", contracts(), ids=lambda item: str(item.complex_id))
def test_each_contract_evaluates_with_finite_passing_residual(contract):
    evaluation = evaluate_contract(contract, SAMPLES[contract.complex_id])
    assert evaluation.residual is not None
    assert evaluation.residual.passed
    assert math.isfinite(evaluation.residual.norm)
    expected = (
        ClosureStatus.CLOSED
        if contract.level is ComplexLevel.C
        else ClosureStatus.SATISFIED
    )
    assert evaluation.status is expected


def test_source_laws_preserve_exact_finite_identities():
    for contract in contracts()[:10]:
        output = evaluate_contract(contract, SAMPLES[contract.complex_id]).output
        assert all(item == pytest.approx(0.0) for item in output.residuals)


def test_address_history_and_spatial_fields_are_exact():
    for contract in contracts()[10:]:
        output = evaluate_contract(contract, SAMPLES[contract.complex_id]).output
        assert all(item == pytest.approx(0.0) for item in output.residuals)


@pytest.mark.parametrize("contract", contracts()[10:], ids=lambda item: str(item.complex_id))
def test_every_higher_order_contract_requires_each_declared_source(contract):
    value = SAMPLES[contract.complex_id]
    removals = tuple(check(value) for check in contract.source_removal_checks)
    assert len(removals) == len(contract.source_ids)
    assert {result.source_id for result in removals} == set(contract.source_ids)
    assert all(result.necessary and result.necessity_residual > 0.0 for result in removals)


def test_spectrum_contracts_are_registered_in_canonical_catalog():
    pytest.importorskip("torch")
    catalog = {item.complex_id: item for item in all_contracts()}
    assert set(IDS) <= set(catalog)


@pytest.mark.parametrize(
    "contract,value",
    [
        (contracts()[0], NormalizationInput(np.asarray((1.0, 1.0)), 0.0)),
        (contracts()[1], DFIInput(np.asarray((0.0, 1.0)), 1.0)),
        (
            contracts()[2],
            DecompositionInput(np.asarray((1.0, 2.0)), np.asarray(((1, 2),))),
        ),
        (contracts()[3], LpInput(np.asarray((1.0, 2.0)), 1.0, 0.5)),
        (contracts()[4], EntropyInput(np.asarray((-1.0, 2.0)), 1.0)),
        (contracts()[5], FinitizationInput(np.asarray((1.0,)), np.asarray((1.0,)))),
        (contracts()[6], DualRealizabilityInput(np.eye(2), np.asarray((1.0,)))),
        (
            contracts()[7],
            MeasureTransferInput(
                np.asarray((1.0,)),
                np.asarray((2,)),
                np.asarray((1.0,)),
                1.0,
            ),
        ),
        (
            contracts()[8],
            MeasurableScopeInput(
                np.asarray((1.0, 2.0)),
                np.asarray((True,)),
                np.asarray((True, True)),
            ),
        ),
        (contracts()[9], FactorMapInput(np.eye(2), np.eye(3), np.eye(2), np.ones(2))),
        (
            contracts()[10],
            AddressInput(
                np.asarray(((0, 2),)),
                np.asarray((0.0,)),
                np.asarray((1.0,)),
                1.0,
            ),
        ),
        (
            contracts()[12],
            HistoryAccessibilityInput(
                np.asarray((0,)),
                np.asarray(((0, 2),)),
                np.asarray(((0, 0, 0),)),
                1.0,
            ),
        ),
        (
            contracts()[15],
            ElasticProbeInput(
                np.zeros(3),
                PROJECTOR_MIDDLE,
                PROJECTOR_MIDDLE,
                0.0,
            ),
        ),
    ],
)
def test_invalid_domains_fail_closed(contract, value):
    with pytest.raises(DomainViolationError):
        evaluate_contract(contract, value)
