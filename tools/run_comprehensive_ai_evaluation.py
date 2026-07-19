"""CLI for comprehensive TNE Artificial Intelligence evaluation."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import torch

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect.artificial_intelligence import comprehensive_evaluation
from the_nothingness_effect.artificial_intelligence.comprehensive_no_local_plots import (
    plot_training_diagnostics,
)
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


_original_train = comprehensive_evaluation.train_multimodal_model


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
                + 0.35
                * float(evaluation.metrics["expected_calibration_error"])
            )
            if score < selected_score:
                selected_score = score
                selected = candidate
        model.calibration_temperature.fill_(selected)
    return run


# The comprehensive module imports its collaborators eagerly.  Replace only the
# geometric constructor, training callback and training-diagnostic callback.
comprehensive_evaluation.TNEGeometricMultimodalModel = CalibratedNoLocalRBMModel
comprehensive_evaluation.train_multimodal_model = _train_with_temperature_selection
comprehensive_evaluation.plot_training_diagnostics = plot_training_diagnostics
run_comprehensive_ai_evaluation = (
    comprehensive_evaluation.run_comprehensive_ai_evaluation
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[0, 1, 2],
    )
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument(
        "--samples-per-class",
        type=int,
        default=24,
    )
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
        "temperature_calibration=validation_selected "
        f"seeds={len(seed_summary)} "
        f"artifacts={report['artifact_count']} "
        f"plots={report['plot_count']} "
        f"mean_test_accuracy={mean_test_accuracy:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
