"""Run the complete TNE AI search with deterministic multi-fidelity screening."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
import math
from typing import Any

import torch

import tools.run_full_ai_hyperparameter_evaluation as base
from the_nothingness_effect.artificial_intelligence.multimodal.data import (
    MultimodalBatch,
    MultimodalDataset,
)

SCREENING_EPOCHS = 6
TRAIN_PER_CLASS = 384
VALIDATION_PER_CLASS = 160
ORDERED_SPACE = tuple(item for item in base.SPACE if item[0] != "epochs") + (
    next(item for item in base.SPACE if item[0] == "epochs"),
)


def _bounded_batch(batch: MultimodalBatch, per_class: int) -> MultimodalBatch:
    indexes: list[torch.Tensor] = []
    for label in torch.unique(batch.labels, sorted=True):
        candidates = torch.nonzero(batch.labels == label, as_tuple=False).reshape(-1)
        indexes.append(candidates[: min(per_class, candidates.numel())])
    selected = torch.cat(indexes).sort().values
    modalities = {name: values[selected] for name, values in batch.modalities.items()}
    return MultimodalBatch(modalities, batch.labels[selected]).validate()


def _bounded_dataset(data: MultimodalDataset) -> MultimodalDataset:
    return MultimodalDataset(
        _bounded_batch(data.train, TRAIN_PER_CLASS),
        _bounded_batch(data.validation, VALIDATION_PER_CLASS),
        data.test,
        data.class_names,
    )


def search(
    data: MultimodalDataset,
    seed: int,
    passes: int,
) -> tuple[base.Config, list[dict[str, Any]]]:
    screening_data = _bounded_dataset(data)
    current = base.Config()
    rows: list[dict[str, Any]] = []
    cache: dict[str, tuple[float, dict[str, Any], Any]] = {}

    def evaluate(config: base.Config, parameter: str):
        trial = config if parameter == "epochs" else replace(
            config,
            epochs=min(config.epochs, SCREENING_EPOCHS),
        )
        key = json.dumps(asdict(trial), sort_keys=True)
        if key not in cache:
            print(
                "evaluating_screening_config=" + key,
                f"parameter={parameter}",
                flush=True,
            )
            model, training = base.train(trial, screening_data, seed)
            objective, metrics, _ = base.score(model, screening_data, seed)
            cache[key] = objective, metrics, training
            print(f"screening_validation_objective={objective:.12g}", flush=True)
        return cache[key], trial

    for pass_index in range(passes):
        changed = False
        for parameter, values in ORDERED_SPACE:
            candidates = []
            for value in values:
                candidate = replace(current, **{parameter: value})
                (objective, metrics, training), trial = evaluate(candidate, parameter)
                candidates.append(
                    (
                        objective,
                        json.dumps(asdict(candidate), sort_keys=True),
                        candidate,
                        trial,
                        metrics,
                        training,
                    )
                )
            candidates.sort(key=lambda item: (item[0], item[1]))
            selected = candidates[0][2]
            for objective, _, candidate, trial, metrics, training in candidates:
                rows.append(
                    {
                        "pass": pass_index,
                        "parameter": parameter,
                        "candidate": getattr(candidate, parameter),
                        "selected": candidate == selected,
                        "objective": objective,
                        "screening_epochs": trial.epochs,
                        "screening_train_rows": screening_data.train.labels.numel(),
                        "screening_validation_rows": screening_data.validation.labels.numel(),
                        "best_epoch": training.best_epoch,
                        "validation_accuracy": metrics["accuracy"],
                        "validation_macro_f1": metrics["macro_f1"],
                        "validation_cross_entropy": metrics["cross_entropy"],
                        "validation_ece": metrics["expected_calibration_error"],
                        "validation_global_rbm_rmse": metrics[
                            "global_rbm_reconstruction_rmse"
                        ],
                        "validation_global_rbm_free_energy": metrics[
                            "mean_global_rbm_free_energy"
                        ],
                        **asdict(candidate),
                    }
                )
            changed |= selected != current
            current = selected
            print(
                f"selected_parameter={parameter} "
                f"selected_value={getattr(current, parameter)!r}",
                flush=True,
            )
        if not changed:
            break
    if not all(math.isfinite(float(row["objective"])) for row in rows):
        raise RuntimeError("non-finite multi-fidelity search objective")
    return current, rows


base.search = search

if __name__ == "__main__":
    raise SystemExit(base.main())
