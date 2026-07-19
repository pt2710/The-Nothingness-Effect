"""Regression checks for appendix-declared physical and DTQC products."""

from __future__ import annotations

import numpy as np

from tools.generate_artifact_provenance import _sample_inputs
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    active_contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import (
    ExactProductInput,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    ComplexLevel,
)


TARGETS = {
    "temporal_directed_elastic_transport",
    "observable_conserved_directed_transport_closure",
    "spatially_calibrated_quantum_information_closure",
    "screened_rotation_halo_geometry",
    "information_preserving_cosmic_network_closure",
    "spatiotemporal_hawking_flux_density",
    "certified_residual_memory_lower_bound",
    "observable_hawking_memory_certification",
    "memory_shock_environmental_reconstruction",
    "horizon_localized_observable_memory_closure",
    "elastic_parseval_quasicrystal_isometry",
    "parity_meyer_noise_stable_diffraction_closure",
    "certified_multiscale_dtqc_reconstruction_closure",
}


def _explicit_product_input(contract, *, residual: float = 0.0) -> ExactProductInput:
    identifiers = tuple(str(item) for item in contract.source_ids)
    return ExactProductInput(
        first_states={
            identifier: np.asarray((index + 1.0, index + 2.0))
            for index, identifier in enumerate(identifiers)
        },
        second_states={
            identifier: np.asarray((index + 3.0, index + 4.0))
            for index, identifier in enumerate(identifiers)
        },
        first_residuals={identifier: residual for identifier in identifiers},
        second_residuals={identifier: residual for identifier in identifiers},
        tolerance=1e-8,
    )


def test_declared_physical_products_close_with_genuine_source_recomputation():
    catalog = {str(contract.complex_id): contract for contract in active_contracts()}
    samples = _sample_inputs()

    assert TARGETS <= set(catalog)
    for identifier in sorted(TARGETS):
        contract = catalog[identifier]
        value = samples.get(identifier, _explicit_product_input(contract))
        evaluation = evaluate_contract(contract, value)
        expected = (
            ClosureStatus.SATISFIED
            if contract.level is ComplexLevel.B
            else ClosureStatus.CLOSED
        )

        assert contract.exact_semantics is True
        assert evaluation.status is expected
        assert len(contract.source_removal_checks) == len(contract.source_ids)
        assert all(check(value).necessary for check in contract.source_removal_checks)


def test_declared_product_closure_fails_when_a_source_residual_is_nonzero():
    contract = {
        str(item.complex_id): item for item in active_contracts()
    }["certified_multiscale_dtqc_reconstruction_closure"]
    evaluation = evaluate_contract(
        contract,
        _explicit_product_input(contract, residual=1e-3),
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.residual is not None
    assert evaluation.residual.passed is False
