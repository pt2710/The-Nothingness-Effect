from __future__ import annotations

import torch

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime.types import ClosureStatus
from the_nothingness_effect.artificial_intelligence.qenn.authoritative_closure_contracts import A_IDS, B_IDS, B_SOURCE_PAIRS, C_IDS, C_SOURCE_PAIRS, contracts
from the_nothingness_effect.artificial_intelligence.qenn.contracts import QENNContractInput


def _value() -> QENNContractInput:
    axis = torch.linspace(0.0, 2.0 * torch.pi, 12)
    signal = torch.stack((torch.sin(axis), torch.cos(axis), torch.sin(2.0 * axis), torch.cos(2.0 * axis), 0.5 * torch.sin(axis), 0.5 * torch.cos(axis)), dim=-1)
    return QENNContractInput(signal, tolerance=1e-6)


def _catalog():
    return {str(item.complex_id): item for item in contracts()}


def test_qenn_dual_classifications_are_total_and_exclusive():
    evaluations = [evaluate_contract(_catalog()[identifier], _value()) for identifier in A_IDS]
    assert len(evaluations) == 12
    assert all(item.status is ClosureStatus.SATISFIED for item in evaluations)
    assert all(item.output.positive_branch != item.output.failure_dual_branch for item in evaluations)
    assert any(item.output.failure_dual_branch for item in evaluations)


def test_qenn_products_recover_every_coordinate_exactly():
    catalog = _catalog()
    for identifier, sources in zip(B_IDS, B_SOURCE_PAIRS):
        evaluation = evaluate_contract(catalog[identifier], _value())
        assert evaluation.status is ClosureStatus.SATISFIED
        assert evaluation.output.source_ids == sources
        assert evaluation.output.exchange_square_residual == 0.0
    for identifier, sources in zip(C_IDS, C_SOURCE_PAIRS):
        evaluation = evaluate_contract(catalog[identifier], _value())
        assert evaluation.status is ClosureStatus.CLOSED
        assert evaluation.output.source_ids == sources
        assert evaluation.output.first_product_residual == 0.0
        assert evaluation.output.second_product_residual == 0.0
        assert evaluation.output.exchange_square_residual == 0.0


def test_qenn_authoritative_catalog_is_complete_and_unique():
    identifiers = [str(item.complex_id) for item in contracts()]
    assert len(identifiers) == 21
    assert len(set(identifiers)) == 21
    assert set(identifiers) == {*A_IDS, *B_IDS, *C_IDS}
