"""Argument-correct typed checks for the central repository facade."""

from __future__ import annotations

import numpy as np

from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import NormalizedDFIResult
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import ElasticPiEvaluation
from fields_of_physics_in_dev.the_nothingness_effect import NothingnessEffect


def test_facade_passes_required_arguments_to_foundational_functions():
    facade = NothingnessEffect()

    orbit = facade.fp(3)
    assert [next(orbit), next(orbit)] == [3, -3]
    assert facade.sym_eq(2) is not None
    assert facade.dual_eq(2) is not None
    assert facade.spa_eq(2) is not None
    assert facade.countable_infinity(1, 2, 3) is not None
    assert facade.uncountable_infinity(1, 2, 3) is not None


def test_facade_returns_typed_dfi_and_elastic_pi_results():
    facade = NothingnessEffect()
    data = np.array([[1.0, 2.0, 4.0], [2.0, 3.0, 5.0]])

    assert isinstance(facade.dfi(data, soi=7.0), NormalizedDFIResult)
    assert isinstance(facade.elastic_pi(np.array([0.0, 1.0]), K_D=2.0), ElasticPiEvaluation)


def test_observation_facade_can_return_or_invoke_the_underlying_operator():
    facade = NothingnessEffect()
    operator = facade.obs_n_col()

    assert callable(operator)
    direct = facade.obs_n_col(1, 2, 3)
    reference = operator(1, 2, 3)
    assert len(direct) == len(reference) == 2
    assert all(hasattr(item, "__next__") for item in direct)
