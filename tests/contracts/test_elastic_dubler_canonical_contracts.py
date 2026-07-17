"""Contract, boundary, and source-removal tests for explicit Elastic Dubler laws."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.types import TNEContractError
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_SPECS,
    contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import elastic_dubler_sample


def test_explicit_elastic_dubler_inventory_and_dependencies():
    items = contracts()
    assert len(items) == 22
    assert {str(item.complex_id) for item in items} == {
        *A_IDS,
        *(item[0] for item in B_SPECS),
        *(item[0] for item in C_SPECS),
    }
    by_id = {str(item.complex_id): item for item in items}
    for b_id, source_a, source_b in B_SPECS:
        assert tuple(map(str, by_id[b_id].source_ids)) == (source_a, source_b)
    for c_id, source_a, source_b in C_SPECS:
        assert tuple(map(str, by_id[c_id].source_ids)) == (source_a, source_b)


def test_explicit_elastic_dubler_sample_closes_all_finite_contracts():
    sample = elastic_dubler_sample()
    for contract in contracts():
        output = contract.operator(sample)
        residual = contract.residual(sample, output) if contract.residual else None
        assert residual is not None and residual.passed, str(contract.complex_id)
        if contract.closure_predicate is not None:
            assert contract.closure_predicate(output, residual), str(contract.complex_id)


def test_elastic_dubler_b_and_c_sources_are_individually_necessary():
    sample = elastic_dubler_sample()
    for contract in contracts():
        if not contract.source_removal_checks:
            continue
        results = tuple(check(sample) for check in contract.source_removal_checks)
        assert len(results) == len(contract.source_ids)
        assert {str(item.source_id) for item in results} == set(map(str, contract.source_ids))
        assert all(item.necessary for item in results)
        assert all(item.necessity_residual > sample.tolerance for item in results)


@pytest.mark.parametrize(
    "mutator",
    (
        lambda sample: replace(sample, elasticity=0.0),
        lambda sample: replace(sample, domain_elasticity=np.zeros_like(sample.domain_elasticity)),
        lambda sample: replace(sample, parity=np.full(sample.parity.shape, 0.5, dtype=float)),
        lambda sample: replace(sample, coordinates=sample.coordinates[::-1]),
        lambda sample: replace(sample, pdfi=np.full_like(sample.pdfi, np.nan)),
    ),
)
def test_elastic_dubler_domain_boundaries_fail_closed(mutator):
    contract = contracts()[0]
    with pytest.raises(TNEContractError):
        contract.operator(mutator(elastic_dubler_sample()))


def test_elastic_dubler_spatial_closures_have_zero_boundary_and_positive_coercivity():
    sample = elastic_dubler_sample()
    for contract in contracts()[-3:]:
        output = contract.operator(sample)
        assert output.boundary_residual <= sample.tolerance
        assert output.reconstruction_residual <= sample.tolerance
        assert output.coercivity > 0.0
        assert output.status == "closed"
