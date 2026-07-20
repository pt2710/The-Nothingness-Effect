"""Tune every public TNE AI model/training hyperparameter on validation data."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any
import zipfile

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_comprehensive_ai_evaluation import (  # noqa: E402
    CalibratedNoLocalRBMModel,
    _evaluate_with_pgqenn_graph_metrics,
    _module_rows_with_pgqenn,
    _source_removals_without_legacy_name,
    _train_with_temperature_selection,
)
from tools.run_tabular_ai_evaluation import _dataset, _objective  # noqa: E402
from the_nothingness_effect.artificial_intelligence.pgqenn.training_evaluation import (  # noqa: E402
    evaluate_pgqenn_graph_heads,
    reset_pgqenn_graph_evidence,
)


@dataclass(frozen=True)
class Config:
    epochs: int = 20
    learning_rate: float = 0.01
    weight_decay: float = 1e-4
    hidden_dim: int = 16
    K_D: float = 1.0
    soi_scale: float = 1.0
    qenn_count: int = 1
    pgqenn_count: int = 1
    axis_dim: int | None = None
    global_rbm_hidden: int | None = None
    max_clusters: int = 40
    dropout: float = 0.05
    optimize_K_D: bool = True
    adaptive_learning_rate: bool = True


SPACE: tuple[tuple[str, tuple[Any, ...]], ...] = (
    ("epochs", (10, 20, 40)),
    ("learning_rate", (0.003, 0.01, 0.03)),
    ("weight_decay", (0.0, 1e-4, 1e-3)),
    ("hidden_dim", (12, 16, 24)),
    ("K_D", (0.5, 1.0, 2.0)),
    ("soi_scale", (0.5, 1.0, 2.0)),
    ("qenn_count", (1, 2)),
    ("pgqenn_count", (1, 2)),
    ("axis_dim", (None, 8, 16)),
    ("global_rbm_hidden", (None, 8, 16)),
    ("max_clusters", (24, 40, 64)),
    ("dropout", (0.0, 0.05, 0.15)),
    ("optimize_K_D", (False, True)),
    ("adaptive_learning_rate", (False, True)),
)


def build(config: Config) -> CalibratedNoLocalRBMModel:
    return CalibratedNoLocalRBMModel(
        hidden_dim=config.hidden_dim,
        output_dim=2,
        K_D=config.K_D,
        soi_scale=config.soi_scale,
        qenn_count=config.qenn_count,
        pgqenn_count=config.pgqenn_count,
        modality_count=3,
        axis_dim=config.axis_dim,
        global_rbm_hidden=config.global_rbm_hidden,
        max_clusters=config.max_clusters,
        dropout=config.dropout,
    )


def train(config: Config, data, seed: int):
    torch.manual_seed(seed)
    model = build(config)
    run = _train_with_temperature_selection(
        model,
        data.train,
        data.validation,
        epochs=config.epochs,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        seed=seed,
        optimize_K_D=config.optimize_K_D,
        adaptive_learning_rate=config.adaptive_learning_rate,
    )
    return model, run


def score(model, data, seed: int) -> tuple[float, dict[str, Any], list[dict[str, Any]]]:
    evaluation = _evaluate_with_pgqenn_graph_metrics(model, data.validation)
    modules = _module_rows_with_pgqenn(seed, evaluation, data.validation.labels)
    accuracies = [float(row["accuracy"]) for row in modules]
    residuals = [math.tanh(abs(float(row["residual_l2"]))) for row in modules]
    pg_losses = [float(row["cross_entropy"]) for row in modules if row["module"] == "PGQENN"]
    value = (
        _objective(evaluation.metrics)
        + 0.35 * (1.0 - min(accuracies))
        + 0.04 * sum(residuals) / max(1, len(residuals))
        + 0.10 * sum(pg_losses) / max(1, len(pg_losses))
    )
    if not math.isfinite(value):
        raise RuntimeError("non-finite validation objective")
    return float(value), evaluation.metrics, modules


def search(data, seed: int, passes: int) -> tuple[Config, list[dict[str, Any]]]:
    current = Config()
    rows: list[dict[str, Any]] = []
    cache: dict[str, tuple[float, dict[str, Any], Any]] = {}

    def evaluate(config: Config):
        key = json.dumps(asdict(config), sort_keys=True)
        if key not in cache:
            model, run = train(config, data, seed)
            value, metrics, _ = score(model, data, seed)
            cache[key] = value, metrics, run
        return cache[key]

    for pass_index in range(passes):
        changed = False
        for parameter, values in SPACE:
            candidates = []
            for value in values:
                candidate = replace(current, **{parameter: value})
                objective, metrics, run = evaluate(candidate)
                candidates.append((objective, json.dumps(asdict(candidate), sort_keys=True), candidate, metrics, run))
            candidates.sort(key=lambda item: (item[0], item[1]))
            selected = candidates[0][2]
            for objective, _, candidate, metrics, run in candidates:
                rows.append({
                    "pass": pass_index,
                    "parameter": parameter,
                    "candidate": getattr(candidate, parameter),
                    "selected": candidate == selected,
                    "objective": objective,
                    "best_epoch": run.best_epoch,
                    "validation_accuracy": metrics["accuracy"],
                    "validation_macro_f1": metrics["macro_f1"],
                    "validation_cross_entropy": metrics["cross_entropy"],
                    "validation_ece": metrics["expected_calibration_error"],
                    **asdict(candidate),
                })
            changed |= selected != current
            current = selected
        if not changed:
            break
    return current, rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(source: Path, dataset_name: str, output: Path, seeds: tuple[int, ...], passes: int) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    checkpoints = output / "checkpoints"
    checkpoints.mkdir(exist_ok=True)
    reset_pgqenn_graph_evidence()
    search_data, ingestion = _dataset(source, dataset_name, seeds[0])
    selected, search_rows = search(search_data, seeds[0], passes)

    split_rows: list[dict[str, Any]] = []
    module_rows: list[dict[str, Any]] = []
    graph_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    for seed in seeds:
        data, report = _dataset(source, dataset_name, seed)
        model, training = train(selected, data, seed)
        evaluations = {
            split: _evaluate_with_pgqenn_graph_metrics(model, getattr(data, split))
            for split in ("train", "validation", "test")
        }
        for split, evaluation in evaluations.items():
            split_rows.append({"seed": seed, "split": split, **evaluation.metrics})
        test = evaluations["test"]
        module_rows.extend(_module_rows_with_pgqenn(seed, test, data.test.labels))
        graph = evaluate_pgqenn_graph_heads(model, data.test)
        graph_rows.append({"seed": seed, **{k: v for k, v in graph["metrics"].items() if k != "confusion_matrix"}})
        source_rows.extend(_source_removals_without_legacy_name(model, data.test, seed))
        seed_rows.append({
            "seed": seed,
            "best_epoch": training.best_epoch,
            "best_validation_objective": training.best_validation_objective,
            "test_accuracy": test.metrics["accuracy"],
            "test_macro_f1": test.metrics["macro_f1"],
            "test_cross_entropy": test.metrics["cross_entropy"],
            "test_ece": test.metrics["expected_calibration_error"],
            **report,
        })
        torch.save({
            "model_state_dict": model.state_dict(),
            "selected_hyperparameters": asdict(selected),
            "seed": seed,
            "best_epoch": training.best_epoch,
            "best_validation_objective": training.best_validation_objective,
        }, checkpoints / f"seed_{seed}_best.pt")

    for name, rows in (
        ("hyperparameter_search.csv", search_rows),
        ("split_metrics.csv", split_rows),
        ("module_metrics.csv", module_rows),
        ("pgqenn_graph_metrics.csv", graph_rows),
        ("source_removal.csv", source_rows),
        ("seed_summary.csv", seed_rows),
    ):
        write_csv(output / name, rows)

    test_rows = [row for row in split_rows if row["split"] == "test"]
    module_summary = {
        module: {
            "mean_test_accuracy": sum(float(row["accuracy"]) for row in module_rows if row["module"] == module) / max(1, sum(row["module"] == module for row in module_rows)),
            "mean_test_macro_f1": sum(float(row["macro_f1"]) for row in module_rows if row["module"] == module) / max(1, sum(row["module"] == module for row in module_rows)),
        }
        for module in ("QENN", "PGQENN", "SOInets")
    }
    summary = {
        "schema_version": "1.0",
        "dataset": dataset_name,
        "selected_hyperparameters": asdict(selected),
        "searched_hyperparameters": [name for name, _ in SPACE],
        "candidate_counts": {name: len(values) for name, values in SPACE},
        "search_seed": seeds[0],
        "evaluation_seeds": list(seeds),
        "integrated_multimodal": {
            "mean_test_accuracy": sum(float(row["accuracy"]) for row in test_rows) / len(test_rows),
            "mean_test_macro_f1": sum(float(row["macro_f1"]) for row in test_rows) / len(test_rows),
            "mean_test_cross_entropy": sum(float(row["cross_entropy"]) for row in test_rows) / len(test_rows),
            "mean_test_ece": sum(float(row["expected_calibration_error"]) for row in test_rows) / len(test_rows),
        },
        "modules": module_summary,
        "nested_validation_tuning": ["QENN ridge", "PGQENN graph ridge", "main-task ridge", "decoder ridge", "temperature", "dynamic K_D/SOI"],
        "split_policy": "training-only preprocessing; validation-only selection; held-out test used after model selection",
        "search_ingestion": ingestion,
        "claim_boundary": "finite tabular benchmark; not clinical/financial deployment validation or formal theorem proof",
    }
    (output / "evaluation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = {"schema_version": "1.0", "files": [{"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": digest(path)} for path in files]}
    (output / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with zipfile.ZipFile(output.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(output.parent))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dataset", choices=("fraud", "breast-cancer"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--passes", type=int, default=1)
    args = parser.parse_args()
    if args.passes < 1:
        raise SystemExit("--passes must be positive")
    print(json.dumps(run(args.source, args.dataset, args.output, tuple(args.seeds), args.passes), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
