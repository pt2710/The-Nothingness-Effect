"""Bijection guard between authority promotions and typed provenance samples."""

from __future__ import annotations

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    implementation_status_overrides,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.source_samples import (
    sample_inputs,
)


def test_promoted_source_samples_are_bijective_with_authority_overrides():
    overrides = implementation_status_overrides()
    samples = sample_inputs()
    assert len(overrides) == 156
    assert len(samples) == 156
    assert set(samples) == set(overrides)
