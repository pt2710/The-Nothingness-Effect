"""Comprehensive train/validation/test evidence for TNE Artificial Intelligence."""

from __future__ import annotations

import math
from pathlib import Path
import time
from typing import Any, Iterable

import torch

from .comprehensive_plots import (
    plot_calibration,
    plot_class_metrics,
    plot_confusions,
    plot_geometry,
    plot_latent,
    plot_learning,
    plot_summaries,
    plot_training_diagnostics,
)
from .comprehensive_support import (
    CLAIM_BOUNDARY,
    aggregate_metrics as build_aggregate_metrics,
    calibration_rows as build_calibration_rows,
    class_rows as build_class_rows,
    dataset_rows as build_dataset_rows,
    extended_metrics,
    geometry_rows as build_geometry_rows,
    module_rows as build_module_rows,
    prediction_rows as build_prediction_rows,
    sha256_file,
    source_removals,
    status_value,
    write_csv,
    write_json,
)
from .multimodal.data import (
    dataset_variation_summary,
    make_synthetic_multimodal_dataset,
)
from .multimodal.evaluation import (
    MultimodalEvaluation,
    evaluate_multimodal_model,
)
from .multimodal.geometric_model import TNEGeometricMultimodalModel
from .multimodal.training import train_multimodal_model


def run_comprehensive_ai_evaluation(
    output_dir: str | Path,
    *,
    seeds: Iterable[int] = (0, 1, 2),
    epochs: int = 10,
    samples_per_class: int = 16,
) -> dict[str, Any]:
    """Train, validate, evaluate and visualize the integrated TNE AI system."""

    output = Path(output_dir)
    plots = output / "plots"
    checkpoints = output / "checkpoints"
    plots.mkdir(parents=True, exist_ok=True)
    checkpoints.mkdir(parents=True, exist_ok=True)
    seeds = tuple(int(seed) for seed in seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be a non-empty unique sequence")
    if epochs < 1 or samples_per_class < 5:
        raise ValueError(
            "epochs must be positive and samples_per_class at least five"
        )

    variation_records: list[dict[str, Any]] = []
    dataset_records: list[dict[str, Any]] = []
    split_records: list[dict[str, Any]] = []
    prediction_records: list[dict[str, Any]] = []
    class_records: list[dict[str, Any]] = []
    geometry_records: list[dict[str, Any]] = []
    history_records: list[dict[str, Any]] = []
    source_records: list[dict[str, Any]] = []
    reconstruction_records: list[dict[str, Any]] = []
    module_records: list[dict[str, Any]] = []
    seed_records: list[dict[str, Any]] = []
    latent_records: list[dict[str, Any]] = []
    aggregate_confusion: torch.Tensor | None = None
    class_names: tuple[str, ...] | None = None

    for seed in seeds:
        torch.manual_seed(seed)
        dataset = make_synthetic_multimodal_dataset(
            samples_per_class=samples_per_class,
            seed=seed,
            include_extended_modalities=True,
        )
        class_names = dataset.class_names
        variation_records.extend(
            {"seed": seed, **row}
            for row in dataset_variation_summary(dataset)
        )
        dataset_records.extend(
            {"seed": seed, **row}
            for row in build_dataset_rows(dataset)
        )
        model = TNEGeometricMultimodalModel(
            modality_count=len(dataset.train.modalities),
            max_clusters=max(40, len(dataset.train.modalities) * 8),
        )
        started = time.perf_counter()
        training = train_multimodal_model(
            model,
            dataset.train,
            dataset.validation,
            epochs=epochs,
            seed=seed,
            optimize_K_D=True,
            adaptive_learning_rate=True,
        )
        training_seconds = time.perf_counter() - started

        evaluations: dict[str, MultimodalEvaluation] = {}
        for split in ("train", "validation", "test"):
            batch = getattr(dataset, split)
            evaluation = evaluate_multimodal_model(model, batch)
            evaluations[split] = evaluation
            split_records.append(
                {
                    "seed": seed,
                    "split": split,
                    **evaluation.metrics,
                    **extended_metrics(evaluation),
                    "closure_status": status_value(
                        evaluation.output.closure_status
                    ),
                }
            )
            prediction_records.extend(
                build_prediction_rows(
                    seed,
                    split,
                    evaluation,
                    batch.labels,
                    dataset.class_names,
                )
            )
            class_records.extend(
                build_class_rows(
                    seed,
                    split,
                    evaluation.confusion_matrix,
                    dataset.class_names,
                )
            )
            geometry_records.extend(
                build_geometry_rows(
                    seed,
                    split,
                    evaluation,
                    batch.labels,
                )
            )

        test = evaluations["test"]
        aggregate_confusion = (
            test.confusion_matrix.clone()
            if aggregate_confusion is None
            else aggregate_confusion + test.confusion_matrix
        )
        module_records.extend(
            build_module_rows(seed, test, dataset.test.labels)
        )
        source_records.extend(
            source_removals(model, dataset.test, seed)
        )
        for modality, rmse in test.reconstruction_rmse.items():
            reconstruction_records.append(
                {"seed": seed, "modality": modality, "rmse": rmse}
            )
        for sample_index, latent in enumerate(
            test.output.hidden.detach().cpu()
        ):
            latent_records.append(
                {
                    "seed": seed,
                    "sample_index": sample_index,
                    "label": int(dataset.test.labels[sample_index]),
                    "latent": [float(value) for value in latent],
                }
            )

        modality_names = test.output.axis_state.modality_names
        for epoch_state in training.history:
            row: dict[str, Any] = {
                "seed": seed,
                "epoch": epoch_state.epoch,
                "train_total_loss": epoch_state.train_total_loss,
                "train_task_loss": epoch_state.train_task_loss,
                "train_reconstruction_loss": (
                    epoch_state.train_reconstruction_loss
                ),
                "train_energy_loss": epoch_state.train_energy_loss,
                "train_closure_penalty": epoch_state.train_closure_penalty,
                "train_accuracy": epoch_state.train_accuracy,
                "validation_loss": epoch_state.validation_loss,
                "validation_accuracy": epoch_state.validation_accuracy,
                "gradient_norm": epoch_state.gradient_norm,
                "local_free_energy": epoch_state.local_free_energy,
                "global_free_energy": epoch_state.global_free_energy,
                "active_clusters": epoch_state.cluster_count,
                "growth_events": epoch_state.growth_event_count,
                "K_D": epoch_state.K_D,
                "soi_scale": epoch_state.soi_scale,
                "learning_rate": epoch_state.learning_rate,
                "validation_objective": epoch_state.validation_objective,
                "is_best_epoch": int(
                    epoch_state.epoch == training.best_epoch
                ),
            }
            for index, modality in enumerate(modality_names):
                row[f"weight_{modality}"] = (
                    epoch_state.modality_weights[index]
                )
            history_records.append(row)

        checkpoint = {
            "schema_version": "2.0",
            "seed": seed,
            "best_epoch": training.best_epoch,
            "best_validation_objective": (
                training.best_validation_objective
            ),
            "restored_best_checkpoint": training.restored_best_checkpoint,
            "state_dict": model.state_dict(),
            "class_names": dataset.class_names,
            "modalities": tuple(dataset.train.modalities),
            "claim_boundary": CLAIM_BOUNDARY,
        }
        checkpoint_path = checkpoints / f"seed_{seed}_best.pt"
        torch.save(checkpoint, checkpoint_path)
        train_metrics = evaluations["train"].metrics
        validation_metrics = evaluations["validation"].metrics
        test_metrics = test.metrics
        seed_records.append(
            {
                "seed": seed,
                "best_epoch": training.best_epoch,
                "restored_best_checkpoint": (
                    training.restored_best_checkpoint
                ),
                "train_accuracy": train_metrics["accuracy"],
                "validation_accuracy": validation_metrics["accuracy"],
                "test_accuracy": test_metrics["accuracy"],
                "train_cross_entropy": train_metrics["cross_entropy"],
                "validation_cross_entropy": (
                    validation_metrics["cross_entropy"]
                ),
                "test_cross_entropy": test_metrics["cross_entropy"],
                "test_macro_f1": test_metrics["macro_f1"],
                "test_balanced_accuracy": (
                    test_metrics["balanced_accuracy"]
                ),
                "test_ece": test_metrics["expected_calibration_error"],
                "training_seconds": training_seconds,
                "checkpoint_bytes": checkpoint_path.stat().st_size,
                "active_clusters": test_metrics["active_clusters"],
                "closure_status": status_value(
                    test.output.closure_status
                ),
            }
        )

    if aggregate_confusion is None or class_names is None:
        raise RuntimeError("comprehensive evaluation produced no results")

    aggregate_records = build_aggregate_metrics(split_records)
    calibration_records = build_calibration_rows(prediction_records)
    tables = {
        "dataset_samples.csv": dataset_records,
        "dataset_variation.csv": variation_records,
        "split_metrics.csv": split_records,
        "aggregate_metrics.csv": aggregate_records,
        "seed_summary.csv": seed_records,
        "prediction_records.csv": prediction_records,
        "class_metrics.csv": class_records,
        "geometry_coordinates.csv": geometry_records,
        "training_history.csv": history_records,
        "source_removal.csv": source_records,
        "reconstruction_metrics.csv": reconstruction_records,
        "module_metrics.csv": module_records,
        "calibration_bins.csv": calibration_records,
    }
    for filename, rows in tables.items():
        write_csv(output / filename, rows)

    plot_learning(plots, history_records)
    plot_confusions(plots, aggregate_confusion, class_names)
    plot_class_metrics(plots, class_records)
    plot_calibration(
        plots,
        calibration_records,
        prediction_records,
    )
    plot_geometry(plots, geometry_records)
    plot_training_diagnostics(plots, history_records)
    plot_summaries(
        plots,
        split_records,
        source_records,
        variation_records,
        reconstruction_records,
        module_records,
    )
    plot_latent(plots, latent_records)

    plot_files = sorted(plots.glob("*.png"))
    finite = all(
        math.isfinite(float(value))
        for row in split_records
        for key, value in row.items()
        if key not in {"seed", "split", "closure_status"}
        and isinstance(value, (int, float))
    )
    varied = all(
        int(row["sample_count"]) > 1
        and float(row["mean_pairwise_distance"]) > 0.0
        for row in variation_records
    )
    restored = all(
        bool(row["restored_best_checkpoint"])
        for row in seed_records
    )
    if len(plot_files) < 20:
        raise RuntimeError(
            "comprehensive evaluation generated fewer than 20 plots"
        )
    if not finite or not varied or not restored:
        raise RuntimeError(
            "comprehensive evaluation failed finite, variation or checkpoint gates"
        )

    configuration = {
        "schema_version": "2.0",
        "architecture": "TNEGeometricMultimodalModel",
        "modules": ["QENN", "PGQENN", "SOInets"],
        "modalities": ["color", "sound", "state", "text", "vision"],
        "seeds": list(seeds),
        "epochs": epochs,
        "samples_per_class": samples_per_class,
        "dataset_points_per_seed": (
            samples_per_class * len(class_names)
        ),
        "best_checkpoint_selection": "minimum validation objective",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(output / "configuration.json", configuration)
    metrics = {
        "schema_version": "2.0",
        "training_status": "completed_all_seeds",
        "validation_status": "best_checkpoint_restored_all_seeds",
        "test_status": "held_out_evaluated_all_seeds",
        "all_metrics_finite": finite,
        "all_splits_have_multiple_varied_points": varied,
        "plot_count": len(plot_files),
        "seed_summary": seed_records,
        "aggregate_metrics": aggregate_records,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(output / "metrics.json", metrics)

    report_lines = [
        "# TNE Artificial Intelligence Comprehensive Evaluation",
        "",
        f"**Claim boundary:** {CLAIM_BOUNDARY}.",
        "",
        "## Dataset",
        "",
        f"- Modalities: {', '.join(configuration['modalities'])}",
        f"- Classes: {len(class_names)}",
        f"- Samples per class and seed: {samples_per_class}",
        (
            "- Total observations per seed: "
            f"{configuration['dataset_points_per_seed']}"
        ),
        "- Every split and modality passed the pairwise-variation gate.",
        "",
        "## Seed results",
        "",
        (
            "| Seed | Best epoch | Train acc. | Validation acc. | "
            "Test acc. | Macro F1 | ECE |"
        ),
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in seed_records:
        report_lines.append(
            "| {seed} | {best_epoch} | {train_accuracy:.6f} | "
            "{validation_accuracy:.6f} | {test_accuracy:.6f} | "
            "{test_macro_f1:.6f} | {test_ece:.6f} |".format(**row)
        )
    report_lines.extend(
        [
            "",
            "## Architecture evidence",
            "",
            "- Shared Observation--Collapse encoding is retained.",
            "- Modalities occupy distinct rotated three-dimensional frames.",
            "- Every coordinate has an antipodal dual carrier.",
            "- Negative Observer-Horizon values increase dual participation.",
            "- Four MPL-TC streams use rotated tetrahedral directions.",
            "- QENN, PGQENN and SOInets diagnostics are exported.",
            "",
            "## Artifacts",
            "",
            f"- CSV result tables: {len(tables)}",
            f"- PNG diagnostics: {len(plot_files)}",
            f"- Model checkpoints: {len(seeds)}",
        ]
    )
    (output / "evaluation_report.md").write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    artifact_paths = sorted(
        path
        for path in output.rglob("*")
        if path.is_file() and path.name != "artifact_manifest.json"
    )
    manifest = {
        "schema_version": "2.0",
        "artifact_count": len(artifact_paths),
        "plot_count": len(plot_files),
        "files": [
            {
                "path": str(path.relative_to(output)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in artifact_paths
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(output / "artifact_manifest.json", manifest)
    return {
        **metrics,
        "artifact_count": manifest["artifact_count"],
    }
