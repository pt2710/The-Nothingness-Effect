from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    additive_derivation,
    anti_invariant_projector,
    invariant_projector,
    involution_residual,
    non_cancellation_energy,
)


def test_involution_and_projectors_split_the_source():
    source = np.array([1.0, -2.0, 3.0])
    involution = lambda value: -np.asarray(value)
    plus = invariant_projector(involution, source)
    minus = anti_invariant_projector(involution, source)
    assert involution_residual(involution, source) == 0.0
    assert np.allclose(plus + minus, source)
    assert np.allclose(plus, 0.0)


def test_additive_derivation_uses_both_sources_nontrivially():
    a = np.array([1.0, 2.0])
    b = np.array([3.0, 4.0])
    combined = additive_derivation(a, b, coupling=0.5)
    assert not np.allclose(combined, a)
    assert not np.allclose(combined, b)
    assert non_cancellation_energy(a, b, combined) > 0.0
