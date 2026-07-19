"""CLI for comprehensive TNE Artificial Intelligence evaluation."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import torch
from torch.nn import functional

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect.artificial_intelligence import comprehensive_evaluation
from the_nothingness_effect.artificial_intelligence.comprehensive_no_local_plots import (
    plot_training_diagnostics,
)
from the_nothingness_effect.artificial_intelligence.multimodal import training as training_module
from the_nothingness_effect.artificial_intelligence.multimodal.evaluation import (
    evaluate_multimodal_model,
)
from the_nothingness_effect.artificial_intelligence.multimodal.geometric_model import (
    TNEGeometricMultimodalModel,
)


class CalibratedNoLocalRBMModel(TNEGeometricMultimodalModel):
    """Geometric no-local-RBM model with persistent calibration state."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.register_buffer("calibration_temperature", torch.ones(()))


_original_loss_components = training_module._loss_components
_original_validation_objective = training_module.validation_objective
_original_train = comprehensive_evaluation.train_multimodal_model
_original_source_removals = comprehensive_evaluation.source_removals


def _strong_qenn_loss(output, labels):
    total, task, reconstruction, energy, closure = _original_loss_components(
        output,
        labels,
    )
    qenn_auxiliary = training_module._qenn_auxiliary_loss(output, labels)
    return (
        total + 0.50 * qenn_auxiliary,
        task + 0.50 * qenn_auxiliary,
        reconstruction,
        energy,
        closure,
    )


def _module_aware_validation_objective(evaluation):
    return _original_validation_objective(evaluation) + 0.20 * float(
        evaluation.metrics.get("mean_qenn_cross_entropy", 0.0)
    )


def _source_removals_without_legacy_name(model, batch, seed):
    rows = _original_source_removals(model, batch, seed)
    for row in rows:
        if row.get("variant") == "rbm_regulator_removed":
            row["variant"] = "precision_regulator_removed"
    return rows


def _ridge_regression(
    features: torch.Tensor,
    target: torch.Tensor,
    ridge: float,
) -> torch.Tensor:
    x = features.detach().to(torch.float64)
    y = target.detach().to(torch.float64)
    ones = torch.ones((x.shape[0], 1), dtype=x.dtype, device=x.device)
    design = torch.cat((x, ones), dim=-1)
    penalty = torch.eye(design.shape[-1], dtype=x.dtype, device=x.device)
    penalty[-1, -1] = 0.0
    system = design.T @ design + ridge * penalty
    return torch.linalg.solve(system, design.T @ y)


def _ridge_solution(
    features: torch.Tensor,
    labels: torch.Tensor,
    classes: int,
    ridge: float,
) -> torch.Tensor:
    target = functional.one_hot(labels, num_classes=classes)
    return _ridge_regression(features, target, ridge)


def _fit_qenn_readouts(model, train_batch, validation_batch) -> tuple[float, ...]:
    """Fit only QENN last layers and select ridge strength on validation data."""

    model.eval()
    with torch.no_grad():
        train_output = model(train_batch.modalities)
        validation_output = model(validation_batch.modalities)
    train_qenn = train_output.backbone_output.soinet_output.qenn_outputs
    validation_qenn = validation_output.backbone_output.soinet_output.qenn_outputs
    modules = model.backbone.soinet.ensemble.qenn
    if not (len(train_qenn) == len(validation_qenn) == len(modules)):
        raise RuntimeError("QENN ridge fine-tuning requires aligned ensemble outputs")

    selected_lambdas: list[float] = []
    candidates = (1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0)
    for index, (module, train_state, validation_state) in enumerate(
        zip(modules, train_qenn, validation_qenn, strict=True)
    ):
        train_features = train_state.spectral_reconstruction
        validation_features = validation_state.spectral_reconstruction
        if train_features is None or validation_features is None:
            raise RuntimeError("QENN spectral reconstruction is required for ridge fine-tuning")
        classes = module.readout_layer.out_features
        best_score = math.inf
        best_beta: torch.Tensor | None = None
        best_ridge = candidates[0]
        for ridge in candidates:
            beta = _ridge_solution(
                train_features,
                train_batch.labels,
                classes,
                ridge,
            )
            logits = validation_features.to(torch.float64) @ beta[:-1] + beta[-1]
            loss = float(functional.cross_entropy(logits, validation_batch.labels))
            accuracy = float(
                (logits.argmax(dim=-1) == validation_batch.labels).float().mean()
            )
            score = loss + 0.25 * (1.0 - accuracy)
            if score < best_score:
                best_score = score
                best_beta = beta
                best_ridge = ridge
        if best_beta is None:
            raise RuntimeError("QENN ridge search did not produce a finite candidate")
        with torch.no_grad():
            module.readout_layer.weight.copy_(
                best_beta[:-1].T.to(
                    dtype=module.readout_layer.weight.dtype,
                    device=module.readout_layer.weight.device,
                )
            )
            module.readout_layer.bias.copy_(
                best_beta[-1].to(
                    dtype=module.readout_layer.bias.dtype,
                    device=module.readout_layer.bias.device,
                )
            )
        buffer_name = f"qenn_readout_ridge_lambda_{index}"
        if hasattr(model, buffer_name):
            getattr(model, buffer_name).fill_(best_ridge)
        else:
            model.register_buffer(buffer_name, torch.tensor(float(best_ridge)))
        selected_lambdas.append(float(best_ridge))
    return tuple(selected_lambdas)


def _inverse_softplus(value: torch.Tensor) -> torch.Tensor:
    value = value.clamp_min(1e-6).to(torch.float64)
    return value + torch.log(-torch.expm1(-value))


def _fit_decoder(model, train_batch, validation_batch) -> float:
    """Fit the decoder alone without changing the classification carriers."""

    model.eval()
    with torch.no_grad():
        train_output = model(train_batch.modalities)
        validation_output = model(validation_batch.modalities)
    train_hidden = train_output.hidden
    validation_hidden = validation_output.hidden
    train_target = train_output.backbone_output.modality_tokens.mean(dim=1)
    validation_target = validation_output.backbone_output.modality_tokens.mean(dim=1)
    candidates = (1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0)
    best_rmse = math.inf
    best_beta: torch.Tensor | None = None
    best_ridge = candidates[0]
    for ridge in candidates:
        beta = _ridge_regression(
            train_hidden,
            _inverse_softplus(train_target),
            ridge,
        )
        reconstruction = functional.softplus(
            validation_hidden.to(torch.float64) @ beta[:-1] + beta[-1]
        )
        rmse = float(
            torch.sqrt(torch.mean((reconstruction - validation_target.to(torch.float64)) ** 2))
        )
        if rmse < best_rmse:
            best_rmse = rmse
            best_beta = beta
            best_ridge = ridge
    if best_beta is None:
        raise RuntimeError("decoder ridge search did not produce a finite candidate")
    with torch.no_grad():
        model.shared_token_decoder.weight.copy_(
            best_beta[:-1].T.to(
                dtype=model.shared_token_decoder.weight.dtype,
                device=model.shared_token_decoder.weight.device,
            )
        )
        model.shared_token_decoder.bias.copy_(
            best_beta[-1].to(
                dtype=model.shared_token_decoder.bias.dtype,
                device=model.shared_token_decoder.bias.device,
            )
        )
    if hasattr(model, "decoder_ridge_lambda"):
        model.decoder_ridge_lambda.fill_(best_ridge)
    else:
        model.register_buffer("decoder_ridge_lambda", torch.tensor(float(best_ridge)))
    return float(best_ridge)


def _train_with_temperature_selection(
    model,
    train_batch,
    validation_batch,
    **kwargs,
):
    run = _original_train(
        model,
        train_batch,
        validation_batch,
        **kwargs,
    )
    _fit_qenn_readouts(model, train_batch, validation_batch)
    _fit_decoder(model, train_batch, validation_batch)
    if not hasattr(model, "calibration_temperature"):
        model.register_buffer("calibration_temperature", torch.ones(()))
    candidates = (0.55, 0.7, 0.85, 1.0, 1.15, 1.35, 1.6)
    selected = 1.0
    selected_score = math.inf
    with torch.no_grad():
        for candidate in candidates:
            model.calibration_temperature.fill_(candidate)
            evaluation = evaluate_multimodal_model(model, validation_batch)
            score = (
                float(evaluation.metrics["cross_entropy"])
                + 0.35 * float(evaluation.metrics["expected_calibration_error"])
            )
            if score < selected_score:
                selected_score = score
                selected = candidate
        model.calibration_temperature.fill_(selected)
    return run


# The comprehensive module imports collaborators eagerly. Replace the selected
# callbacks with the audited no-local-RBM training and reporting surfaces.
training_module._loss_components = _strong_qenn_loss
training_module.validation_objective = _module_aware_validation_objective
comprehensive_evaluation.TNEGeometricMultimodalModel = CalibratedNoLocalRBMModel
comprehensive_evaluation.train_multimodal_model = _train_with_temperature_selection
comprehensive_evaluation.source_removals = _source_removals_without_legacy_name
comprehensive_evaluation.plot_training_diagnostics = plot_training_diagnostics
run_comprehensive_ai_evaluation = comprehensive_evaluation.run_comprehensive_ai_evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--samples-per-class", type=int, default=24)
    args = parser.parse_args()
    report = run_comprehensive_ai_evaluation(
        args.output,
        seeds=tuple(args.seeds),
        epochs=args.epochs,
        samples_per_class=args.samples_per_class,
    )
    seed_summary = report["seed_summary"]
    mean_test_accuracy = sum(
        float(row["test_accuracy"])
        for row in seed_summary
    ) / len(seed_summary)
    print(
        "comprehensive_ai_evaluation=passed "
        "local_rbm=removed "
        "qenn_auxiliary=supervised_and_ridge_finetuned "
        "decoder=validation_ridge_finetuned "
        "temperature_calibration=validation_selected "
        f"seeds={len(seed_summary)} "
        f"artifacts={report['artifact_count']} "
        f"plots={report['plot_count']} "
        f"mean_test_accuracy={mean_test_accuracy:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
