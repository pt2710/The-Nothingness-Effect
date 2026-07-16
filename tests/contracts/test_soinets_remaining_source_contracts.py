"""Executable source-law gates for SOInet A05--A18."""

from __future__ import annotations

import numpy as np
import torch

from the_nothingness_effect.artificial_intelligence.soinets.contracts import (
    SOInetContractInput,
)
from the_nothingness_effect.artificial_intelligence.soinets.source_contracts import (
    SOURCE_IDS,
    contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts


def _modalities(*, identical: bool = False) -> torch.Tensor:
    axis = torch.linspace(0.0, 2.0 * torch.pi, 8)
    base = torch.stack(
        (
            1.2 + torch.sin(axis),
            1.2 + torch.cos(axis),
            1.2 + torch.sin(2.0 * axis),
            1.2 + torch.cos(2.0 * axis),
        ),
        dim=-1,
    )
    if identical:
        return torch.stack((base, base, base))
    return torch.stack((base, 1.05 * base, torch.roll(base, shifts=1, dims=0)))


def test_soinet_native_registry_is_complete_eighteen_a_sources():
    identifiers = {str(contract.complex_id) for contract in all_contracts()}

    assert len(SOURCE_IDS) == 14
    assert set(map(str, SOURCE_IDS)).issubset(identifiers)
    assert len(contracts()) == 14


def test_soinet_remaining_source_laws_return_finite_modality_fields():
    value = SOInetContractInput(_modalities(), tolerance=1e-6)

    for contract in contracts():
        evaluation = contract.evaluate(value)
        output = evaluation.output

        assert output.response.shape == value.modalities.shape
        assert output.residual_field.shape == value.modalities.shape
        assert torch.isfinite(output.response).all()
        assert torch.isfinite(output.residual_field).all()
        assert np.isfinite(output.invariant_residual)
        assert evaluation.residual is not None


def test_soinet_exact_composition_identity_is_zero_residual():
    value = SOInetContractInput(_modalities(), tolerance=1e-6)
    compositionality = contracts()[4].evaluate(value)

    assert compositionality.output.invariant_residual <= 1e-6
    assert compositionality.residual is not None
    assert compositionality.residual.passed


def test_soinet_identical_modalities_close_transfer_cloning_and_phase_locking():
    value = SOInetContractInput(_modalities(identical=True), tolerance=1e-5)
    by_id = {str(contract.complex_id): contract for contract in contracts()}

    hierarchy = by_id[
        "hierarchical_soi_stack_transfer_cross_regime_collapse_duality"
    ].evaluate(value)
    generalization = by_id[
        "soi_cross_domain_generalization_and_collapse"
    ].evaluate(value)
    cloning = by_id[
        "soinet_universal_cloning_principle_cloning_failure_duality"
    ].evaluate(value)
    phase = by_id[
        "spectral_phase_locking_and_collapse_in_soinet"
    ].evaluate(value)

    assert hierarchy.output.invariant_residual <= 1e-5
    assert generalization.output.invariant_residual <= 1e-5
    assert cloning.output.invariant_residual <= 1e-5
    assert phase.output.invariant_residual <= 1e-5


def test_soinet_held_out_modality_perturbation_activates_failure_duals():
    baseline = _modalities(identical=True)
    perturbed = baseline.clone()
    perturbed[-1, -2:] += 6.0
    value = SOInetContractInput(perturbed)
    by_id = {str(contract.complex_id): contract for contract in contracts()}

    generalization = by_id[
        "soi_cross_domain_generalization_and_collapse"
    ].evaluate(value)
    cloning = by_id[
        "soinet_universal_cloning_principle_cloning_failure_duality"
    ].evaluate(value)
    brittleness = by_id[
        "soinet_universal_generalization_principle_failure_brittleness_duality"
    ].evaluate(value)

    assert generalization.output.invariant_residual > 0.0
    assert cloning.output.invariant_residual > 0.0
    assert brittleness.output.invariant_residual > 0.0
