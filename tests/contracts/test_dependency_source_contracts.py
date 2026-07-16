"""Contract, failure-dual, and dependency-closure gates for phase-two A sources."""
from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    all_contracts,
    dependency_downgrades,
    release_statuses,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.dependency_sources import (
    FAMILY_IDS,
    SPEC_BY_ID,
    sample_input,
    source_ids,
    source_operator,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


def test_phase_two_defines_exactly_31_unique_a_level_sources():
    identifiers = source_ids()
    assert len(identifiers) == 31
    assert len(set(identifiers)) == 31
    assert set(identifiers) == set(SPEC_BY_ID)
    assert {family: len(ids) for family, ids in FAMILY_IDS.items()} == {
        "qenn": 8,
        "pgqenn": 6,
        "soinets": 14,
        "dfi": 3,
    }


def test_every_dependency_source_has_a_typed_satisfied_invariant_and_finite_failure_dual():
    catalog = {str(contract.complex_id): contract for contract in all_contracts()}
    for identifier in source_ids():
        contract = catalog[identifier]
        assert contract.level is ComplexLevel.A
        assert contract.source_ids == ()
        value = sample_input(identifier)
        evaluation = evaluate_contract(contract, value)
        output = evaluation.output
        assert evaluation.status is ClosureStatus.SATISFIED
        assert evaluation.residual is not None and evaluation.residual.passed
        assert output.invariant_residual <= value.tolerance
        assert output.failure_condition
        assert output.diagnostic_name
        assert np.isfinite(output.response).all()
        assert np.isfinite(output.residual_field).all()
        assert np.isfinite(output.failure_metric)
        assert np.isfinite(output.diagnostic_value)


def test_controlled_failure_dual_amplitude_is_observable_for_every_source():
    for identifier in source_ids():
        baseline = source_operator(identifier, sample_input(identifier))
        failure = source_operator(identifier, sample_input(identifier, failure=True))
        assert failure.failure_metric > baseline.failure_metric
        assert failure.failure_metric >= 8.0 * baseline.failure_metric
        assert failure.invariant_residual == baseline.invariant_residual


def test_catalog_has_no_duplicate_ids_after_dependency_source_registration():
    identifiers = [str(contract.complex_id) for contract in all_contracts()]
    assert len(identifiers) == len(set(identifiers))


def test_phase_two_matrix_closes_all_requested_dependencies():
    statuses = release_statuses()
    assert all(statuses[identifier] == "implemented" for identifier in source_ids())
    assert sum(status == "implemented" for status in statuses.values()) == 226
    assert dependency_downgrades() == ()
