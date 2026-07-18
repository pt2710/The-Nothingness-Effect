from __future__ import annotations

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ClosureStatus,
    DomainViolationError,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts import (
    ApplicabilityInput,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.recertified_contracts import (
    ContextualApplicabilityInput,
    contracts,
)


def _data() -> np.ndarray:
    return np.array(
        [
            [1.0, 2.0, 4.0],
            [2.0, 3.0, 5.0],
            [3.0, 5.0, 8.0],
            [5.0, 8.0, 13.0],
        ]
    )


def _a04():
    return {
        str(item.complex_id): item for item in contracts()
    }["dfi_adaptive_applicability_and_contextual_instability"]


def test_a04_closes_for_an_admissible_identity_scalarization():
    value = ContextualApplicabilityInput(
        data=_data(),
        comparison_data=_data().copy(),
        spectrum_scale=7.0,
        threshold=1e-12,
    )
    evaluation = evaluate_contract(_a04(), value)

    assert evaluation.status is ClosureStatus.SATISFIED
    assert evaluation.residual is not None and evaluation.residual.passed
    assert evaluation.output.classification == "applicable"
    assert evaluation.output.applicability_defect == pytest.approx(0.0)
    np.testing.assert_allclose(evaluation.output.contextual_defect, 0.0)


def test_a04_satisfies_the_dual_classification_for_contextual_instability():
    comparison = _data().copy()
    comparison[:, 0] *= 1.5
    value = ContextualApplicabilityInput(
        data=_data(),
        comparison_data=comparison,
        spectrum_scale=7.0,
        threshold=1e-12,
    )
    evaluation = evaluate_contract(_a04(), value)

    assert evaluation.status is ClosureStatus.SATISFIED
    assert evaluation.output.classification == "contextually_unstable"
    assert np.linalg.norm(evaluation.output.contextual_defect) > value.threshold
    assert evaluation.output.applicability_defect > 0.0
    assert evaluation.output.classification_residual == pytest.approx(0.0)


def test_legacy_applicability_input_remains_compatible():
    evaluation = evaluate_contract(
        _a04(),
        ApplicabilityInput(_data(), 7.0, 1e-12),
    )

    assert evaluation.status is ClosureStatus.SATISFIED
    assert evaluation.output.classification == "applicable"


def test_a04_rejects_a_nonpositive_dynamic_constant():
    value = ContextualApplicabilityInput(
        data=_data(),
        comparison_data=_data(),
        spectrum_scale=7.0,
        dynamic_constant=0.0,
    )

    with pytest.raises(DomainViolationError, match="dynamic_constant"):
        evaluate_contract(_a04(), value)
