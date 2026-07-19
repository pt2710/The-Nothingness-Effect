from __future__ import annotations

import numpy as np
import torch

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.exact_product_carrier import ExactProductInput
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.artificial_intelligence.qenn.authoritative_closure_contracts import B_IDS, B_SOURCE_PAIRS, C_IDS, contracts
from the_nothingness_effect.artificial_intelligence.qenn.contracts import QENNContractInput


def _value() -> QENNContractInput:
    axis = torch.linspace(0.0, 2.0 * torch.pi, 12)
    signal = torch.stack((torch.sin(axis), torch.cos(axis), torch.sin(2.0 * axis), torch.cos(2.0 * axis), 0.5 * torch.sin(axis), 0.5 * torch.cos(axis)), dim=-1)
    return QENNContractInput(signal, tolerance=1e-6)


def _catalog():
    return {str(item.complex_id): item for item in contracts()}


def test_declared_product_defect_stays_open():
    first, second = B_SOURCE_PAIRS[0]
    value = ExactProductInput(
        first_states={first: np.array([1.0]), second: np.array([2.0])},
        second_states={first: np.array([3.0]), second: np.array([4.0])},
        first_residuals={first: 0.0, second: 1e-3},
        second_residuals={first: 0.0, second: 0.0},
        tolerance=1e-6,
    )
    evaluation = evaluate_contract(_catalog()[B_IDS[0]], value)
    assert evaluation.status is ClosureStatus.OPEN
    assert evaluation.output.first_product_residual == 1e-3
    assert evaluation.residual is not None and not evaluation.residual.passed


def test_all_qenn_product_sources_are_necessary():
    catalog = _catalog()
    for identifier in (*B_IDS, *C_IDS):
        contract = catalog[identifier]
        removals = tuple(check(_value()) for check in contract.source_removal_checks)
        assert len(removals) == len(contract.source_ids)
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)
