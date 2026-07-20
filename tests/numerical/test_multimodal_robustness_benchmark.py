from __future__ import annotations

import csv
import json
import math

import torch

from tools.run_multimodal_robustness_benchmark import corrupt_batch
from the_nothingness_effect.artificial_intelligence.evaluation_pipeline import (
    run_ai_module_training_evaluation,
)
from the_nothingness_effect.artificial_intelligence.multimodal.data import (
    make_synthetic_multimodal_dataset,
)
from the_nothingness_effect.artificial_intelligence.multimodal.evaluation import (
    classification_metrics_from_confusion,
)
from the_nothingness_effect.artificial_intelligence.multimodal.model import (
    TNETrainableMultimodalModel,
)
from the_nothingness_effect.artificial_intelligence.multimodal.training import (
    train_multimodal_model,
)


def test_multimodal_corruptions_preserve_typed_batch_and_are_deterministic():
    batch = make_synthetic_multimodal_dataset(
        samples_per_class=5,
        seed=3,
    ).test
    scenarios = (
        "clean",
        "gaussian_0.05",
        "remove_color",
        "remove_sound",
        "remove_vision",
        "sound_phase_shift",
        "vision_occlusion",
        "color_channel_permutation",
    )
    for scenario in scenarios:
        first = corrupt_batch(
            batch,
            scenario,
            seed=17,
        )
        second = corrupt_batch(
            batch,
            scenario,
            seed=17,
        )
        assert first.labels.shape == batch.labels.shape
        assert set(first.modalities) == set(batch.modalities)
        assert all(
            torch.equal(
                first.modalities[name],
                second.modalities[name],
            )
            for name in first.modalities
        )
        assert all(
            torch.isfinite(value).all()
            for value in first.modalities.values()
        )


def test_leave_one_modality_out_zeroes_only_selected_channel():
    batch = make_synthetic_multimodal_dataset(
        samples_per_class=5,
        seed=4,
    ).test
    removed = corrupt_batch(
        batch,
        "remove_sound",
        seed=0,
    )
    assert torch.count_nonzero(
        removed.modalities["sound"]
    ) == 0
    assert torch.equal(
        removed.modalities["color"],
        batch.modalities["color"],
    )
    assert torch.equal(
        removed.modalities["vision"],
        batch.modalities["vision"],
    )


def test_classification_metrics_are_zero_safe_and_consistent():
    confusion = torch.tensor(
        [[3, 1], [0, 4]],
    )
    metrics = classification_metrics_from_confusion(
        confusion,
    )
    assert metrics["micro_f1"] == 7 / 8
    assert 0.0 <= metrics["macro_precision"] <= 1.0
    assert 0.0 <= metrics["macro_recall"] <= 1.0
    assert 0.0 <= metrics["macro_f1"] <= 1.0
    assert (
        metrics["balanced_accuracy"]
        == metrics["macro_recall"]
    )


def test_training_restores_best_validation_checkpoint():
    dataset = make_synthetic_multimodal_dataset(
        samples_per_class=5,
        seed=7,
    )
    model = TNETrainableMultimodalModel()
    run = train_multimodal_model(
        model,
        dataset.train,
        dataset.validation,
        epochs=2,
        seed=7,
    )
    assert run.restored_best_checkpoint
    assert 0 <= run.best_epoch < 2
    assert math.isfinite(
        run.best_validation_objective
    )


def test_ai_module_pipeline_writes_complete_evidence(tmp_path):
    output = tmp_path / "ai-evaluation"
    report = run_ai_module_training_evaluation(
        output,
        seeds=(0,),
        epochs=1,
        samples_per_class=5,
    )
    expected = {
        "configuration.json",
        "dataset_manifest.json",
        "metrics.json",
        "metrics.csv",
        "aggregate_metrics.csv",
        "module_metrics.csv",
        "module_metric_summary.csv",
        "source_removal.csv",
        "training_history.csv",
        "seed_summary.csv",
        "evaluation_report.md",
    }
    assert expected <= {
        path.name for path in output.iterdir()
    }
    assert (
        output / "checkpoints" / "seed_0_best.pt"
    ).is_file()
    assert (
        output / "trained_model" / "seed_0_model.pt"
    ).is_file()
    assert (
        output
        / "predictions"
        / "seed_0_test_predictions.csv"
    ).is_file()
    assert {
        "learning_curves.png",
        "aggregate_confusion_matrix.png",
        "module_residual_summary.png",
        "module_accuracy_summary.png",
        "generalization_gap.png",
    } <= {
        path.name
        for path in (output / "plots").iterdir()
    }

    metrics = json.loads(
        (output / "metrics.json").read_text()
    )
    assert (
        metrics["training_status"]
        == "completed_all_seeds"
    )
    assert metrics["validation_status"] == (
        "best_checkpoint_restored_all_seeds"
    )
    assert metrics["all_metrics_finite"]
    assert set(metrics["closure_status"]) == {
        "QENN",
        "PGQENN",
        "SOInets",
    }
    assert report == metrics

    with (
        output / "module_metrics.csv"
    ).open(
        newline="",
        encoding="utf-8",
    ) as handle:
        modules = {
            row["module"]
            for row in csv.DictReader(handle)
        }
    assert modules == {
        "QENN",
        "PGQENN",
        "SOInets",
    }
