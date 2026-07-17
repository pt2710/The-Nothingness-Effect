"""Contract, boundary, and source-removal tests for Elastic-pi Ripples."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_pi_ripples import (
    elastic_pi_ripple_sample,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import TNEContractError
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.canonical_contracts import (
    A_IDS,
    B_SPECS,
    C_ID,
    contracts,
)


def test_ripple_inventory_and_dependencies():
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


def test_ripple_sample_closes_all_finite_contracts():
    sample = elastic_pi_ripple_sample()
    for contract in contracts():
        output = contract.operator(sample)
        residual = contract.residual(sample, output) if contract.residual else None
        assert residual is not None and residual.passed, str(contract.complex_id)
        if contract.closure_predicate is not None:
            assert contract.closure_predicate(output, residual), str(contract.complex_id)


def test_ripple_sources_are_individually_necessary():
    sample = elastic_pi_ripple_sample()
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
        lambda sample: replace(sample, flowpoint_parity=np.full(sample.flowpoint_parity.shape, 0.5, dtype=float)),
        lambda sample: replace(sample, memory_kernel=-np.ones_like(sample.memory_kernel)),
        lambda sample: replace(sample, frequency=np.zeros_like(sample.frequency)),
        lambda sample: replace(sample, stochastic_spectrum=np.zeros_like(sample.stochastic_spectrum)),
        lambda sample: replace(sample, environment=-np.ones_like(sample.environment)),
        lambda sample: replace(sample, base_velocity=0.0),
        lambda sample: replace(sample, transport_matrix=np.eye(sample.coordinate.size - 1)),
        lambda sample: replace(sample, waveform=np.full_like(sample.waveform, np.nan)),
    ),
)
def test_ripple_domain_boundaries_fail_closed(mutator):
    with pytest.raises(TNEContractError):
        contracts()[0].operator(mutator(elastic_pi_ripple_sample()))


def test_noninvertible_transport_is_reported_as_degeneracy_not_hidden():
    sample = elastic_pi_ripple_sample()
    singular = np.eye(sample.coordinate.size)
    singular[-1] = singular[-2]
    degenerate = replace(sample, transport_matrix=singular, detected=singular @ sample.source)
    output = contracts()[5].operator(degenerate)
    assert output.status == "degenerate"
    assert output.obstruction <= sample.tolerance


def test_ripple_spatial_closure_is_boundary_closed_and_coercive():
    sample = elastic_pi_ripple_sample()
    output = contracts()[-1].operator(sample)
    assert output.boundary_residual <= sample.tolerance
    assert output.reconstruction_residual <= sample.tolerance
    assert output.coercivity > 0.0
    assert output.status == "closed"
