"""Tune every public TNE AI and global-RBM hyperparameter on validation data."""
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
    base_evaluate_multimodal_model,
)
from tools.run_tabular_ai_evaluation import _dataset, _objective  # noqa: E402
from the_nothingness_effect.artificial_intelligence.multimodal import training as training_module  # noqa: E402
from the_nothingness_effect.artificial_intelligence.multimodal.rbm import (  # noqa: E402
    GaussianBernoulliEnergyLayer,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.training_evaluation import (  # noqa: E402
    evaluate_pgqenn_graph_heads,
    reset_pgqenn_graph_evidence,
)


_ORIGINAL_TRAINING_LOSS = training_module._loss_components


def _global_rbm_weighted_loss(output, labels):
    total, task, reconstruction, energy, closure = _ORIGINAL_TRAINING_LOSS(output, labels)
    weight = float(output.metadata.get("global_rbm_loss_weight", 0.02))
    if not math.isfinite(weight) or weight < 0.0:
        raise RuntimeError("global RBM loss weight must be finite and non-negative")
    total = total + (weight - 0.02) * energy
    return total, task, reconstruction, energy, closure


training_module._loss_components = _global_rbm_weighted_loss


class TunableGlobalRBMLayer(GaussianBernoulliEnergyLayer):
    """Global RBM whose deterministic CD/Gibbs depth is validation-tunable."""

    def __init__(
        self,
        visible_dim: int,
        hidden_dim: int,
        *,
        weight_scale: float,
        configured_steps: int,
    ) -> None:
        super().__init__(visible_dim, hidden_dim, weight_scale=weight_scale)
        if configured_steps < 1:
            raise ValueError("global RBM steps must be positive")
        self.configured_steps = int(configured_steps)
        self.initial_weight_scale = float(weight_scale)

    def forward(self, visible, *, steps=1, stochastic=False, generator=None):
        del steps
        return super().forward(
            visible,
            steps=self.configured_steps,
            stochastic=stochastic,
            generator=generator,
        )


class TunableGlobalRBMModel(CalibratedNoLocalRBMModel):
    """Integrated TNE model with an explicitly tunable global RBM."""

    def __init__(
        self,
        *args,
        global_rbm_weight_scale: float = 0.02,
        global_rbm_steps: int = 1,
        global_rbm_loss_weight: float = 0.02,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if not math.isfinite(global_rbm_loss_weight) or global_rbm_loss_weight < 0.0:
            raise ValueError("global RBM loss weight must be finite and non-negative")
        visible_dim = int(self.global_energy.visible_dim)
        hidden_dim = int(self.global_energy.hidden_dim)
        self.global_energy = TunableGlobalRBMLayer(
            visible_dim,
            hidden_dim,
            weight_scale=global_rbm_weight_scale,
            configured_steps=global_rbm_steps,
        )
        self.global_rbm_loss_weight = float(global_rbm_loss_weight)

    def forward(self, modalities, *, tolerance=1e-5):
        output = super().forward(modalities, tolerance=tolerance)
        output.metadata.update(
            {
                "global_rbm_hidden_dim": int(self.global_energy.hidden_dim),
                "global_rbm_weight_scale": float(self.global_energy.initial_weight_scale),
                "global_rbm_steps": int(self.global_energy.configured_steps),
                "global_rbm_loss_weight": float(self.global_rbm_loss_weight),
            }
        )
        return output


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
    global_rbm_weight_scale: float = 0.02
    global_rbm_steps: int = 1
    global_rbm_loss_weight: float = 0.02
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
    ("global_rbm_weight_scale", (0.01, 0.02, 0.05)),
    ("global_rbm_steps", (1, 2, 4)),
    ("global_rbm_loss_weight", (0.005, 0.02, 0.08)),
    ("max_clusters", (24, 40, 64)),
    ("dropout", (0.0, 0.05, 0.15)),
    ("optimize_K_D", (False, True)),
    ("adaptive_learning_rate", (False, True)),
)


def build(config: Config) -> TunableGlobalRBMModel:
    return TunableGlobalRBMModel(
        hidden_dim=config.hidden_dim,
        output_dim=2,
        K_D=config.K_D,
        soi_scale=config.soi_scale,
        qenn_count=config.qenn_count,
        pgqenn_count=config.pgqenn_count,
        modality_count=3,
        axis_dim=config.axis_dim,
        global_rbm_hidden=config.global_rbm_hidden,
        global_rbm_weight_scale=config.global_rbm_weight_scale,
        global_rbm_steps=config.global_rbm_steps,
        global_rbm_loss_weight=config.global_rbm_loss_weight,
        max_clusters=config.max_clusters,
        dropout=config.dropout,
    )


def _flatten_parameters(module: torch.nn.Module) -> torch.Tensor:
    return torch.cat([parameter.detach().reshape(-1).cpu() for parameter in module.parameters()])


def train(config: Config, data, seed: int):
    torch.manual_seed(seed)
    model = build(config)
    initial_global_rbm = _flatten_parameters(model.global_energy)
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
    final_global_rbm = _flatten_parameters(model.global_energy)
    update_l2 = float(torch.linalg.vector_norm(final_global_rbm - initial_global_rbm))
    if not math.isfinite(update_l2) or update_l2 <= 0.0:
        raise RuntimeError("global RBM parameters did not receive a finite training update")
    model.register_buffer("global_rbm_parameter_update_l2", torch.tensor(update_l2))
    return model, run


def _finite(value: Any) -> bool:
    return value is not None and math.isfinite(float(value))


def _global_rbm_metrics(seed: int, split: str, evaluation) -> dict[str, Any]:
    state = evaluation.output.global_rbm_state
    if state is None:
        raise RuntimeError("global RBM state is required")
    hidden = state.hidden_probability
    entropy = -torch.mean(
        hidden * torch.log(hidden.clamp_min(1e-9))
        + (1.0 - hidden) * torch.log((1.0 - hidden).clamp_min(1e-9))
    )
    return {
        "seed": seed,
        "split": split,
        "hidden_dim": int(hidden.shape[-1]),
        "cd_steps": int(evaluation.output.metadata["global_rbm_steps"]),
        "initial_weight_scale": float(evaluation.output.metadata["global_rbm_weight_scale"]),
        "loss_weight": float(evaluation.output.metadata["global_rbm_loss_weight"]),
        "mean_free_energy": float(state.free_energy.mean()),
        "mean_negative_free_energy": float(state.negative_free_energy.mean()),
        "contrastive_divergence": float(state.contrastive_divergence),
        "reconstruction_rmse": float(state.reconstruction_residual),
        "mean_hidden_probability": float(hidden.mean()),
        "hidden_entropy": float(entropy),
        "parameter_update_l2": float(evaluation.output.metadata.get("global_rbm_parameter_update_l2", 0.0)),
    }


def _global_rbm_context_ablation(model, batch, seed: int) -> list[dict[str, Any]]:
    complete = base_evaluate_multimodal_model(model, batch)
    complete_probabilities = complete.output.observation.detach()
    weight = model.energy_projection.weight.detach().clone()
    try:
        with torch.no_grad():
            model.energy_projection.weight.zero_()
        removed = base_evaluate_multimodal_model(model, batch)
    finally:
        with torch.no_grad():
            model.energy_projection.weight.copy_(weight)
    delta = float(torch.mean(torch.abs(removed.output.observation - complete_probabilities)))
    return [
        {
            "seed": seed,
            "variant": "complete",
            "accuracy": complete.metrics["accuracy"],
            "macro_f1": complete.metrics["macro_f1"],
            "cross_entropy": complete.metrics["cross_entropy"],
            "global_rbm_reconstruction_rmse": complete.metrics["global_rbm_reconstruction_rmse"],
            "mean_probability_delta_from_complete": 0.0,
        },
        {
            "seed": seed,
            "variant": "global_rbm_context_removed",
            "accuracy": removed.metrics["accuracy"],
            "macro_f1": removed.metrics["macro_f1"],
            "cross_entropy": removed.metrics["cross_entropy"],
            "global_rbm_reconstruction_rmse": removed.metrics["global_rbm_reconstruction_rmse"],
            "mean_probability_delta_from_complete": delta,
        },
    ]


def score(model, data, seed: int) -> tuple[float, dict[str, Any], list[dict[str, Any]]]:
    evaluation = _evaluate_with_pgqenn_graph_metrics(model, data.validation)
    modules = _module_rows_with_pgqenn(seed, evaluation, data.validation.labels)
    qenn_accuracies = [
        float(row["accuracy"])
        for row in modules
        if row.get("module") == "QENN" and _finite(row.get("accuracy"))
    ]
    accuracies = qenn_accuracies + [
        float(evaluation.metrics["pgqenn_graph_accuracy"]),
        float(evaluation.metrics["accuracy"]),
    ]
    residuals = [
        math.tanh(abs(float(row["residual_l2"])))
        for row in modules
        if _finite(row.get("residual_l2"))
    ]
    state = evaluation.output.global_rbm_state
    if state is None:
        raise RuntimeError("global RBM state missing during validation")
    rbm_penalty = (
        0.15 * math.tanh(float(state.reconstruction_residual))
        + 0.05 * math.tanh(abs(float(state.contrastive_divergence)))
    )
    value = (
        _objective(evaluation.metrics)
        + 0.35 * (1.0 - min(accuracies))
        + 0.04 * sum(residuals) / max(1, len(residuals))
        + 0.10 * float(evaluation.metrics["pgqenn_graph_cross_entropy"])
        + rbm_penalty
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
            print(f"evaluating_config={key}", flush=True)
            model, run = train(config, data, seed)
            value, metrics, _ = score(model, data, seed)
            cache[key] = value, metrics, run
            print(f"validation_objective={value:.12g}", flush=True)
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
                rows.append(
                    {
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
                        "validation_global_rbm_rmse": metrics["global_rbm_reconstruction_rmse"],
                        "validation_global_rbm_free_energy": metrics["mean_global_rbm_free_energy"],
                        **asdict(candidate),
                    }
                )
            changed |= selected != current
            current = selected
            print(f"selected_parameter={parameter} selected_value={getattr(current, parameter)!r}", flush=True)
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


def _module_summary(module_rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for module in ("QENN", "PGQENN", "SOInets"):
        rows = [row for row in module_rows if row["module"] == module]
        accuracies = [float(row["accuracy"]) for row in rows if _finite(row.get("accuracy"))]
        macro_f1 = [float(row["macro_f1"]) for row in rows if _finite(row.get("macro_f1"))]
        if not accuracies or not macro_f1:
            raise RuntimeError(f"missing finite held-out metrics for {module}")
        summary[module] = {
            "mean_test_accuracy": sum(accuracies) / len(accuracies),
            "mean_test_macro_f1": sum(macro_f1) / len(macro_f1),
        }
    return summary


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
    global_rbm_rows: list[dict[str, Any]] = []
    global_rbm_ablation_rows: list[dict[str, Any]] = []
    for seed in seeds:
        data, report = _dataset(source, dataset_name, seed)
        model, training = train(selected, data, seed)
        evaluations = {
            split: _evaluate_with_pgqenn_graph_metrics(model, getattr(data, split))
            for split in ("train", "validation", "test")
        }
        for split, evaluation in evaluations.items():
            evaluation.output.metadata["global_rbm_parameter_update_l2"] = float(model.global_rbm_parameter_update_l2)
            split_rows.append({"seed": seed, "split": split, **evaluation.metrics})
            global_rbm_rows.append(_global_rbm_metrics(seed, split, evaluation))
        test = evaluations["test"]
        module_rows.extend(_module_rows_with_pgqenn(seed, test, data.test.labels))
        graph = evaluate_pgqenn_graph_heads(model, data.test)
        graph_rows.append({"seed": seed, **{key: value for key, value in graph["metrics"].items() if key != "confusion_matrix"}})
        source_rows.extend(_source_removals_without_legacy_name(model, data.test, seed))
        global_rbm_ablation_rows.extend(_global_rbm_context_ablation(model, data.test, seed))
        seed_rows.append(
            {
                "seed": seed,
                "best_epoch": training.best_epoch,
                "best_validation_objective": training.best_validation_objective,
                "test_accuracy": test.metrics["accuracy"],
                "test_macro_f1": test.metrics["macro_f1"],
                "test_cross_entropy": test.metrics["cross_entropy"],
                "test_ece": test.metrics["expected_calibration_error"],
                "global_rbm_parameter_update_l2": float(model.global_rbm_parameter_update_l2),
                "global_rbm_test_reconstruction_rmse": test.metrics["global_rbm_reconstruction_rmse"],
                "global_rbm_test_free_energy": test.metrics["mean_global_rbm_free_energy"],
                **report,
            }
        )
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "selected_hyperparameters": asdict(selected),
                "seed": seed,
                "best_epoch": training.best_epoch,
                "best_validation_objective": training.best_validation_objective,
                "global_rbm_parameter_update_l2": float(model.global_rbm_parameter_update_l2),
            },
            checkpoints / f"seed_{seed}_best.pt",
        )

    for name, rows in (
        ("hyperparameter_search.csv", search_rows),
        ("split_metrics.csv", split_rows),
        ("module_metrics.csv", module_rows),
        ("pgqenn_graph_metrics.csv", graph_rows),
        ("source_removal.csv", source_rows),
        ("seed_summary.csv", seed_rows),
        ("global_rbm_metrics.csv", global_rbm_rows),
        ("global_rbm_source_removal.csv", global_rbm_ablation_rows),
    ):
        write_csv(output / name, rows)

    test_rows = [row for row in split_rows if row["split"] == "test"]
    rbm_test_rows = [row for row in global_rbm_rows if row["split"] == "test"]
    rbm_removed = [row for row in global_rbm_ablation_rows if row["variant"] == "global_rbm_context_removed"]
    summary = {
        "schema_version": "1.1",
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
        "modules": _module_summary(module_rows),
        "global_rbm": {
            "training_mode": "joint AdamW through explicit global energy loss",
            "mean_parameter_update_l2": sum(float(row["parameter_update_l2"]) for row in rbm_test_rows) / len(rbm_test_rows),
            "mean_test_reconstruction_rmse": sum(float(row["reconstruction_rmse"]) for row in rbm_test_rows) / len(rbm_test_rows),
            "mean_test_contrastive_divergence": sum(float(row["contrastive_divergence"]) for row in rbm_test_rows) / len(rbm_test_rows),
            "mean_test_free_energy": sum(float(row["mean_free_energy"]) for row in rbm_test_rows) / len(rbm_test_rows),
            "mean_context_removal_probability_delta": sum(float(row["mean_probability_delta_from_complete"]) for row in rbm_removed) / len(rbm_removed),
        },
        "nested_validation_tuning": [
            "QENN ridge",
            "PGQENN graph ridge",
            "main-task ridge",
            "decoder ridge",
            "temperature",
            "dynamic K_D/SOI",
            "global RBM hidden size/weight scale/CD steps/loss weight",
        ],
        "split_policy": "training-only preprocessing; validation-only selection; held-out test used after model selection",
        "search_ingestion": ingestion,
        "claim_boundary": "finite tabular benchmark; not clinical/financial deployment validation or formal theorem proof",
    }
    (output / "evaluation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = {
        "schema_version": "1.1",
        "files": [
            {"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": digest(path)}
            for path in files
        ],
    }
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
