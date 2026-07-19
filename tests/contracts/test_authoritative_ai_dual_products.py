"""Exact closure and failure gates for PGQENN and SOInet dual products."""

from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import ExactProductInput
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus, ComplexLevel
from the_nothingness_effect.artificial_intelligence.pgqenn.authoritative_contracts import (
    A_IDS as PG_A_IDS,
    B_IDS as PG_B_IDS,
    C_IDS as PG_C_IDS,
    contracts as pgqenn_contracts,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite import fixture as pgqenn_fixture
from the_nothingness_effect.artificial_intelligence.soinets.authoritative_contracts import (
    A_IDS as SOI_A_IDS,
    B_IDS as SOI_B_IDS,
    C_IDS as SOI_C_IDS,
    contracts as soinets_contracts,
)
from the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite import fixture as soinets_fixture


@pytest.mark.parametrize(
    ("factory", "fixture", "a_ids", "b_ids", "c_ids"),
    (
        (pgqenn_contracts, pgqenn_fixture, PG_A_IDS, PG_B_IDS, PG_C_IDS),
        (soinets_contracts, soinets_fixture, SOI_A_IDS, SOI_B_IDS, SOI_C_IDS),
    ),
)
def test_authoritative_ai_catalogues_close_complete_duals_and_products(
    factory,
    fixture,
    a_ids,
    b_ids,
    c_ids,
):
    catalogue = {str(item.complex_id): item for item in factory()}
    value = fixture()

    assert set(catalogue) == {*a_ids, *b_ids, *c_ids}
    for identifier in a_ids:
        evaluation = evaluate_contract(catalogue[identifier], value)
        assert evaluation.status is ClosureStatus.SATISFIED
        assert evaluation.exact_semantics
        assert evaluation.output.positive_branch != evaluation.output.failure_dual_branch
    for identifier in b_ids:
        evaluation = evaluate_contract(catalogue[identifier], value)
        assert evaluation.status is ClosureStatus.SATISFIED
        assert evaluation.output.exchange_square_residual == 0.0
    for identifier in c_ids:
        evaluation = evaluate_contract(catalogue[identifier], value)
        assert evaluation.status is ClosureStatus.CLOSED
        assert evaluation.output.closure_status == "closed"


@pytest.mark.parametrize(
    ("factory", "fixture"),
    ((pgqenn_contracts, pgqenn_fixture), (soinets_contracts, soinets_fixture)),
)
def test_authoritative_ai_products_recompute_every_source_removal(factory, fixture):
    value = fixture()
    for contract in factory():
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(value) for check in contract.source_removal_checks)
        assert len(removals) == len(contract.source_ids)
        assert {str(item.source_id) for item in removals} == {
            str(item) for item in contract.source_ids
        }
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


@pytest.mark.parametrize("factory", (pgqenn_contracts, soinets_contracts))
def test_authoritative_ai_product_defect_fails_closed(factory):
    contract = next(item for item in factory() if item.level is ComplexLevel.B)
    first, second = (str(item) for item in contract.source_ids)
    value = ExactProductInput(
        first_states={first: np.array([1.0]), second: np.array([2.0])},
        second_states={first: np.array([3.0]), second: np.array([4.0])},
        first_residuals={first: 0.0, second: 1e-3},
        second_residuals={first: 0.0, second: 0.0},
        tolerance=1e-6,
    )
    evaluation = evaluate_contract(contract, value)
    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.residual is not None and not evaluation.residual.passed
