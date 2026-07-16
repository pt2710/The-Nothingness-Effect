"""Hardening checks for Spectrum source-removal certificate recomputation."""

from __future__ import annotations

from the_nothingness_effect._runtime.theorem_complex_runtime.source_samples import (
    sample_inputs,
)
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.hardened_contracts import (
    contracts,
)


def test_hardened_ablation_recomputes_nonzero_surviving_certificates():
    samples = sample_inputs()
    for contract in contracts()[10:]:
        value = samples[str(contract.complex_id)]
        removals = tuple(check(value) for check in contract.source_removal_checks)
        assert len(removals) == len(contract.source_ids)
        assert {item.source_id for item in removals} == set(contract.source_ids)
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)
        assert all(item.removed_response > 0.0 for item in removals)
        assert all(item.removed_response < item.baseline_response for item in removals)
