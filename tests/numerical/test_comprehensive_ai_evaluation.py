from __future__ import annotations

import csv
import json

import torch

from tools.run_comprehensive_ai_evaluation import (
    run_comprehensive_ai_evaluation,
)
from the_nothingness_effect.artificial_intelligence.multimodal.axes import (
    ModalityAxisNetwork,
)
from the_nothingness_effect.artificial_intelligence.multimodal.data import (
    dataset_variation_summary,
    make_synthetic_multimodal_dataset,
)
from the_nothingness_effect.artificial_intelligence.multimodal.geometric_model import (
    TNEGeometricMultimodalModel,
)
from the_nothingness_effect.artificial_intelligence.multimodal.rbm import (
    GaussianBernoulliEnergyLayer,
)


def test_extended_dataset_contains_multiple_varied_points_per_modality():
    dataset = make_synthetic_multimodal_dataset(
        samples_per_class=6,
        seed=11,
        include_extended_modalities=True,
    )
    assert set(dataset.train.modalities) == {
        "color",
        "sound",
        "state",
        "text",
        "vision",
    }
    summary = dataset_variation_summary(dataset)
    assert len(summary) == 15
    assert all(int(row["sample_count"]) > 1 for row in summary)
    assert all(
        float(row["mean_pairwise_distance"]) > 0.0
        for row in summary
    )


def test_modality_axis_network_exposes_dual_3d_and_mpl_tc_geometry():
    torch.manual_seed(5)
    network = ModalityAxisNetwork(input_dim=6, axis_dim=12)
    names = ("color", "sound", "state", "text", "vision")
    tokens = torch.rand(8, len(names), 6)
    weights = torch.softmax(torch.rand(8, len(names)), dim=-1)
    state = network(tokens, names, weights)
    assert state.geometric_coordinates.shape == (8, len(names), 3)
    assert state.mpl_tc_stream_weights.shape == (8, len(names), 4)
    assert state.mpl_tc_growth_vectors.shape == (8, len(names), 3)
    assert torch.allclose(
        state.dual_coordinates,
        -state.geometric_coordinates,
    )
    assert torch.allclose(
        state.mpl_tc_stream_weights.sum(dim=-1),
        torch.ones(8, len(names)),
        atol=1e-6,
    )


def test_geometric_model_contains_no_local_rbm_and_one_global_rbm():
    model = TNEGeometricMultimodalModel()
    energy_layers = [
        module
        for module in model.modules()
        if isinstance(module, GaussianBernoulliEnergyLayer)
    ]
    assert not hasattr(model, "local_energy")
    assert len(energy_layers) == 1
    assert energy_layers[0] is model.global_energy


def test_comprehensive_evaluation_writes_complete_visual_evidence(tmp_path):
    output = tmp_path / "comprehensive-ai"
    report = run_comprehensive_ai_evaluation(
        output,
        seeds=(0,),
        epochs=1,
        samples_per_class=5,
    )
    assert report["training_status"] == "completed_all_seeds"
    assert report["validation_status"] == (
        "best_checkpoint_restored_all_seeds"
    )
    assert report["test_status"] == "held_out_evaluated_all_seeds"
    assert report["pgqenn_graph_training_status"] == (
        "validation_selected_ridge_finetuned_all_seeds"
    )
    assert report["pgqenn_graph_validation_status"] == (
        "ridge_and_temperature_selected_on_validation_only"
    )
    assert report["pgqenn_graph_test_status"] == (
        "held_out_graphs_evaluated_all_seeds"
    )
    assert 0.0 <= report["pgqenn_graph_mean_test_accuracy"] <= 1.0
    assert 0.0 <= report["pgqenn_graph_mean_test_macro_f1"] <= 1.0
    assert report["all_metrics_finite"]
    assert report["all_splits_have_multiple_varied_points"]
    assert report["plot_count"] >= 23

    expected_tables = {
        "dataset_samples.csv",
        "dataset_variation.csv",
        "split_metrics.csv",
        "aggregate_metrics.csv",
        "seed_summary.csv",
        "prediction_records.csv",
        "class_metrics.csv",
        "geometry_coordinates.csv",
        "training_history.csv",
        "source_removal.csv",
        "reconstruction_metrics.csv",
        "calibration_bins.csv",
        "module_metrics.csv",
        "pgqenn_graph_metrics.csv",
        "pgqenn_graph_predictions.csv",
        "pgqenn_graph_hyperparameters.csv",
        "pgqenn_graph_source_removal.csv",
    }
    assert expected_tables <= {
        path.name
        for path in output.glob("*.csv")
    }
    assert not (output / "plots" / "rbm_free_energy.png").exists()
    assert (output / "plots" / "global_rbm_free_energy.png").is_file()
    assert (output / "plots" / "pgqenn_graph_accuracy.png").is_file()
    assert (output / "plots" / "pgqenn_graph_cross_entropy.png").is_file()
    assert (output / "plots" / "pgqenn_graph_confusion.png").is_file()

    summary = json.loads(
        (output / "pgqenn_graph_summary.json").read_text(encoding="utf-8")
    )
    assert summary["training_status"] == (
        "validation_selected_ridge_finetuned_all_seeds"
    )
    assert summary["graph_semantics"] == (
        "one_aligned_observation_with_named_modality_nodes"
    )
    assert isinstance(summary["source_removal_nondegenerate"], bool)

    with (output / "module_metrics.csv").open(encoding="utf-8") as handle:
        module_rows = list(csv.DictReader(handle))
    pgqenn_rows = [row for row in module_rows if row["module"] == "PGQENN"]
    assert pgqenn_rows
    assert all(row["accuracy"] not in {"", "None"} for row in pgqenn_rows)
    assert all(row["macro_f1"] not in {"", "None"} for row in pgqenn_rows)
    assert all(
        row["evaluation_scope"] == "graph_level_modality_node_classification"
        for row in pgqenn_rows
    )

    manifest_path = output / "artifact_manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_count"] >= 37
    assert manifest["plot_count"] >= 23
    assert manifest["pgqenn_graph_evidence"]["test_status"] == (
        "held_out_graphs_evaluated_all_seeds"
    )
