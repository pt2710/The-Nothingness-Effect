from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.soinets.evaluation import (
    evaluate_classification,
)
from the_nothingness_effect.artificial_intelligence.soinets.model import SOInetModel
from the_nothingness_effect.artificial_intelligence.soinets.training import (
    fit_classification,
)


def _dataset(seed: int = 211):
    generator = torch.Generator().manual_seed(seed)
    qenn = torch.rand((4, 6, 4), generator=generator) + 0.2
    pgqenn = 1.15 * qenn + 0.02 * torch.rand(qenn.shape, generator=generator)
    targets = torch.tensor([0, 1, 2, 1])
    return qenn, pgqenn, targets


def test_soinet_task_metrics_are_causally_architecture_coupled():
    torch.manual_seed(211)
    model = SOInetModel(4, 6, 3, qenn_count=1, pgqenn_count=1)
    qenn, pgqenn, targets = _dataset()
    baseline = evaluate_classification(model, qenn, pgqenn, targets)

    with torch.no_grad():
        model.meta_readout.weight.add_(0.4)
    perturbed = evaluate_classification(model, qenn, pgqenn, targets)

    assert baseline.logits.shape == (4, 3)
    assert baseline.probabilities.shape == (4, 3)
    assert not torch.allclose(baseline.logits, perturbed.logits)
    assert 0.0 <= float(baseline.accuracy) <= 1.0
    assert torch.isfinite(baseline.loss)


def test_soinet_fit_records_train_and_validation_metrics_from_same_model():
    torch.manual_seed(223)
    model = SOInetModel(4, 6, 3, qenn_count=1, pgqenn_count=1)
    qenn, pgqenn, targets = _dataset(223)
    before = model.meta_readout.weight.detach().clone()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    history = fit_classification(
        model,
        optimizer,
        (qenn, pgqenn, targets),
        (qenn, pgqenn, targets),
        epochs=1,
    )

    assert len(history) == 1
    assert history[0].epoch == 1
    assert history[0].train_loss >= 0.0
    assert history[0].validation_loss >= 0.0
    assert not torch.allclose(before, model.meta_readout.weight)
