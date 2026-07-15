"""Contract and source-removal tests for the Elastic-pi norm."""

from __future__ import annotations

import numpy as np

from equations.elastic_pi_norm.contracts import ElasticPiNormInput, contracts
from equations.theorem_complex_runtime.contracts import evaluate_contract
from equations.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


INPUT = ElasticPiNormInput(
    trajectory=np.array([1, 3, 8, 5, 12]),
    entropy=np.array([0.2, 0.7, 1.6, 2.1, 3.4]),
    K_D=4.0,
    p=2.0,
    anchored=False,
)


def test_all_eight_elastic_pi_norm_contracts_evaluate():
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts())

    assert len(evaluations) == 8
    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluations[-1].output.coercivity_ratio > 0.0


def test_every_derived_norm_source_is_necessary():
    for contract in contracts():
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(INPUT) for check in contract.source_removal_checks)
        assert {str(item.source_id) for item in removals} == {str(item) for item in contract.source_ids}
        assert all(item.necessary for item in removals)


def test_spatial_weighted_closure_is_not_promoted_to_attainment():
    evaluation = evaluate_contract(contracts()[-1], INPUT)

    assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
    assert "not promoted" in evaluation.detail
