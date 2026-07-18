from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.normalized_closure_contracts import (
    ExactSpatialDFIInput,
    SOURCE_IDS as DFI_SOURCES,
    contracts as dfi_contracts,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.normalized_closure_contracts import (
    ExactSpatialParityInput,
    SOURCE_IDS as PDFI_SOURCES,
    contracts as pdfi_contracts,
)


def _contract(contracts, identifier):
    return {str(item.complex_id): item for item in contracts()}[identifier]


def test_dfi_potential_uses_e_over_one_plus_e():
    fields = {source: np.zeros(4) for source in DFI_SOURCES}
    fields[DFI_SOURCES[1]] = np.array([3.0, 0.0, 3.0, 0.0])
    weights = {source: 1.0 for source in DFI_SOURCES}
    value = ExactSpatialDFIInput(
        fields,
        {source: np.zeros(4) for source in DFI_SOURCES},
        weights,
        dict(weights),
        (3, 2, 1, 0),
        tolerance=1e-12,
    )
    evaluation = evaluate_contract(
        _contract(dfi_contracts, "spatially_localized_dfi_consistency_closure"),
        value,
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.defect_potential_1b[0] == pytest.approx(3.0 / 4.0)
    assert evaluation.output.volume_energy_1b == pytest.approx(6.0)


def test_pdfi_potential_uses_e_over_one_plus_e():
    fields = {source: np.zeros(4) for source in PDFI_SOURCES}
    fields[PDFI_SOURCES[2]] = np.array([1.0, 0.0, 1.0, 0.0])
    weights = {source: 2.0 for source in PDFI_SOURCES}
    value = ExactSpatialParityInput(
        fields,
        {source: np.zeros(4) for source in PDFI_SOURCES},
        weights,
        dict(weights),
        (3, 2, 1, 0),
        tolerance=1e-12,
    )
    evaluation = evaluate_contract(
        _contract(pdfi_contracts, "spatial_parity_elastic_calibration_closure"),
        value,
    )

    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.defect_potential_1b[0] == pytest.approx(1.0)
    assert evaluation.output.volume_energy_1b == pytest.approx(4.0)
