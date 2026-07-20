"""Train, validate and evaluate TNE AI on bounded real CIFAR archive bytes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

import matplotlib.pyplot as plt
import torch

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.run_comprehensive_ai_evaluation import (  # noqa: E402
    CalibratedNoLocalRBMModel,
    _evaluate_with_pgqenn_graph_metrics,
    _module_rows_with_pgqenn,
    _source_removals_without_legacy_name,
    _train_with_temperature_selection,
)
from the_nothingness_effect.artificial_intelligence.multimodal.real_data import (  # noqa: E402
    load_cifar_multimodal_dataset,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.training_evaluation import (  # noqa: E402
    evaluate_pgqenn_graph_heads,
    reset_pgqenn_graph_evidence,
)


CLAIM_BOUNDARY = (
    "bounded deterministic held-out evaluation on public CIFAR archive bytes; "
    "not unrestricted real-world generalization, empirical deployment validation, "
    "or formal theorem proof"
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _confusion_plot(
    path: Path, matrix: torch.Tensor, class_names: tuple[str, ...]
) -> None:
    figure, axis = plt.subplots(
        figsize=(max(6, len(class_names) * 0.55), 5.5)
    )
    image = axis.imshow(matrix.detach().cpu().numpy())
    axis.set_title("Held-out TNE multimodal confusion")
    axis.set_xlabel("Predicted class")
    axis.set_ylabel("True class")
    axis.set_xticks(
        range(len(class_names)), class_names, rotation=75, ha="right"
    )
    axis.set_yticks(range(len(class_names)), class_names)
    figure.colorbar(image, ax=axis, label="Count")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _metric_plot(path: Path, rows: list[dict[str, Any]]) -> None:
    labels = [f"{row['module']}:{row['instance']}" for row in rows]
    accuracy = [float(row["accuracy"]) for row in rows]
    macro_f1 = [float(row["macro_f1"]) for row in rows]
    positions = torch.arange(len(rows), dtype=torch.float64).numpy()
    width = 0.38
    figure, axis = plt.subplots(
        figsize=(max(7, len(rows) * 1.2), 5.0)
    )
    axis.bar(positions - width / 2, accuracy, width, label="Accuracy")
    axis.bar(positions + width / 2, macro_f1, width, label="Macro F1")
    axis.set_ylim(0.0, 1.05)
    axis.set_xticks(positions, labels, rotation=25, ha="right")
    axis.set_title("Held-out module metrics")
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def run_real_data_evaluation(
    *,
    archive: str | Path,
    variant: str,
    output_dir: str | Path,
    seeds: tuple[int, ...] = (0, 1, 2),
    epochs: int = 20,
    samples_per_class: int = 24,
    max_classes: int | None = None,
) -> dict[str, Any]:
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be a non-empty unique tuple")
    if epochs < 1:
        raise ValueError("epochs must be positive")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plots = output / "plots"
    checkpoints = output / "checkpoints"
    plots.mkdir(exist_ok=True)
    checkpoints.mkdir(exist_ok=True)
    reset_pgqenn_graph_evidence()

    split_rows: list[dict[str, Any]] = []
    module_rows: list[dict[str, Any]] = []
    pgqenn_rows: list[dict[str, Any]] = []
    source_removal_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    ingestion_reports: list[dict[str, Any]] = []
    aggregate_confusion: torch.Tensor | None = None
    class_names: tuple[str, ...] | None = None
    modality_names: tuple[str, ...] | None = None

    for seed in seeds:
        torch.manual_seed(seed)
        loaded = load_cifar_multimodal_dataset(
            archive,
            variant=variant,
            seed=seed,
            samples_per_class=samples_per_class,
            max_classes=max_classes,
        )
        dataset = loaded.dataset
        ingestion_reports.append(loaded.report)
        current_modalities = tuple(sorted(dataset.train.modalities))
        if class_names is None:
            class_names = dataset.class_names
            modality_names = current_modalities
        elif class_names != dataset.class_names or modality_names != current_modalities:
            raise RuntimeError("CIFAR class or modality domain changed between seeds")
        model = CalibratedNoLocalRBMModel(
            output_dim=len(dataset.class_names),
            modality_count=len(dataset.train.modalities),
            max_clusters=max(40, len(dataset.train.modalities) * 8),
        )
        started = time.perf_counter()
        training = _train_with_temperature_selection(
            model,
            dataset.train,
            dataset.validation,
            epochs=epochs,
            seed=seed,
            optimize_K_D=True,
            adaptive_learning_rate=True,
        )
        training_seconds = time.perf_counter() - started
        evaluations = {
            split: _evaluate_with_pgqenn_graph_metrics(
                model, getattr(dataset, split)
            )
            for split in ("train", "validation", "test")
        }
        for split, evaluation in evaluations.items():
            split_rows.append(
                {
                    "seed": seed,
                    "split": split,
                    **evaluation.metrics,
                    "closure_status": str(
                        getattr(
                            evaluation.output.closure_status,
                            "value",
                            evaluation.output.closure_status,
                        )
                    ),
                }
            )
        test = evaluations["test"]
        aggregate_confusion = (
            test.confusion_matrix.detach().cpu().clone()
            if aggregate_confusion is None
            else aggregate_confusion + test.confusion_matrix.detach().cpu()
        )
        seed_module_rows = _module_rows_with_pgqenn(
            seed, test, dataset.test.labels
        )
        for row in seed_module_rows:
            row["dataset"] = variant
        module_rows.extend(seed_module_rows)
        graph = evaluate_pgqenn_graph_heads(model, dataset.test)
        pgqenn_rows.append(
            {
                "seed": seed,
                **{
                    key: value
                    for key, value in graph["metrics"].items()
                    if key != "confusion_matrix"
                },
                "closure_status": "declared_runtime_status_preserved",
            }
        )
        source_removal_rows.extend(
            {"dataset": variant, **row}
            for row in _source_removals_without_legacy_name(
                model, dataset.test, seed
            )
        )
        checkpoint_path = checkpoints / f"{variant}-seed-{seed}.pt"
        torch.save(
            {
                "schema_version": "1.0",
                "dataset": variant,
                "seed": seed,
                "class_names": dataset.class_names,
                "modalities": tuple(dataset.train.modalities),
                "best_epoch": training.best_epoch,
                "best_validation_objective": training.best_validation_objective,
                "state_dict": model.state_dict(),
                "claim_boundary": CLAIM_BOUNDARY,
            },
            checkpoint_path,
        )
        seed_rows.append(
            {
                "dataset": variant,
                "seed": seed,
                "best_epoch": training.best_epoch,
                "best_validation_objective": training.best_validation_objective,
                "restored_best_checkpoint": training.restored_best_checkpoint,
                "training_seconds": training_seconds,
                "test_accuracy": test.metrics["accuracy"],
                "test_macro_f1": test.metrics["macro_f1"],
                "test_cross_entropy": test.metrics["cross_entropy"],
                "test_ece": test.metrics["expected_calibration_error"],
                "pgqenn_graph_accuracy": graph["metrics"]["accuracy"],
                "pgqenn_graph_macro_f1": graph["metrics"]["macro_f1"],
                "checkpoint_sha256": _sha256_file(checkpoint_path),
            }
        )

    if class_names is None or modality_names is None or aggregate_confusion is None:
        raise RuntimeError("real-data evaluation produced no evidence")
    if not all(bool(report["leakage_free"]) for report in ingestion_reports):
        raise RuntimeError("real-data evaluation detected split leakage")
    numeric_values = [
        float(value)
        for row in split_rows + module_rows + pgqenn_rows
        for value in row.values()
        if isinstance(value, (int, float))
    ]
    if not numeric_values or not all(
        math.isfinite(value) for value in numeric_values
    ):
        raise RuntimeError("real-data evaluation produced non-finite metrics")

    _write_csv(output / "split_metrics.csv", split_rows)
    _write_csv(output / "module_metrics.csv", module_rows)
    _write_csv(output / "pgqenn_graph_metrics.csv", pgqenn_rows)
    _write_csv(output / "source_removal.csv", source_removal_rows)
    _write_csv(output / "seed_summary.csv", seed_rows)
    _write_json(output / "cifar_ingestion_reports.json", ingestion_reports)
    _confusion_plot(
        plots / "held_out_confusion.png", aggregate_confusion, class_names
    )
    _metric_plot(
        plots / "held_out_module_metrics.png",
        [row for row in module_rows if int(row["seed"]) == int(seeds[0])],
    )

    means: dict[str, float] = {}
    for key in (
        "test_accuracy",
        "test_macro_f1",
        "test_cross_entropy",
        "test_ece",
        "pgqenn_graph_accuracy",
        "pgqenn_graph_macro_f1",
    ):
        means[f"mean_{key}"] = sum(
            float(row[key]) for row in seed_rows
        ) / len(seed_rows)
    report = {
        "schema_version": "1.0",
        "dataset": variant,
        "archive_sha256": ingestion_reports[0]["archive_sha256"],
        "seeds": list(seeds),
        "epochs": epochs,
        "samples_per_class": samples_per_class,
        "classes": len(class_names),
        "class_names": list(class_names),
        "modalities": list(modality_names),
        "leakage_free_all_seeds": True,
        "training_status": "completed_all_seeds",
        "validation_status": "best_checkpoint_restored_all_seeds",
        "test_status": "held_out_evaluated_all_seeds",
        "qenn_evidence": "per-sample held-out metrics in module_metrics.csv",
        "pgqenn_evidence": (
            "graph-level held-out metrics in pgqenn_graph_metrics.csv"
        ),
        "soinets_evidence": "integrated held-out metrics in module_metrics.csv",
        "means": means,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(output / "evaluation_summary.json", report)
    artifacts = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = {
        "schema_version": "1.0",
        "artifact_count": len(artifacts),
        "files": [
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
            for path in artifacts
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _write_json(output / "artifact_manifest.json", manifest)
    report["artifact_count"] = len(artifacts)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument(
        "--variant", choices=("cifar-10", "cifar-100"), required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--samples-per-class", type=int, default=24)
    parser.add_argument("--max-classes", type=int)
    args = parser.parse_args()
    report = run_real_data_evaluation(
        archive=args.archive,
        variant=args.variant,
        output_dir=args.output,
        seeds=tuple(args.seeds),
        epochs=args.epochs,
        samples_per_class=args.samples_per_class,
        max_classes=args.max_classes,
    )
    print(
        "real_data_ai_evaluation=completed "
        f"dataset={report['dataset']} classes={report['classes']} "
        f"artifacts={report['artifact_count']} "
        f"mean_accuracy={report['means']['mean_test_accuracy']:.6f} "
        f"pgqenn_graph_accuracy="
        f"{report['means']['mean_pgqenn_graph_accuracy']:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
