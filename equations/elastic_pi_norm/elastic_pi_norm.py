"""Canonical weighted path law from the Elastic-pi appendix handoff."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from equations.elastic_pi.elastic_pi import evaluate_elastic_pi, require_elastic_pi_value
from equations.theorem_complex_runtime.types import DomainViolationError
from equations.theorem_complex_runtime.validation import ensure_finite


@dataclass(frozen=True)
class ElasticPiNormResult:
    trajectory: np.ndarray
    entropy: np.ndarray
    K_D: float
    p: float
    elastic_field: np.ndarray
    transition_weights: np.ndarray
    metric_increments: np.ndarray
    weighted_terms: np.ndarray
    value: float
    norm_status: str


def elastic_pi_weighted_path(
    trajectory,
    entropy,
    *,
    K_D: float,
    p: float = 2.0,
    anchored: bool = True,
) -> ElasticPiNormResult:
    r"""Evaluate (sum d(x_n,x_n-1)^p exp(-(S_n-S_n-1)/K_D))^(1/p)."""

    states = np.asarray(trajectory, dtype=float)
    entropy_values = np.asarray(entropy, dtype=float)
    if states.ndim != 1 or states.size < 2:
        raise DomainViolationError("Elastic-pi norm requires a one-dimensional trajectory with at least two states")
    if entropy_values.shape != states.shape:
        raise DomainViolationError("Elastic-pi norm entropy must share the trajectory shape")
    ensure_finite((states, entropy_values), name="Elastic-pi norm source")
    exponent = float(p)
    if not np.isfinite(exponent) or exponent < 1.0:
        raise DomainViolationError("Elastic-pi norm requires p >= 1")
    if anchored and not np.isclose(states[0], 0.0):
        raise DomainViolationError("the anchored norm domain requires x_0 = 0")
    evaluation = evaluate_elastic_pi(entropy_values, K_D=K_D)
    field = require_elastic_pi_value(evaluation)
    weights = field[1:] / field[:-1]
    if np.any(weights <= 0.0):
        raise DomainViolationError("Elastic-pi transition weights must be positive")
    increments = np.abs(np.diff(states))
    terms = increments**exponent * weights
    value = float(np.sum(terms) ** (1.0 / exponent))
    ensure_finite(value, name="Elastic-pi weighted path")
    return ElasticPiNormResult(
        states,
        entropy_values,
        float(K_D),
        exponent,
        field,
        weights,
        increments,
        terms,
        value,
        "norm_on_anchored_domain" if anchored else "seminorm_on_unrestricted_sequences",
    )
