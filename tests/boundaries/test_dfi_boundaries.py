"""Failure and singularity boundaries for canonical and legacy DFI paths."""

from __future__ import annotations

import numpy as np
import pytest

from equations.dynamic_fluctuation_index.dfi import (
    DFIStatus,
    DFISingularityError,
    DynamicFluctuationIndex,
    NormalizedDFIResult,
    normalized_dfi,
    require_finite_dfi,
)
from equations.theorem_complex_runtime.types import DomainViolationError, NonFiniteValueError


SINGULAR = np.array([[1.0, 0.0], [2.0, 0.0]])


def test_zero_remainder_returns_an_explicit_obstruction_without_neutral_values():
    result = normalized_dfi(SINGULAR, spectrum_scale=5.0)

    assert result.status is DFIStatus.SINGULAR
    assert result.normalized_entropy is None
    assert result.entropic_weight is None
    assert result.relative_volume is None
    assert result.divergence_witness.coordinates
    assert result.approximation_metadata["masked_nonfinite_values"] == 0
    with pytest.raises(DFISingularityError):
        require_finite_dfi(result)


def test_canonical_facade_does_not_relabel_a_singularity_as_finite():
    result = DynamicFluctuationIndex().dfi(SINGULAR, soi=5.0)

    assert isinstance(result, NormalizedDFIResult)
    assert result.status is DFIStatus.SINGULAR


def test_legacy_neutral_coercion_requires_explicit_compatibility_mode():
    result = DynamicFluctuationIndex(compatibility_mode=True).dfi(SINGULAR, soi=5.0)

    assert all(metrics["Compatibility_Mode"] is True for metrics in result.values())
    assert all(np.all(np.isfinite(metrics["Entropic_Weight"])) for metrics in result.values())


@pytest.mark.parametrize("scale", [0.0, -1.0, np.inf, np.nan])
def test_invalid_spectrum_scale_is_rejected(scale):
    with pytest.raises(DomainViolationError):
        normalized_dfi(np.ones((3, 2)), spectrum_scale=scale)


def test_nonfinite_source_data_is_rejected_before_evaluation():
    with pytest.raises(NonFiniteValueError):
        normalized_dfi(np.array([[1.0, np.nan], [2.0, 3.0]]), spectrum_scale=1.0)
