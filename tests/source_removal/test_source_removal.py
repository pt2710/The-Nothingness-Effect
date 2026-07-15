from __future__ import annotations

import numpy as np

from tne_runtime.theorem_complex_runtime import ComplexId
from tne_runtime.theorem_complex_runtime.invariants import (
    additive_derivation,
    source_removal_result,
)


def test_each_additive_source_is_necessary():
    a = np.array([1.0, 2.0])
    b = np.array([0.5, 3.0])
    complete = additive_derivation(a, b)
    remove_a = additive_derivation(np.zeros_like(a), b)
    remove_b = additive_derivation(a, np.zeros_like(b))
    result_a = source_removal_result(ComplexId("source_a"), complete, remove_a, tolerance=1e-8)
    result_b = source_removal_result(ComplexId("source_b"), complete, remove_b, tolerance=1e-8)
    assert result_a.necessary is True
    assert result_b.necessary is True
