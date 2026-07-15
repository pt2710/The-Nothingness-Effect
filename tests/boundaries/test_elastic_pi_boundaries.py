"""Exact, approximate, and singular boundaries of the Elastic-pi law."""

from __future__ import annotations

import numpy as np
import pytest

from equations.elastic_pi.elastic_pi import (
    ElasticPi,
    ElasticPiEvaluationError,
    ElasticPiStatus,
    evaluate_elastic_pi,
    require_elastic_pi_value,
)
from equations.theorem_complex_runtime.types import DomainViolationError


def test_exact_source_law_and_log_identity():
    entropy = np.array([-2.0, 0.0, 3.0])
    result = evaluate_elastic_pi(entropy, K_D=2.0)

    assert result.status is ElasticPiStatus.EXACTLY_EVALUATED
    assert np.allclose(result.value, np.pi * np.exp(-entropy / 2.0))
    assert np.allclose(result.analytic_log_value, np.log(np.pi) - entropy / 2.0)
    assert result.approximation_metadata["clipped"] is False


def test_underflow_is_an_explicit_status_not_a_neutral_positive_value():
    result = evaluate_elastic_pi(np.array([1000.0]), K_D=1.0)

    assert result.status is ElasticPiStatus.UNDERFLOW
    assert result.value is None
    assert result.approximation_metadata["exact_value_available"] is False
    with pytest.raises(ElasticPiEvaluationError):
        require_elastic_pi_value(result)


def test_clipped_evaluation_preserves_approximation_metadata():
    result = ElasticPi().compute_piE_and_laplacian(
        np.array([-1000.0, 1000.0]), exponent_clip=500.0, return_diagnostics=True
    )

    assert result.status is ElasticPiStatus.APPROXIMATED
    assert result.value is not None
    assert result.approximation_metadata["clipped_count"] == 2
    assert not np.array_equal(result.exact_exponent, result.evaluated_exponent)


def test_clipped_tuple_api_is_forbidden_because_it_would_drop_diagnostics():
    with pytest.raises(DomainViolationError):
        ElasticPi().compute_piE_and_laplacian(np.array([1.0]), exponent_clip=100.0)


@pytest.mark.parametrize("scale", [0.0, -1.0, np.inf, np.nan])
def test_elasticity_scale_must_be_strictly_positive(scale):
    with pytest.raises(DomainViolationError):
        evaluate_elastic_pi(np.array([0.0]), K_D=scale)


def test_nonuniform_coordinates_are_not_silently_treated_as_uniform():
    with pytest.raises(DomainViolationError):
        evaluate_elastic_pi(np.array([0.0, 1.0, 2.0]), K_D=1.0, x=[0.0, 1.0, 3.0])
