"""Validation-driven dynamic-K_D search for the trainable multimodal model."""

from __future__ import annotations

from dataclasses import dataclass
import math

from the_nothingness_effect.artificial_intelligence.shared.dynamic_kd import (
    dynamic_kd_state,
    set_dynamic_kd,
)
from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
)

from .data import MultimodalBatch
from .evaluation import MultimodalEvaluation, evaluate_multimodal_model
from .model import TNETrainableMultimodalModel


@dataclass(frozen=True)
class KDProbe:
    epoch: int
    K_D: float
    objective: float | None
    cross_entropy: float | None
    reconstruction_rmse: float | None
    brier_score: float | None
    calibration_error: float | None
    bounded_closure_penalty: float | None
    status: str
    obstruction: str = ""


@dataclass(frozen=True)
class KDSelection:
    epoch: int
    previous_K_D: float
    selected_K_D: float
    previous_objective: float
    selected_objective: float
    improvement: float
    probes: tuple[KDProbe, ...]


def validation_objective(evaluation: MultimodalEvaluation) -> float:
    """Composite validation objective with task, reconstruction and closure terms."""

    metrics = evaluation.metrics
    bounded_closure = sum(
        math.tanh(abs(value)) for value in evaluation.residuals.values()
    ) / max(1, len(evaluation.residuals))
    objective = (
        metrics["cross_entropy"]
        + 0.25 * metrics["mean_reconstruction_rmse"]
        + 0.10 * metrics["brier_score"]
        + 0.05 * metrics["expected_calibration_error"]
        + 0.02 * bounded_closure
    )
    if not math.isfinite(objective):
        raise AIObstructionError("multimodal validation objective became non-finite")
    return float(objective)


class DynamicKDSearch:
    """Greedy, deterministic local search over the exact positive K_D domain."""

    def __init__(
        self,
        *,
        lower: float = 0.25,
        upper: float = 4.0,
        scale_factors: tuple[float, ...] = (0.72, 1.0, 1.4),
    ) -> None:
        if not (math.isfinite(lower) and math.isfinite(upper) and 0.0 < lower < upper):
            raise ValueError("dynamic K_D bounds must be finite, positive and ordered")
        if not scale_factors or any(
            not math.isfinite(value) or value <= 0.0 for value in scale_factors
        ):
            raise ValueError("dynamic K_D scale factors must be finite and positive")
        self.lower = float(lower)
        self.upper = float(upper)
        self.scale_factors = tuple(float(value) for value in scale_factors)
        self._probes: list[KDProbe] = []
        self._selections: list[KDSelection] = []

    @property
    def probes(self) -> tuple[KDProbe, ...]:
        return tuple(self._probes)

    @property
    def selections(self) -> tuple[KDSelection, ...]:
        return tuple(self._selections)

    def _candidates(self, current: float) -> tuple[float, ...]:
        candidates = {
            round(min(self.upper, max(self.lower, current * factor)), 12)
            for factor in self.scale_factors
        }
        candidates.add(round(current, 12))
        return tuple(sorted(candidates))

    def select(
        self,
        model: TNETrainableMultimodalModel,
        validation_batch: MultimodalBatch,
        *,
        epoch: int,
    ) -> KDSelection:
        validation_batch.validate()
        previous = dynamic_kd_state(model).value
        probes: list[KDProbe] = []
        for candidate in self._candidates(previous):
            set_dynamic_kd(model, candidate)
            try:
                evaluation = evaluate_multimodal_model(model, validation_batch)
                bounded_closure = sum(
                    math.tanh(abs(value)) for value in evaluation.residuals.values()
                ) / max(1, len(evaluation.residuals))
                probe = KDProbe(
                    epoch=epoch,
                    K_D=candidate,
                    objective=validation_objective(evaluation),
                    cross_entropy=evaluation.metrics["cross_entropy"],
                    reconstruction_rmse=evaluation.metrics[
                        "mean_reconstruction_rmse"
                    ],
                    brier_score=evaluation.metrics["brier_score"],
                    calibration_error=evaluation.metrics[
                        "expected_calibration_error"
                    ],
                    bounded_closure_penalty=bounded_closure,
                    status="evaluated",
                )
            except AIObstructionError as exc:
                probe = KDProbe(
                    epoch, candidate, None, None, None, None, None, None,
                    "obstructed", str(exc),
                )
            probes.append(probe)
        valid = tuple(probe for probe in probes if probe.objective is not None)
        if not valid:
            set_dynamic_kd(model, previous)
            raise AIObstructionError("all dynamic K_D candidates were obstructed")
        selected = min(valid, key=lambda probe: (float(probe.objective), probe.K_D))
        previous_probe = min(valid, key=lambda probe: abs(probe.K_D - previous))
        set_dynamic_kd(model, selected.K_D)
        selection = KDSelection(
            epoch=epoch,
            previous_K_D=previous,
            selected_K_D=selected.K_D,
            previous_objective=float(previous_probe.objective),
            selected_objective=float(selected.objective),
            improvement=float(previous_probe.objective) - float(selected.objective),
            probes=tuple(probes),
        )
        self._probes.extend(probes)
        self._selections.append(selection)
        return selection
