"""Domain and norm-status boundaries for the Elastic-pi weighted path."""

from __future__ import annotations

import numpy as np
import pytest

from equations.elastic_pi_norm.elastic_pi_norm import elastic_pi_weighted_path
from tne_runtime.theorem_complex_runtime.types import DomainViolationError


def test_preserved_weighted_path_formula():
    trajectory = np.array([0.0, 2.0, 5.0])
    entropy = np.array([0.0, 1.0, 3.0])
    result = elastic_pi_weighted_path(trajectory, entropy, K_D=2.0, p=2.0, anchored=True)
    expected_weights = np.exp(-np.diff(entropy) / 2.0)
    expected = np.sqrt(np.sum(np.diff(trajectory) ** 2 * expected_weights))

    assert np.allclose(result.transition_weights, expected_weights)
    assert np.isclose(result.value, expected)
    assert result.norm_status == "norm_on_anchored_domain"


def test_unrestricted_difference_functional_reports_seminorm_status():
    result = elastic_pi_weighted_path([2.0, 2.0, 2.0], [0.0, 0.0, 0.0], K_D=1.0, anchored=False)

    assert result.value == 0.0
    assert result.norm_status == "seminorm_on_unrestricted_sequences"


def test_anchored_domain_rejects_nonzero_initial_state():
    with pytest.raises(DomainViolationError, match="x_0 = 0"):
        elastic_pi_weighted_path([1.0, 2.0], [0.0, 1.0], K_D=1.0, anchored=True)


@pytest.mark.parametrize("p", [0.0, 0.5, np.inf, np.nan])
def test_p_must_define_a_norm_exponent(p):
    with pytest.raises(DomainViolationError):
        elastic_pi_weighted_path([0.0, 1.0], [0.0, 1.0], K_D=1.0, p=p)
