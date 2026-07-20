"""Tune, train, validate and evaluate TNE AI on real tabular datasets."""
from __future__ import annotations

import argparse
import csv
import json
import math
import zipfile
from pathlib import Path
import sys
from typing import Any

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
from the_nothingness_effect.artificial_intelligence.multimodal.data import (  # noqa: E402
    MultimodalBatch,
    MultimodalDataset,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.training_evaluation import (  # noqa: E402
    evaluate_pgqenn_graph_heads,
    reset_pgqenn_graph_evidence,
)


def _numeric_values(row: dict[str | None, str | list[str] | None], fields: list[str]) -> list[float] | None:
    values: list[float] = []
    for name in fields:
        raw = row.get(name)
        if raw is None or isinstance(raw, list):
            return None
        text = raw.strip()
        if not text:
            return None
        try:
            values.append(float(text))
        except ValueError:
            return None
    return values


def _read_rows(path: Path, dataset: str) -> tuple[list[list[float]], list[int], list[str]]:
    if dataset == "fraud":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".csv")]
            if names != ["creditcard.csv"]:
                raise RuntimeError("fraud archive must contain only creditcard.csv")
            handle = archive.open(names[0])
            text = (line.decode("utf-8") for line in handle)
            reader = csv.DictReader(text)
            fields = [
                name.strip()
                for name in (reader.fieldnames or ())
                if name is not None and name.strip() and name.strip() != "Class"
            ]
            rows: list[list[float]] = []
            labels: list[int] = []
            skipped = 0
            for row in reader:
                values = _numeric_values(row, fields)
                label_text = row.get("Class")
                if values is None or not isinstance(label_text, str) or not label_text.strip():
                    skipped += 1
                    continue
                rows.append(values)
                labels.append(int(label_text))
            if not rows:
                raise RuntimeError("fraud CSV contains no complete numeric observations")
            if skipped > max(5, int(0.001 * (len(rows) + skipped))):
                raise RuntimeError(f"fraud CSV contains too many malformed observations: {skipped}")
            return rows, labels, fields
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = [
            name.strip()
            for name in (reader.fieldnames or ())
            if name is not None
            and name.strip()
            and name.strip() not in {"id", "diagnosis", "Unnamed: 32"}
        ]
        rows: list[list[float]] = []
        labels: list[int] = []
        skipped = 0
        for row in reader:
            diagnosis = row.get("diagnosis")
            diagnosis = diagnosis.strip() if isinstance(diagnosis, str) else ""
            values = _numeric_values(row, fields)
            if diagnosis not in {"M", "B"} or values is None:
                skipped += 1
                continue
            rows.append(values)
            labels.append(1 if diagnosis == "M" else 0)
        if not rows:
            raise RuntimeError("breast-cancer CSV contains no complete labeled observations")
        if skipped > max(5, int(0.01 * (len(rows) + skipped))):
            raise RuntimeError(
                f"breast-cancer CSV contains too many malformed observations: {skipped}"
            )
        return rows, labels, fields


def _indices(labels: list[int], seed: int, dataset: str) -> tuple[list[int], list[int], list[int]]:
    generator = torch.Generator().manual_seed(seed)
    by_class = {label: [] for label in sorted(set(labels))}
    for index, label in enumerate(labels):
        by_class[label].append(index)
    selected: dict[int, list[int]] = {}
    for label, values in by_class.items():
        order = torch.randperm(len(values), generator=generator).tolist()
        ordered = [values[i] for i in order]
        if dataset == "fraud" and label == 0:
            ordered = ordered[: min(len(ordered), 12 * len(by_class[1]))]
        selected[label] = ordered
    train, validation, test = [], [], []
    for values in selected.values():
        n = len(values)
        a, b = max(2, int(0.60 * n)), max(3, int(0.80 * n))
        train.extend(values[:a])
        validation.extend(values[a:b])
        test.extend(values[b:])
    return train, validation, test


def _dataset(path: Path, dataset: str, seed: int) -> tuple[MultimodalDataset, dict[str, Any]]:
    rows, labels, fields = _read_rows(path, dataset)
    matrix = torch.tensor(rows, dtype=torch.float64)
    targets = torch.tensor(labels, dtype=torch.long)
    train_idx, val_idx, test_idx = _indices(labels, seed, dataset)
    train_tensor = matrix[train_idx]
    centre = train_tensor.median(dim=0).values
    scale = (train_tensor - centre).abs().median(dim=0).values.clamp_min(1e-8)
    scaled = ((matrix - centre) / scale).clamp(-20.0, 20.0).to(torch.float32)
    groups = torch.tensor_split(torch.arange(scaled.shape[1]), 3)

    def batch(indices: list[int]) -> MultimodalBatch:
        index = torch.tensor(indices, dtype=torch.long)
        modalities = {
            f"tabular_group_{group_index + 1}": scaled[index][:, group]
            for group_index, group in enumerate(groups)
        }
        return MultimodalBatch(modalities, targets[index]).validate()

    train, validation, test = batch(train_idx), batch(val_idx), batch(test_idx)
    report = {
        "dataset": dataset,
        "rows": len(rows),
        "features": len(fields),
        "class_counts": {str(label): labels.count(label) for label in sorted(set(labels))},
        "train_rows": len(train_idx),
        "validation_rows": len(val_idx),
        "test_rows": len(test_idx),
        "preprocessing": "training-only median and MAD scaling; clipped to [-20,20]",
        "split_seed": seed,
    }
    return MultimodalDataset(train, validation, test, ("negative", "positive")), report


def _objective(metrics: dict[str, Any]) -> float:
    accuracy = float(metrics["accuracy"])
    macro_f1 = float(metrics["macro_f1"])
    cross_entropy = float(metrics["cross_entropy"])
    ece = float(metrics["expected_calibration_error"])
    return cross_entropy + 0.35 * ece + 0.75 * (1.0 - macro_f1) + 0.20 * (1.0 - accuracy)


def run(*, source: Path, dataset_name: str, output: Path, seeds: tuple[int, ...], epochs: tuple[int, ...], clusters: tuple[int, ...]) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    reset_pgqenn_graph_evidence()
    search_rows: list[dict[str, Any]] = []
    best: tuple[float, int, int] | None = None
    search_data, _ = _dataset(source, dataset_name, seeds[0])
    for epoch_count in epochs:
        for max_clusters in clusters:
            torch.manual_seed(seeds[0])
            model = CalibratedNoLocalRBMModel(output_dim=2, modality_count=3, max_clusters=max_clusters)
            _train_with_temperature_selection(model, search_data.train, search_data.validation, epochs=epoch_count, seed=seeds[0], optimize_K_D=True, adaptive_learning_rate=True)
            evaluation = _evaluate_with_pgqenn_graph_metrics(model, search_data.validation)
            score = _objective(evaluation.metrics)
            row = {"epochs": epoch_count, "max_clusters": max_clusters, "objective": score, **evaluation.metrics}
            search_rows.append(row)
            if best is None or score < best[0]:
                best = (score, epoch_count, max_clusters)
    if best is None:
        raise RuntimeError("hyperparameter search produced no candidate")

    split_rows, module_rows, pgqenn_rows, source_rows, seed_rows = [], [], [], [], []
    for seed in seeds:
        data, ingestion = _dataset(source, dataset_name, seed)
        torch.manual_seed(seed)
        model = CalibratedNoLocalRBMModel(output_dim=2, modality_count=3, max_clusters=best[2])
        training = _train_with_temperature_selection(model, data.train, data.validation, epochs=best[1], seed=seed, optimize_K_D=True, adaptive_learning_rate=True)
        evaluations = {split: _evaluate_with_pgqenn_graph_metrics(model, getattr(data, split)) for split in ("train", "validation", "test")}
        for split, evaluation in evaluations.items():
            split_rows.append({"seed": seed, "split": split, **evaluation.metrics})
        test = evaluations["test"]
        module_rows.extend(_module_rows_with_pgqenn(seed, test, data.test.labels))
        graph = evaluate_pgqenn_graph_heads(model, data.test)
        pgqenn_rows.append({"seed": seed, **{key: value for key, value in graph["metrics"].items() if key != "confusion_matrix"}})
        source_rows.extend(_source_removals_without_legacy_name(model, data.test, seed))
        seed_rows.append({"seed": seed, "best_epoch": training.best_epoch, "best_validation_objective": training.best_validation_objective, "test_accuracy": test.metrics["accuracy"], "test_macro_f1": test.metrics["macro_f1"], "test_cross_entropy": test.metrics["cross_entropy"], "test_ece": test.metrics["expected_calibration_error"], **ingestion})

    def write_csv(name: str, rows: list[dict[str, Any]]) -> None:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with (output / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    for name, rows in (("hyperparameter_search.csv", search_rows), ("split_metrics.csv", split_rows), ("module_metrics.csv", module_rows), ("pgqenn_graph_metrics.csv", pgqenn_rows), ("source_removal.csv", source_rows), ("seed_summary.csv", seed_rows)):
        write_csv(name, rows)
    result = {"dataset": dataset_name, "selected_hyperparameters": {"epochs": best[1], "max_clusters": best[2], "optimize_K_D": True, "adaptive_learning_rate": True}, "seeds": list(seeds), "training_status": "completed", "validation_status": "validation-selected", "test_status": "held-out", "claim_boundary": "finite deterministic tabular benchmark; not clinical deployment validation, financial deployment validation or formal theorem proof"}
    (output / "evaluation_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(math.isfinite(float(row["objective"])) for row in search_rows):
        raise RuntimeError("non-finite hyperparameter objective")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dataset", choices=("fraud", "breast-cancer"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--epochs", nargs="+", type=int, default=[10, 20, 40])
    parser.add_argument("--clusters", nargs="+", type=int, default=[24, 40, 64])
    args = parser.parse_args()
    report = run(source=args.source, dataset_name=args.dataset, output=args.output, seeds=tuple(args.seeds), epochs=tuple(args.epochs), clusters=tuple(args.clusters))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
