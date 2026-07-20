"""Contract, boundary, and source-removal tests for Locality-Driven Gravity."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_locality_gravity import (
    locality_gravity_sample,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import TNEContractError
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_SPECS,
    contracts,
)


def test_locality_inventory_and_dependencies():
    items = contracts()
    assert len(items) == 16
    assert {str(item.complex_id) for item in items} == {
        *A_IDS,
        *(item[0] for item in B_SPECS),
        *(item[0] for item in C_SPECS),
    }
    by_id = {str(item.complex_id): item for item in items}
    for b_id, source_ids in B_SPECS:
        assert tuple(map(str, by_id[b_id].source_ids)) == source_ids
    for c_id, source_a, source_b in C_SPECS:
        assert tuple(map(str, by_id[c_id].source_ids)) == (source_a, source_b)


def test_locality_sample_closes_all_finite_contracts():
    sample = locality_gravity_sample()
    for contract in contracts():
        output = contract.operator(sample)
        residual = contract.residual(sample, output) if contract.residual else None
        assert residual is not None and residual.passed, str(contract.complex_id)
        if contract.closure_predicate is not None:
            assert contract.closure_predicate(output, residual), str(contract.complex_id)


def test_locality_sources_are_individually_necessary():
    sample = locality_gravity_sample()
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
        lambda sample: replace(sample, radius=sample.radius[::-1]),
        lambda sample: replace(sample, radius=np.asarray((1.0, 1.1, 1.3, 1.6, 2.0))),
        lambda sample: replace(sample, screening_mass=-1.0),
        lambda sample: replace(sample, elasticity=0.0),
        lambda sample: replace(sample, density=-np.ones_like(sample.density)),
        lambda sample: replace(sample, information=np.full_like(sample.information, np.nan)),
    ),
)
def test_locality_domain_boundaries_fail_closed(mutator):
    with pytest.raises(TNEContractError):
        contracts()[0].operator(mutator(locality_gravity_sample()))


def test_locality_spatial_closures_are_boundary_closed_and_coercive():
    sample = locality_gravity_sample()
    for contract in contracts()[-2:]:
        output = contract.operator(sample)
        assert output.boundary_residual <= sample.tolerance
        assert output.reconstruction_residual <= sample.tolerance
        assert output.coercivity > 0.0
        assert output.status == "closed"
