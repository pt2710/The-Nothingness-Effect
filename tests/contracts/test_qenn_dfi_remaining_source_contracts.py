"""Executable source-law gates for QENN 05--12 and DFI 05--07."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from the_nothingness_effect.artificial_intelligence.qenn.contracts import (
    QENNContractInput,
)
from the_nothingness_effect.artificial_intelligence.qenn.source_contracts import (
    SOURCE_IDS as QENN_SOURCE_IDS,
    contracts as qenn_source_contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.source_contracts import (
    DFICertificationInput,
    SOURCE_IDS as DFI_SOURCE_IDS,
    contracts as dfi_source_contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)


def _qenn_input() -> QENNContractInput:
    axis = torch.linspace(0.0, 2.0 * torch.pi, 12)
    signal = torch.stack(
        (
            torch.sin(axis),
            torch.cos(axis),
            torch.sin(2.0 * axis),
            torch.cos(2.0 * axis),
            0.5 * torch.sin(axis),
            0.5 * torch.cos(axis),
        ),
        dim=-1,
    )
    return QENNContractInput(signal, tolerance=1e-6)


def _dfi_data() -> np.ndarray:
    return np.asarray(
        (
            (1.0, 2.0, 4.0),
            (2.0, 3.0, 5.0),
            (3.0, 5.0, 8.0),
        ),
        dtype=float,
    )


def test_qenn_native_registry_is_complete_twelve_a_sources():
    identifiers = {str(contract.complex_id) for contract in all_contracts()}

    assert len(QENN_SOURCE_IDS) == 8
    assert set(map(str, QENN_SOURCE_IDS)).issubset(identifiers)
    assert len(qenn_source_contracts()) == 8


def test_qenn_remaining_source_laws_return_finite_typed_diagnostics():
    value = _qenn_input()

    for contract in qenn_source_contracts():
        evaluation = contract.evaluate(value)
        output = evaluation.output

        assert output.response.shape == value.signal.shape
        assert output.residual_field.shape == value.signal.shape
        assert torch.isfinite(output.response).all()
        assert torch.isfinite(output.residual_field).all()
        assert np.isfinite(output.invariant_residual)
        assert evaluation.residual is not None


def test_qenn_failure_duals_are_activated_by_targeted_perturbations():
    base = _qenn_input()
    parity_contract = qenn_source_contracts()[1]
    drift_contract = qenn_source_contracts()[3]
    epoch_contract = qenn_source_contracts()[5]

    parity_signal = base.signal.clone()
    parity_signal[:, 1] += torch.linspace(0.0, 3.0, parity_signal.shape[0])
    parity = parity_contract.evaluate(QENNContractInput(parity_signal))

    drift_signal = base.signal.clone()
    drift_signal[-1] += 20.0
    drift = drift_contract.evaluate(QENNContractInput(drift_signal))

    expanding = torch.stack(
        [torch.arange(1.0, 7.0) * (1.7**step) for step in range(8)]
    )
    epoch = epoch_contract.evaluate(QENNContractInput(expanding))

    assert parity.output.invariant_residual > 0.0
    assert drift.output.invariant_residual > 0.0
    assert epoch.output.invariant_residual > 0.0


def test_dfi_native_registry_includes_three_certification_sources():
    identifiers = {str(contract.complex_id) for contract in all_contracts()}

    assert len(DFI_SOURCE_IDS) == 3
    assert set(map(str, DFI_SOURCE_IDS)).issubset(identifiers)
    assert len(dfi_source_contracts()) == 3


def test_dfi_fixed_map_flowpoint_and_simulation_identity_close_componentwise():
    value = DFICertificationInput(_dfi_data(), spectrum_scale=1.0)

    for contract in dfi_source_contracts():
        evaluation = contract.evaluate(value)

        assert evaluation.output.invariant_residual == pytest.approx(0.0)
        assert evaluation.output.total_residual == pytest.approx(0.0)
        assert np.allclose(evaluation.output.component_residual, 0.0)
        assert evaluation.residual is not None and evaluation.residual.passed


def test_dfi_component_mismatch_cannot_be_hidden_by_equal_totals():
    data = _dfi_data()
    baseline = dfi_source_contracts()[1].evaluate(
        DFICertificationInput(data, spectrum_scale=1.0)
    ).output.components
    swapped = baseline.copy()
    swapped[:, [0, 1]] = swapped[:, [1, 0]]

    evaluation = dfi_source_contracts()[1].evaluate(
        DFICertificationInput(
            data,
            spectrum_scale=1.0,
            flowpoint_components=swapped,
        )
    )

    assert evaluation.output.total_residual == pytest.approx(0.0)
    assert evaluation.output.invariant_residual > 0.0
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_dfi_certification_rejects_shape_changing_interfaces():
    with pytest.raises(DomainViolationError):
        dfi_source_contracts()[2].evaluate(
            DFICertificationInput(
                _dfi_data(),
                spectrum_scale=1.0,
                simulated_components=np.ones((2, 2)),
            )
        )
