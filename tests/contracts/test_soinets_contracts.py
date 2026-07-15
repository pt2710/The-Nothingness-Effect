from __future__ import annotations

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.soinets.contracts import A_IDS, B_IDS, C_IDS, SOInetContractInput, contracts, derived_operator, source_operator, spatial_operator
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus, DomainViolationError, NonFiniteValueError


@pytest.fixture
def value():
    position = torch.linspace(0.2, 1.4, 18)
    features = torch.stack((position, position.square(), torch.sin(position), torch.cos(position)), dim=-1)
    return SOInetContractInput(torch.stack([features * (1.0 + 0.1 * index) for index in range(3)]))


def test_soinet_sources_match_authoritative_b19_b20_dependencies(value):
    configured = contracts()
    assert tuple(item.complex_id for item in configured) == (*A_IDS, *B_IDS, *C_IDS)
    assert configured[4].source_ids == (A_IDS[0], A_IDS[1])
    assert configured[5].source_ids == (A_IDS[2], A_IDS[3])
    assert all(evaluate_contract(item, value).output is not None for item in configured)
    assert all(source_operator(index, value).response.shape == value.modalities.shape for index in range(4))


def test_soinet_b_laws_are_non_cancelling_and_source_necessary(value):
    configured = contracts()
    for index in range(2):
        output = derived_operator(index, value)
        assert output.residual_energy >= output.non_cancellation_energy >= 0.0
        assert all(check(value).necessary for check in configured[4 + index].source_removal_checks)


def test_soinet_c_law_is_one_spatial_field_with_explicit_candidate_status(value):
    output = spatial_operator(value)
    assert output.local_operator.shape == value.modalities.shape
    assert output.boundary_trace_residual >= 0.0 and output.localization_residual >= 0.0
    assert output.observability_residual == 0.0
    assert output.closure_status == "numerical_candidate"
    assert evaluate_contract(contracts()[-1], value).status is ClosureStatus.NUMERICAL_CANDIDATE
    assert all(check(value).necessary for check in contracts()[-1].source_removal_checks)


def test_soinet_contracts_fail_closed(value):
    with pytest.raises(DomainViolationError):
        source_operator(0, SOInetContractInput(torch.ones((1, 4, 2))))
    invalid = value.modalities.clone()
    invalid[0, 0, 0] = float("nan")
    with pytest.raises(NonFiniteValueError):
        source_operator(0, SOInetContractInput(invalid))
