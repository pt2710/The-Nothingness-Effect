"""Fail-closed verification of bounded real-data TNE AI performance evidence."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any

import torch


REQUIRED_DATASETS = ("cifar-10", "cifar-100")
REQUIRED_READOUT_BUFFERS = (
    "main_task_ridge_lambda",
    "main_task_validation_accuracy",
    "main_task_validation_cross_entropy",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"expected non-empty CSV evidence: {path}")
    return rows


def _finite(value: object, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError(f"non-finite performance value for {label}: {value}")
    return result


def verify_real_ai_performance(root: str | Path) -> dict[str, Any]:
    output = Path(root)
    dataset_reports: list[dict[str, Any]] = []
    for dataset_name in REQUIRED_DATASETS:
        dataset_root = output / dataset_name
        summary = _load_json(dataset_root / "evaluation_summary.json")
        module_rows = _load_csv(dataset_root / "module_metrics.csv")
        seed_rows = _load_csv(dataset_root / "seed_summary.csv")
        ingestion = json.loads(
            (dataset_root / "cifar_ingestion_reports.json").read_text(
                encoding="utf-8"
            )
        )
        if not isinstance(ingestion, list) or not ingestion:
            raise RuntimeError(f"missing ingestion reports for {dataset_name}")
        if not all(bool(row.get("leakage_free")) for row in ingestion):
            raise RuntimeError(f"split leakage detected for {dataset_name}")

        classes = int(summary.get("classes", 0))
        if classes < 2:
            raise RuntimeError(f"invalid class domain for {dataset_name}: {classes}")
        chance = 1.0 / classes
        main_accuracy = _finite(
            summary["means"]["mean_test_accuracy"],
            f"{dataset_name} integrated test accuracy",
        )
        pgqenn_accuracy = _finite(
            summary["means"]["mean_pgqenn_graph_accuracy"],
            f"{dataset_name} PGQENN graph accuracy",
        )
        grouped: dict[str, list[float]] = {}
        for row in module_rows:
            module = str(row.get("module", ""))
            if module in {"QENN", "PGQENN", "SOInets"}:
                grouped.setdefault(module, []).append(
                    _finite(row["accuracy"], f"{dataset_name} {module} accuracy")
                )
        if set(grouped) != {"QENN", "PGQENN", "SOInets"}:
            raise RuntimeError(
                f"missing module accuracy evidence for {dataset_name}: {sorted(grouped)}"
            )
        module_means = {module: mean(values) for module, values in grouped.items()}
        if abs(module_means["SOInets"] - main_accuracy) > 1e-7:
            raise RuntimeError(
                f"SOInets module and summary accuracy disagree for {dataset_name}"
            )
        if abs(module_means["PGQENN"] - pgqenn_accuracy) > 1e-7:
            raise RuntimeError(
                f"PGQENN module and summary accuracy disagree for {dataset_name}"
            )
        for module in ("QENN", "PGQENN", "SOInets"):
            if module_means[module] <= chance + 1e-9:
                raise RuntimeError(
                    f"{dataset_name} {module} remained at or below chance: "
                    f"{module_means[module]:.6f} <= {chance:.6f}"
                )

        expected_seeds = {int(seed) for seed in summary.get("seeds", [])}
        observed_seeds = {int(row["seed"]) for row in seed_rows}
        if not expected_seeds or observed_seeds != expected_seeds:
            raise RuntimeError(
                f"seed evidence mismatch for {dataset_name}: "
                f"{sorted(observed_seeds)} != {sorted(expected_seeds)}"
            )
        validation_accuracies: list[float] = []
        selected_lambdas: list[float] = []
        for seed in sorted(expected_seeds):
            checkpoint_path = (
                dataset_root / "checkpoints" / f"{dataset_name}-seed-{seed}.pt"
            )
            checkpoint = torch.load(
                checkpoint_path,
                map_location="cpu",
                weights_only=False,
            )
            state_dict = checkpoint.get("state_dict")
            if not isinstance(state_dict, dict):
                raise RuntimeError(f"checkpoint omitted state_dict: {checkpoint_path}")
            for key in REQUIRED_READOUT_BUFFERS:
                if key not in state_dict:
                    raise RuntimeError(
                        f"checkpoint omitted {key}: {checkpoint_path}"
                    )
                if not torch.isfinite(torch.as_tensor(state_dict[key])).all():
                    raise RuntimeError(
                        f"checkpoint contains non-finite {key}: {checkpoint_path}"
                    )
            selected_lambdas.append(float(state_dict["main_task_ridge_lambda"]))
            validation_accuracies.append(
                float(state_dict["main_task_validation_accuracy"])
            )
        if any(value <= 0.0 for value in selected_lambdas):
            raise RuntimeError(f"non-positive ridge lambda for {dataset_name}")
        if any(value < chance - 1e-9 for value in validation_accuracies):
            raise RuntimeError(
                f"validation-selected readout fell below chance for {dataset_name}"
            )

        dataset_reports.append(
            {
                "dataset": dataset_name,
                "classes": classes,
                "chance_accuracy": chance,
                "mean_test_accuracy": main_accuracy,
                "mean_test_margin_over_chance": main_accuracy - chance,
                "module_mean_accuracy": module_means,
                "validation_accuracy_by_seed": validation_accuracies,
                "selected_main_task_ridge_lambda_by_seed": selected_lambdas,
                "leakage_free": True,
                "performance_status": "nondegenerate_above_chance",
            }
        )

    report = {
        "schema_version": "1.0",
        "verification_status": "passed",
        "datasets": dataset_reports,
        "gate": (
            "QENN, PGQENN and integrated SOInets mean held-out accuracy must each "
            "exceed balanced-class chance; every checkpoint must contain finite "
            "validation-selected main-readout calibration buffers"
        ),
        "claim_boundary": (
            "bounded multi-seed non-degeneracy verification on selected CIFAR "
            "classes; not unrestricted benchmark certification"
        ),
    }
    (output / "performance_verification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    report = verify_real_ai_performance(args.root)
    print(
        "real_ai_performance_verification=passed "
        + " ".join(
            f"{row['dataset']}={row['mean_test_accuracy']:.6f}"
            for row in report["datasets"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
