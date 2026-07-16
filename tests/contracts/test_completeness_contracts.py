"""A/B/C gates for the fifteen completeness contracts."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    ComplexLevel,
)
from the_nothingness_effect.the_completeness_theorem.authoritative_obligations import (
    APPENDIX_SHA256,
    NoetherTransgression,
    NoetherTypeSeparation,
    SheafDescentCertificate,
    SplittingAttainment,
    TerminalObservableFactorization,
    TypedAdmissibilityDecoding,
)
from the_nothingness_effect.the_completeness_theorem.contracts import (
    CompletenessInput,
    contracts,
    registered_completeness_registry,
)
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import (
    godel_boundary_system,
)


STATE = np.array([1.0, -0.5, 2.0, 0.75, -1.25, 0.4])
CLOSURE = np.diag([1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
PARITY = np.diag([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
INPUT = CompletenessInput(
    godel_boundary_system(),
    STATE,
    CLOSURE,
    PARITY,
    (1, 0, 1, 1, 0, 1),
    np.arange(STATE.size, dtype=float),
)


def test_all_fifteen_completeness_contracts_register_and_resolve_dependencies():
    registry = registered_completeness_registry()

    assert len(registry.contracts()) == 15
    assert registry.counts()["registered_contracts"] == 15
    assert not [
        source
        for contract in registry.contracts()
        for source in contract.source_ids
        if source not in {item.complex_id for item in registry.contracts()}
    ]


def test_completeness_contracts_use_latest_authority_binding():
    assert {contract.appendix_source_sha256 for contract in contracts()} == {
        APPENDIX_SHA256
    }


def test_completeness_contracts_evaluate_without_promoting_finite_closure_to_proof():
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts())

    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-2].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[0].output.obstruction_count > 0
    assert "proof" not in evaluations[-1].detail.lower()


def test_authoritative_obligations_are_integrated_into_b_and_c_outputs():
    catalogue = contracts()
    b07 = catalogue[9].operator(INPUT)
    b08 = catalogue[10].operator(INPUT)
    b_noether = catalogue[12].operator(INPUT)
    c10 = catalogue[13].operator(INPUT)
    c_terminal = catalogue[14].operator(INPUT)

    assert isinstance(
        b07.authoritative_certificate,
        TypedAdmissibilityDecoding,
    )
    assert b07.authoritative_certificate.reconstructive_domain
    assert isinstance(b08.authoritative_certificate, SplittingAttainment)
    assert b08.authoritative_certificate.exact_splitting

    separation, transgression = b_noether.authoritative_certificate
    assert isinstance(separation, NoetherTypeSeparation)
    assert isinstance(transgression, NoetherTransgression)
    assert separation.types_separated
    assert transgression.commutation_domain_satisfied

    assert isinstance(c10.authoritative_certificate, SheafDescentCertificate)
    assert c10.authoritative_certificate.gluable
    assert isinstance(
        c_terminal.authoritative_certificate,
        TerminalObservableFactorization,
    )
    assert (
        c_terminal.authoritative_certificate.factors_through_unique_terminal_map
    )


def test_authoritative_boundaries_fail_closed_inside_catalogue():
    catalogue = contracts()

    fixed_orbit = replace(
        INPUT,
        typed_admissibility_free_orbit=False,
        typed_admissibility_gate=1.0,
    )
    assert evaluate_contract(
        catalogue[9],
        fixed_orbit,
    ).status is ClosureStatus.OPEN

    nonzero_flux = replace(INPUT, noether_boundary_flux=0.25)
    assert evaluate_contract(
        catalogue[12],
        nonzero_flux,
    ).status is ClosureStatus.OPEN

    missing_descent = replace(INPUT, fixed_descent_data=False)
    assert evaluate_contract(
        catalogue[13],
        missing_descent,
    ).status is ClosureStatus.OPEN

    nonterminal = replace(
        INPUT,
        terminal_observable_values=np.array(
            [1.0, 2.0, 1.0, 1.0, 1.0, 1.0]
        ),
        terminal_value=1.0,
    )
    assert evaluate_contract(
        catalogue[14],
        nonterminal,
    ).status is ClosureStatus.OPEN


def test_complex_08_nonattainment_is_reported_without_false_exactness():
    b08 = contracts()[10].operator(
        replace(
            INPUT,
            splitting_residual=0.0,
            splitting_infimum_attained=False,
        )
    )

    assert isinstance(b08.authoritative_certificate, SplittingAttainment)
    assert not b08.authoritative_certificate.exact_splitting


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
