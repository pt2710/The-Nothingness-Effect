from __future__ import annotations

import pytest

from equations.duality.duality import FiniteInvolution, reciprocal_orbit_double_cover
from tne_runtime.theorem_complex_runtime.types import DomainViolationError


def test_double_cover_does_not_hide_fixed_point_obstruction():
    involution = FiniteInvolution((1.0, 2.0, 3.0), (1, 0, 2))
    with pytest.raises(DomainViolationError, match="free involution"):
        reciprocal_orbit_double_cover(involution)


def test_out_of_domain_action_index_fails():
    involution = FiniteInvolution((1.0, -1.0), (1, 0))
    with pytest.raises(DomainViolationError):
        involution.apply_index(2)
