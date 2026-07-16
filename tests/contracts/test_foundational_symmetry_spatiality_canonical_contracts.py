"""Canonical contract gates for Foundational Symmetry and Spatiality."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    DomainViolationError,
)
from the_nothingness_effect.foundational_architecture.spatiality.canonical_contracts import (
    A1 as SPATIALITY_A1,
    A2 as SPATIALITY_A2,
    B1 as SPATIALITY_B1,
    B2 as SPATIALITY_B2,
    C1 as SPATIALITY_C1,
    OrbitClassificationInput,
    OrbitHarmonicInput,
    PhaseSpatialityInput,
    SpectralReconstructionInput,
    SquareRootLiftInput,
    contracts as spatiality_contracts,
)
from the_nothingness_effect.foundational_architecture.symmetry.canonical_contracts import (
    A1 as SYMMETRY_A1,
    A2 as SYMMETRY_A2,
    B1 as SYMMETRY_B1,
    B2 as SYMMETRY_B2,
    C1 as SYMMETRY_C1,
    GeneratorWordInput,
    OrbitActionInput,
    ScheduleParityInput,
    ScheduleTransportInput,
    ScheduleWordFieldInput,
    contracts as symmetry_contracts,
)


def _state() -> np.ndarray:
    return np.asarray((1.0, -2.0, 0.5), dtype=float)


def _samples() -> np.ndarray:
    indices = np.arange(5)
    return (
        np.exp(2j * np.pi * indices / 5)
        + 0.2 * np.exp(4j * np.pi * indices / 5)
    )


def _symmetry_values() -> dict[str, object]:
    state = _state()
    tape = (1, 0, 1, 1)
    identity = np.eye(state.size)
    return {
        str(SYMMETRY_A1): ScheduleParityInput(tape, state),
        str(SYMMETRY_A2): OrbitActionInput(state),
        str(SYMMETRY_B1): ScheduleTransportInput(tape, state, 0, 2),
        str(SYMMETRY_B2): GeneratorWordInput(state, (1, 0, 0), identity),
        str(SYMMETRY_C1): ScheduleWordFieldInput(tape, state, identity),
    }


def _spatiality_values() -> dict[str, object]:
    return {
        str(SPATIALITY_A1): OrbitClassificationInput(1.0 + 2.0j, 5),
        str(SPATIALITY_A2): PhaseSpatialityInput(1.0 + 2.0j, 0.7),
        str(SPATIALITY_B1): SquareRootLiftInput(1.0 + 2.0j, 5),
        str(SPATIALITY_B2): OrbitHarmonicInput(_samples()),
        str(SPATIALITY_C1): SpectralReconstructionInput(_samples()),
    }


def test_foundational_catalog_contains_exactly_ten_new_canonical_contracts():
    identifiers = {str(contract.complex_id) for contract in all_contracts()}
    expected = {
        *(str(identifier) for identifier in (SYMMETRY_A1, SYMMETRY_A2, SYMMETRY_B1, SYMMETRY_B2, SYMMETRY_C1)),
        *(str(identifier) for identifier in (SPATIALITY_A1, SPATIALITY_A2, SPATIALITY_B1, SPATIALITY_B2, SPATIALITY_C1)),
    }

    assert len(symmetry_contracts()) == 5
    assert len(spatiality_contracts()) == 5
    assert expected.issubset(identifiers)


def test_symmetry_schedule_decoder_transport_and_word_field_close_exactly():
    values = _symmetry_values()
    by_id = {str(contract.complex_id): contract for contract in symmetry_contracts()}

    schedule = evaluate_contract(by_id[str(SYMMETRY_A1)], values[str(SYMMETRY_A1)])
    transport = evaluate_contract(by_id[str(SYMMETRY_B1)], values[str(SYMMETRY_B1)])
    word = evaluate_contract(by_id[str(SYMMETRY_B2)], values[str(SYMMETRY_B2)])
    field = evaluate_contract(by_id[str(SYMMETRY_C1)], values[str(SYMMETRY_C1)])

    assert np.array_equal(schedule.output.tape_reconstruction, np.asarray((1, 0, 1, 1)))
    assert schedule.residual is not None and schedule.residual.passed
    assert transport.output.transport_exponent == 1
    assert np.array_equal(transport.output.transported_state, -_state())
    assert transport.residual is not None and transport.residual.passed
    assert word.output.word_parity == 1
    assert np.array_equal(word.output.word_action, -_state())
    assert word.residual is not None and word.residual.passed
    assert field.status is ClosureStatus.CLOSED
    assert field.residual is not None and field.residual.passed


def test_symmetry_b_and_c_sources_are_individually_necessary():
    values = _symmetry_values()
    for contract in symmetry_contracts():
        if not contract.source_removal_checks:
            continue
        results = tuple(check(values[str(contract.complex_id)]) for check in contract.source_removal_checks)
        assert len(results) == len(contract.source_ids)
        assert all(item.necessary and item.necessity_residual > 0.0 for item in results)


def test_symmetry_rejects_nonbinary_schedule_and_singular_conjugator():
    with pytest.raises(DomainViolationError):
        evaluate_contract(
            symmetry_contracts()[0],
            ScheduleParityInput((1, 2), _state()),
        )
    with pytest.raises(DomainViolationError):
        evaluate_contract(
            symmetry_contracts()[3],
            GeneratorWordInput(_state(), (1,), np.zeros((3, 3))),
        )


def test_spatiality_orbits_phase_lift_harmonics_and_reconstruction_close():
    values = _spatiality_values()
    by_id = {str(contract.complex_id): contract for contract in spatiality_contracts()}

    orbit = evaluate_contract(by_id[str(SPATIALITY_A1)], values[str(SPATIALITY_A1)])
    phase = evaluate_contract(by_id[str(SPATIALITY_A2)], values[str(SPATIALITY_A2)])
    lift = evaluate_contract(by_id[str(SPATIALITY_B1)], values[str(SPATIALITY_B1)])
    harmonic = evaluate_contract(by_id[str(SPATIALITY_B2)], values[str(SPATIALITY_B2)])
    reconstruction = evaluate_contract(by_id[str(SPATIALITY_C1)], values[str(SPATIALITY_C1)])

    assert orbit.output.orbit_classification == "free_C_5_orbit"
    assert orbit.residual is not None and orbit.residual.passed
    assert phase.residual is not None and phase.residual.passed
    assert lift.output.lifted_orbit.shape == (10,)
    assert lift.residual is not None and lift.residual.passed
    assert np.allclose(harmonic.output.reconstructed_samples, _samples())
    assert harmonic.residual is not None and harmonic.residual.passed
    assert np.allclose(reconstruction.output.reconstruction, _samples())
    assert reconstruction.status is ClosureStatus.CLOSED


def test_spatiality_b_and_c_sources_are_individually_necessary():
    values = _spatiality_values()
    for contract in spatiality_contracts():
        if not contract.source_removal_checks:
            continue
        results = tuple(check(values[str(contract.complex_id)]) for check in contract.source_removal_checks)
        assert len(results) == len(contract.source_ids)
        assert all(item.necessary and item.necessity_residual > 0.0 for item in results)


def test_spatiality_rejects_invalid_order_and_nonfinite_samples():
    with pytest.raises(DomainViolationError):
        evaluate_contract(
            spatiality_contracts()[0],
            OrbitClassificationInput(1.0 + 0.0j, 1),
        )
    with pytest.raises(DomainViolationError):
        evaluate_contract(
            spatiality_contracts()[3],
            OrbitHarmonicInput(np.asarray((1.0 + 0.0j, np.nan + 0.0j))),
        )
