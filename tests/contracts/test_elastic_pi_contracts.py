"""A/B/C contract tests for the canonical Elastic-pi architecture."""

from __future__ import annotations

import numpy as np

from equations.elastic_pi.contracts import ElasticPiInput, contracts
from equations.theorem_complex_runtime.contracts import evaluate_contract
from equations.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


INPUT = ElasticPiInput(
    entropy=np.array([0.2, 0.7, 1.8, 3.4, 5.5]),
    K_D=2.5,
    coordinates=np.linspace(0.0, 1.0, 5),
)


def test_all_seven_elastic_pi_contracts_evaluate():
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts())

    assert len(evaluations) == 7
    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[-1].output.closure_status == "numerical_candidate"


def test_every_derived_source_is_necessary():
    for contract in contracts():
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(INPUT) for check in contract.source_removal_checks)
        assert {str(item.source_id) for item in removals} == {str(item) for item in contract.source_ids}
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


def test_spatial_closure_is_candidate_not_a_claim_of_mathematical_attainment():
    contract = contracts()[-1]
    evaluation = evaluate_contract(contract, INPUT)

    assert contract.exact_semantics is False
    assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
    assert "not promoted" in evaluation.detail
