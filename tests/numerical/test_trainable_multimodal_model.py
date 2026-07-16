from __future__ import annotations

import torch

from the_nothingness_effect.artificial_intelligence.multimodal import (
    DynamicKDSearch,
    TNETrainableMultimodalModel,
    evaluate_multimodal_model,
    make_synthetic_multimodal_dataset,
    train_multimodal_model,
)
from the_nothingness_effect.artificial_intelligence.shared.dynamic_kd import (
    dynamic_kd_state,
    set_dynamic_kd,
)


def test_visible_multimodal_model_has_per_sample_predictions_and_gradients():
    torch.manual_seed(0)
    dataset = make_synthetic_multimodal_dataset(samples_per_class=5, seed=0)
    model = TNETrainableMultimodalModel(hidden_dim=8)
    output = model(dataset.train.modalities)

    assert output.readout.shape == (dataset.train.labels.numel(), 4)
    assert output.observation.shape == output.readout.shape
    assert output.reconstructed_fused_tokens.shape == (
        dataset.train.labels.numel(),
        6,
    )
    assert output.axis_state.mapped_axes.shape[:2] == (
        dataset.train.labels.numel(),
        3,
    )
    assert output.local_rbm_state.hidden_probability.shape[0] == (
        dataset.train.labels.numel() * 3
    )
    assert output.global_rbm_state.hidden_probability.shape[0] == dataset.train.labels.numel()
    assert output.cluster_state.active_clusters >= 3
    assert torch.allclose(
        output.regulated_modality_weights.sum(dim=-1),
        torch.ones(dataset.train.labels.numel()),
        atol=1e-6,
    )
    assert output.metadata["dependency_chain"] == (
        "DTQC->QENN",
        "QENN+MPL-TC->PGQENN",
        "QENN+PGQENN->SOInet",
    )
    torch.nn.functional.cross_entropy(output.readout, dataset.train.labels).backward()
    assert model.task_head.weight.grad is not None
    assert model.backbone.shared_encoder[0].weight.grad is not None


def test_multimodal_training_validation_and_evaluation_are_finite():
    torch.manual_seed(0)
    dataset = make_synthetic_multimodal_dataset(samples_per_class=5, seed=0)
    model = TNETrainableMultimodalModel(hidden_dim=8)
    run = train_multimodal_model(
        model,
        dataset.train,
        dataset.validation,
        epochs=2,
        seed=0,
        optimize_K_D=True,
        adaptive_learning_rate=True,
    )
    evaluation = evaluate_multimodal_model(model, dataset.test)

    assert len(run.history) == 2
    assert len(run.kd_selections) == 2
    assert len(run.kd_probes) >= 6
    assert all(item.K_D > 0.0 for item in run.history)
    assert all(torch.isfinite(torch.tensor(item.validation_objective)) for item in run.history)
    assert all(torch.isfinite(torch.tensor(item.train_total_loss)) for item in run.history)
    assert 0.0 <= evaluation.metrics["accuracy"] <= 1.0
    assert evaluation.confusion_matrix.sum() == dataset.test.labels.numel()
    assert set(evaluation.reconstruction_rmse) == {"color", "sound", "vision"}


def test_dynamic_kd_updates_every_exact_elastic_source_law_atomically():
    model = TNETrainableMultimodalModel(hidden_dim=8)
    initial = dynamic_kd_state(model)
    assert initial.value == 1.0 and len(initial.buffer_names) >= 8

    updated = set_dynamic_kd(model, 0.625)
    assert updated.value == 0.625
    assert set(updated.buffer_names) == set(initial.buffer_names)

    dataset = make_synthetic_multimodal_dataset(samples_per_class=5, seed=4)
    selection = DynamicKDSearch(scale_factors=(0.8, 1.0, 1.25)).select(
        model, dataset.validation, epoch=0
    )
    assert selection.selected_K_D > 0.0
    assert selection.selected_objective <= selection.previous_objective + 1e-12
    assert dynamic_kd_state(model).value == selection.selected_K_D
