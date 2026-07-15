from __future__ import annotations

import pytest
import torch

from equations.artificial_intelligence.qenn.contracts import A_IDS, B_IDS, C_IDS, QENNContractInput, contracts, derived_operator, source_operator, spatial_operator
from equations.theorem_complex_runtime.contracts import evaluate_contract
from equations.theorem_complex_runtime.types import ClosureStatus, DomainViolationError, NonFiniteValueError


@pytest.fixture
def value():
    signal = torch.linspace(0.2, 1.4, 16).repeat(6, 1)
    signal = signal + torch.arange(6, dtype=signal.dtype).unsqueeze(1) * 0.01
    return QENNContractInput(signal)


def test_qenn_chain_has_exact_inventory_and_typed_results(value):
    configured = contracts()
    assert tuple(item.complex_id for item in configured) == (*A_IDS, *B_IDS, *C_IDS)
    assert all(evaluate_contract(item, value).output is not None for item in configured)
    assert all(source_operator(index, value).response.shape == value.signal.shape for index in range(4))


def test_qenn_b_laws_use_both_sources_and_are_non_cancelling(value):
    configured = contracts()
    for index in range(2):
        output = derived_operator(index, value)
        assert output.derived_operator.shape == value.signal.shape
        assert output.residual_energy >= output.non_cancellation_energy >= 0.0
        checks = configured[4 + index].source_removal_checks
        results = [check(value) for check in checks]
        assert len(results) == 2
        assert all(result.source_id in A_IDS for result in results)
        assert all(result.necessary for result in results)


def test_qenn_c_law_is_spatial_and_never_promoted_to_proof(value):
    configured = contracts()
    output = spatial_operator(value)
    assert output.local_operator.shape == value.signal.shape
    assert output.spatial_domain.shape == (value.signal.shape[-1],)
    assert output.closure_status in {"open", "numerical_candidate"}
    evaluation = evaluate_contract(configured[-1], value)
    assert evaluation.status in {ClosureStatus.OPEN, ClosureStatus.NUMERICAL_CANDIDATE}
    assert all(check(value).necessary for check in configured[-1].source_removal_checks)


def test_qenn_contracts_fail_closed():
    with pytest.raises(DomainViolationError):
        source_operator(0, QENNContractInput(torch.ones(3)))
    with pytest.raises(DomainViolationError):
        source_operator(1, QENNContractInput(torch.zeros((2, 4))))
    invalid = torch.ones((2, 4))
    invalid[0, 0] = float("nan")
    with pytest.raises(NonFiniteValueError):
        source_operator(0, QENNContractInput(invalid))
