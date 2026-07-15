"""Contract and source-removal tests for pDFI."""

from __future__ import annotations

import numpy as np

from equations.parity_dfi.contracts import ParityDFIInput, contracts
from tne_runtime.theorem_complex_runtime.contracts import evaluate_contract
from tne_runtime.theorem_complex_runtime.types import ClosureStatus, ComplexLevel


INPUT = ParityDFIInput(np.array([7, 22, 11, 34, 17, 52]), response_seed=2.5, K_D=100.0)


def test_all_ten_pdfi_contracts_evaluate():
    evaluations = tuple(evaluate_contract(contract, INPUT) for contract in contracts())

    assert len(evaluations) == 10
    assert all(item.residual is None or item.residual.passed for item in evaluations)
    assert evaluations[-1].status is ClosureStatus.NUMERICAL_CANDIDATE


def test_every_b_and_c_source_is_necessary():
    for contract in contracts():
        if contract.level is ComplexLevel.A:
            continue
        removals = tuple(check(INPUT) for check in contract.source_removal_checks)
        assert {str(item.source_id) for item in removals} == {str(item) for item in contract.source_ids}
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)


def test_c_level_remains_a_numerical_candidate():
    contract = contracts()[-1]
    evaluation = evaluate_contract(contract, INPUT)

    assert contract.exact_semantics is False
    assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluation.output.boundary_trace_residual > 0.0
