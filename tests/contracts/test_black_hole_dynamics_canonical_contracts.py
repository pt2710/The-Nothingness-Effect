"""Contract, boundary, and source-removal tests for Black-Hole Dynamics."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_black_hole import (
    black_hole_sample,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import TNEContractError
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_ID,
    contracts,
)


def test_black_hole_inventory_and_dependencies():
    items = contracts()
    assert len(items) == 11
    assert {str(item.complex_id) for item in items} == {
        *A_IDS,
        *(item[0] for item in B_SPECS),
        C_ID,
    }
    by_id = {str(item.complex_id): item for item in items}
    for b_id, source_ids in B_SPECS:
        assert tuple(map(str, by_id[b_id].source_ids)) == source_ids
    assert tuple(map(str, by_id[C_ID].source_ids)) == tuple(item[0] for item in B_SPECS)


def test_black_hole_sample_closes_all_finite_contracts():
    sample = black_hole_sample()
    for contract in contracts():
        output = contract.operator(sample)
        residual = contract.residual(sample, output) if contract.residual else None
        assert residual is not None and residual.passed, str(contract.complex_id)
        if contract.closure_predicate is not None:
            assert contract.closure_predicate(output, residual), str(contract.complex_id)


def test_black_hole_sources_are_individually_necessary():
    sample = black_hole_sample()
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
        lambda sample: replace(sample, coordinate=sample.coordinate[::-1]),
        lambda sample: replace(sample, coordinate=np.asarray((0.0, 0.1, 0.3, 0.6, 1.0))),
        lambda sample: replace(sample, mass=np.zeros_like(sample.mass)),
        lambda sample: replace(sample, elasticity=0.0),
        lambda sample: replace(sample, visibility=np.full_like(sample.visibility, 1.5)),
        lambda sample: replace(sample, gravitational_memory=-np.ones_like(sample.gravitational_memory)),
        lambda sample: replace(sample, simulation=np.full_like(sample.simulation, np.nan)),
    ),
)
def test_black_hole_domain_boundaries_fail_closed(mutator):
    with pytest.raises(TNEContractError):
        contracts()[0].operator(mutator(black_hole_sample()))


def test_black_hole_spatial_closure_is_boundary_closed_and_coercive():
    sample = black_hole_sample()
    output = contracts()[-1].operator(sample)
    assert output.boundary_residual <= sample.tolerance
    assert output.reconstruction_residual <= sample.tolerance
    assert output.coercivity > 0.0
    assert output.status == "closed"
