from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import (
    elastic_dubler_sample,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.parity_elastic_spectral_contract import (
    ParityElasticSpectralInput,
    contract,
    parity_elastic_spectral_operator,
)


def test_parity_elastic_coefficient_form_and_operator_close_exactly():
    theorem = contract()
    evaluation = evaluate_contract(theorem, elastic_dubler_sample())

    assert theorem.exact_semantics is True
    assert evaluation.status is ClosureStatus.CLOSED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.closure_status == "closed"
    assert evaluation.output.coefficient_residual == pytest.approx(0.0)
    assert evaluation.output.form_identity_residual == pytest.approx(0.0)
    assert evaluation.output.operator_identity_residual == pytest.approx(0.0)
    assert evaluation.output.parity_restoration_residual == pytest.approx(0.0)
    assert evaluation.output.infinite_elasticity_residual == pytest.approx(0.0)
    assert evaluation.output.source_sampling_residual == pytest.approx(0.0)


def test_perturbed_spectral_coefficient_is_localized_and_open():
    legacy = elastic_dubler_sample()
    exact = parity_elastic_spectral_operator(legacy)
    corrupted = exact.coefficient.copy()
    corrupted[corrupted.size // 2] *= 1.1
    value = ParityElasticSpectralInput(
        coordinates=exact.spatial_domain,
        parity_source=exact.parity_source,
        trial_field=exact.trial_field,
        baseline_elasticity=exact.baseline_coefficient,
        beta=1.0,
        elasticity=legacy.elasticity,
        coefficient=corrupted,
        form_defect_density=exact.form_defect_density,
        operator_defect=exact.local_operator,
        tolerance=1e-10,
    )
    evaluation = evaluate_contract(contract(), value)

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.coefficient_residual > 0.0
    assert evaluation.output.form_identity_residual == pytest.approx(0.0)
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_zero_parity_source_restores_baseline_operator():
    legacy = elastic_dubler_sample()
    value = ParityElasticSpectralInput(
        coordinates=legacy.coordinates,
        parity_source=np.zeros_like(legacy.pdfi),
        trial_field=legacy.pdfi,
        baseline_elasticity=legacy.domain_elasticity,
        beta=1.0,
        elasticity=legacy.elasticity,
        potential=np.zeros_like(legacy.pdfi),
        tolerance=1e-10,
    )
    output = parity_elastic_spectral_operator(value)

    np.testing.assert_allclose(output.coefficient, output.baseline_coefficient)
    np.testing.assert_allclose(output.form_defect_density, 0.0)
    np.testing.assert_allclose(output.local_operator, 0.0, atol=1e-12)
    assert output.closure_status == "closed"


def test_both_spectral_b_sources_are_necessary():
    theorem = contract()
    removals = tuple(
        check(elastic_dubler_sample()) for check in theorem.source_removal_checks
    )

    assert len(removals) == 2
    assert all(item.necessary for item in removals)
    assert all(item.necessity_residual > 0.0 for item in removals)
