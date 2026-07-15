"""Typed boundary failures for completeness laws."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from equations.completeness_theorem.contracts import source_operator
from tests.contracts.test_completeness_contracts import INPUT
from tne_runtime.theorem_complex_runtime.types import DomainViolationError, NonFiniteValueError


def test_nonbinary_theorem_prefix_is_rejected():
    with pytest.raises(DomainViolationError, match="binary"):
        source_operator(1, replace(INPUT, theorem_bits=(1, 0, 2, 1, 0, 1)))


def test_misaligned_operator_shape_is_rejected():
    with pytest.raises(DomainViolationError):
        source_operator(3, replace(INPUT, closure_operator=np.eye(5)))


def test_nonfinite_state_is_not_coerced():
    state = INPUT.state.copy()
    state[2] = np.nan
    with pytest.raises(NonFiniteValueError):
        source_operator(5, replace(INPUT, state=state))


def test_empty_formal_system_is_rejected():
    empty = INPUT.formal_system.clone()
    empty.nodes.clear()
    with pytest.raises(DomainViolationError, match="cannot be empty"):
        source_operator(0, replace(INPUT, formal_system=empty))
