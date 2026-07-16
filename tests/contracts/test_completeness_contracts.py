"""A/B/C gates for the fifteen authoritative completeness contracts."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from the_nothingness_effect.the_completeness_theorem.contracts import (
    APPENDIX_SHA256,
    A_IDS,
    B_IDS,
    C_IDS,
    AdmissibilityData,
    CompletenessInput,
    NoetherData,
    ProtectedTransportData,
    SheafData,
    SplittingData,
    TerminalData,
    contracts,
    derived_operator,
    registered_completeness_registry,
    spatial_operator,
)
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import (
    godel_boundary_system,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    ComplexLevel,
    DomainViolationError,
)


STATE = np.array([1.0, -0.5, 2.0, 0.75, 0.0, 0.0])
CLOSURE = np.diag([1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
PARITY = np.diag([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
EMBEDDING = np.concatenate((np.eye(4), np.zeros((4, 2))), axis=1)
RETRACTION = EMBEDDING.T
IDENTITY = np.eye(STATE.size)
LOCAL_CERTIFICATE = np.array([0.25, -0.5, 0.75, 1.0, 0.0, 0.0])


def fixture() -> CompletenessInput:
    return CompletenessInput(
        godel_boundary_system(),
        STATE,
        CLOSURE,
        PARITY,
        (1, 0, 1, 1, 0, 1),
        np.arange(STATE.size, dtype=float),
        AdmissibilityData(
            diameter=1.0,
            infinity_state=np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            infinity_involution=np.diag([-1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            observation_outcome_bit=0,
            theorem_bit=1,
        ),
        SplittingData(
            update_trajectory=(STATE.copy(), STATE.copy(), STATE.copy()),
            embedding=EMBEDDING,
            retraction=RETRACTION,
        ),
        ProtectedTransportData(
            protected_state=STATE,
            pullback_operator=PARITY,
        ),
        NoetherData(
            global_noether_map=IDENTITY,
            local_noether_map=IDENTITY,
            constant_injection=IDENTITY,
            transgression_map=IDENTITY,
            temporal_difference_map=IDENTITY,
            boundary_flux=np.zeros(STATE.size),
            common_codomain="charge-change",
        ),
        SheafData(
            local_certificates=(
                LOCAL_CERTIFICATE.copy(),
                LOCAL_CERTIFICATE.copy(),
                LOCAL_CERTIFICATE.copy(),
            ),
            transition_maps=(IDENTITY, IDENTITY, IDENTITY),
            cover_complete=True,
            descent_data_fixed=True,
        ),
        TerminalData(
            admissibility_representation_class=np.array([2.0, 2.0]),
            invariance_conservation_class=np.array([2.0, 2.0]),
            observable_samples=np.array([3.0, 3.0, 3.0]),
            endomorphism_samples=np.array([2.0, 2.0]),
        ),
    )


INPUT = fixture()


def _contract(identifier: str):
    return next(item for item in contracts() if str(item.complex_id) == identifier)


def test_all_fifteen_completeness_contracts_register_and_resolve_authoritative_dependencies():
    registry = registered_completeness_registry()

    assert len(registry.contracts()) == 15
    assert registry.counts()["registered_contracts"] == 15
    assert not [
        source
        for contract in registry.contracts()
        for source in contract.source_ids
        if source not in {item.complex_id for item in registry.contracts()}
    ]
    assert _contract(str(B_IDS[0])).source_ids == (A_IDS[1], A_IDS[2])
    assert _contract(str(C_IDS[0])).source_ids == (B_IDS[0], B_IDS[1], B_IDS[2])
    assert _contract(str(C_IDS[1])).source_ids == tuple(B_IDS)
    assert {item.appendix_source_sha256 for item in contracts()} == {APPENDIX_SHA256}


def test_completeness_contracts_evaluate_without_promoting_finite_closure_to_proof():
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts())

    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-2].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[0].output.obstruction_count > 0
    assert "proof" not in evaluations[-1].detail.lower()


def test_all_b_and_c_sources_are_necessary():
    for contract in contracts():
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(INPUT) for check in contract.source_removal_checks)
        assert {str(item.source_id) for item in removals} == {
            str(item) for item in contract.source_ids
        }
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


def test_every_b_law_has_non_cancellation_energy():
    for contract in contracts():
        if contract.level is ComplexLevel.B:
            assert contract.operator(INPUT).non_cancellation_energy > 0.0


def test_complex_07_decoder_is_defined_only_on_manifest_free_orbits_and_null_gate_is_separate():
    output = derived_operator(0, INPUT)
    assert output.domain_admitted
    assert output.decoder_defined
    assert output.free_orbit
    assert output.decoded_theorem_bit == INPUT.admissibility.theorem_bit
    assert not output.null_gate_detected

    null_input = replace(
        INPUT,
        admissibility=replace(INPUT.admissibility, diameter=0.0),
    )
    null_output = derived_operator(0, null_input)
    assert null_output.domain_admitted
    assert not null_output.decoder_defined
    assert null_output.decoded_theorem_bit is None
    assert null_output.null_gate_detected

    fixed_orbit = replace(
        INPUT,
        admissibility=replace(INPUT.admissibility, infinity_involution=IDENTITY),
    )
    fixed_output = derived_operator(0, fixed_orbit)
    assert not fixed_output.domain_admitted
    assert not fixed_output.decoder_defined
    assert not fixed_output.null_gate_detected


def test_complex_08_requires_attainment_even_when_the_idempotent_splits_exactly():
    nonattaining = replace(
        INPUT,
        splitting=replace(
            INPUT.splitting,
            update_trajectory=(STATE.copy(), STATE.copy() + 1.0),
        ),
    )
    output = derived_operator(1, nonattaining)

    assert output.splitting_residual == pytest.approx(0.0)
    assert output.attainment_residual > 0.0
    assert not output.domain_admitted
    assert np.allclose(output.derived_operator, 0.0)
    evaluation = evaluate_contract(_contract(str(B_IDS[1])), nonattaining)
    assert evaluation.status is ClosureStatus.OPEN


def test_noether_operator_and_residual_have_separate_types_and_boundary_flux_gates_commutation():
    output = derived_operator(3, INPUT)
    assert output.domain_admitted
    assert output.operator_codomain == "charge-change"
    assert output.residual_codomain != output.operator_codomain
    assert np.allclose(output.derived_operator, STATE)
    assert np.allclose(output.residual, 0.0)

    leaking = replace(
        INPUT,
        noether=replace(INPUT.noether, boundary_flux=np.ones(STATE.size)),
    )
    leaking_output = derived_operator(3, leaking)
    assert not leaking_output.domain_admitted
    assert leaking_output.boundary_flux_residual > 0.0
    assert evaluate_contract(_contract(str(B_IDS[3])), leaking).status is ClosureStatus.OPEN

    missing_codomain = replace(
        INPUT,
        noether=replace(INPUT.noether, common_codomain=""),
    )
    with pytest.raises(DomainViolationError):
        derived_operator(3, missing_codomain)


def test_complex_10_requires_fixed_overlap_data_and_the_cocycle_law():
    closure = spatial_operator(0, INPUT)
    assert closure.cover_complete
    assert closure.descent_data_fixed
    assert closure.global_section is not None
    assert closure.overlap_residuals == pytest.approx((0.0, 0.0, 0.0))
    assert closure.cocycle_residual == pytest.approx(0.0)

    bad_g79 = 2.0 * IDENTITY
    incompatible = replace(
        INPUT,
        sheaf=replace(
            INPUT.sheaf,
            transition_maps=(IDENTITY, IDENTITY, bad_g79),
        ),
    )
    open_output = spatial_operator(0, incompatible)
    assert open_output.global_section is None
    assert open_output.cocycle_residual > 0.0
    assert evaluate_contract(_contract(str(C_IDS[0])), incompatible).status is ClosureStatus.OPEN

    unfixed = replace(
        INPUT,
        sheaf=replace(INPUT.sheaf, descent_data_fixed=False),
    )
    assert spatial_operator(0, unfixed).closure_status == "open"


def test_terminal_observables_factor_through_the_unique_terminal_map():
    output = spatial_operator(1, INPUT)
    assert output.unique_terminal_map
    assert output.terminal_point == pytest.approx(np.array([2.0]))
    assert output.observable_constant == pytest.approx(3.0)
    assert output.terminal_factorization_residual == pytest.approx(0.0)

    nonfactorizing = replace(
        INPUT,
        terminal=replace(
            INPUT.terminal,
            observable_samples=np.array([3.0, 4.0, 3.0]),
        ),
    )
    failed = spatial_operator(1, nonfactorizing)
    assert not failed.unique_terminal_map
    assert failed.terminal_factorization_residual > 0.0
    assert evaluate_contract(_contract(str(C_IDS[1])), nonfactorizing).status is ClosureStatus.OPEN
