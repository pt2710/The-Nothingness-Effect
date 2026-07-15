from __future__ import annotations

import pytest
import torch

from equations.artificial_intelligence.pgqenn.contracts import A_IDS, B_IDS, C_IDS, PGQENNContractInput, contracts, derived_operator, source_operator, spatial_operator
from equations.artificial_intelligence.pgqenn.growth_law import CanonicalPrimeGrowth
from equations.theorem_complex_runtime.contracts import evaluate_contract
from equations.theorem_complex_runtime.types import ClosureStatus, DomainViolationError, NonFiniteValueError


@pytest.fixture
def value():
    graph = CanonicalPrimeGrowth().build(11)
    base = torch.linspace(0.3, 1.1, 6).repeat(11, 1)
    features = base + torch.arange(11, dtype=base.dtype).unsqueeze(1) * 0.01
    return PGQENNContractInput(graph, features)


def test_pgqenn_inventory_and_all_typed_outputs(value):
    configured = contracts()
    assert tuple(item.complex_id for item in configured) == (*A_IDS, *B_IDS, *C_IDS)
    assert all(evaluate_contract(item, value).output is not None for item in configured)
    assert all(source_operator(index, value).response.shape == value.node_features.shape for index in range(4))


def test_pgqenn_b_laws_are_non_cancelling_and_source_necessary(value):
    configured = contracts()
    for index in range(2):
        output = derived_operator(index, value)
        assert output.residual_energy >= output.non_cancellation_energy >= 0.0
        assert all(check(value).necessary for check in configured[4 + index].source_removal_checks)


def test_pgqenn_c_law_has_graph_local_boundary_and_observability(value):
    output = spatial_operator(value)
    assert output.spatial_domain == value.graph.primes
    assert output.boundary_trace_residual >= 0.0
    assert output.localization_residual >= 0.0
    assert output.observability_residual == 0.0
    assert output.closure_status == "numerical_candidate"
    evaluation = evaluate_contract(contracts()[-1], value)
    assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
    assert all(check(value).necessary for check in contracts()[-1].source_removal_checks)


def test_pgqenn_contracts_fail_closed(value):
    with pytest.raises(DomainViolationError):
        source_operator(0, PGQENNContractInput(value.graph, torch.ones((2, 3))))
    invalid = value.node_features.clone()
    invalid[0, 0] = float("inf")
    with pytest.raises(NonFiniteValueError):
        source_operator(0, PGQENNContractInput(value.graph, invalid))
