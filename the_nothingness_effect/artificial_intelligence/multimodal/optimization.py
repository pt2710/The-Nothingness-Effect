"""Validation-driven dynamic-K_D search for the trainable multimodal model."""

from __future__ import annotations

from dataclasses import dataclass
import math

from the_nothingness_effect.artificial_intelligence.shared.dynamic_kd import (
    dynamic_kd_state,
    set_dynamic_kd,
)
from the_nothingness_effect.artificial_intelligence.shared.dynamic_soi import (
    dynamic_soi_state,
    set_dynamic_soi,
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
    soi_scale: float
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
    previous_soi_scale: float
    selected_soi_scale: float
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
    """Deterministic coordinate search over positive K_D and SOI gain.

    The historical class name remains a compatibility surface.  The canonical
    search now evaluates the joint Elastic/SOI validation landscape while
    preserving DFI similarity invariance.
    """

    def __init__(
        self,
        *,
        lower: float = 0.25,
        upper: float = 4.0,
        scale_factors: tuple[float, ...] = (0.72, 1.0, 1.4),
        soi_lower: float = 0.25,
        soi_upper: float = 4.0,
        soi_scale_factors: tuple[float, ...] = (0.8, 1.0, 1.25),
    ) -> None:
        if not (math.isfinite(lower) and math.isfinite(upper) and 0.0 < lower < upper):
            raise ValueError("dynamic K_D bounds must be finite, positive and ordered")
        if not scale_factors or any(
            not math.isfinite(value) or value <= 0.0 for value in scale_factors
        ):
            raise ValueError("dynamic K_D scale factors must be finite and positive")
        if not (
            math.isfinite(soi_lower)
            and math.isfinite(soi_upper)
            and 0.0 < soi_lower < soi_upper
        ):
            raise ValueError("dynamic SOI bounds must be finite, positive and ordered")
        if not soi_scale_factors or any(
            not math.isfinite(value) or value <= 0.0
            for value in soi_scale_factors
        ):
            raise ValueError("dynamic SOI scale factors must be finite and positive")
        self.lower = float(lower)
        self.upper = float(upper)
        self.scale_factors = tuple(float(value) for value in scale_factors)
        self.soi_lower = float(soi_lower)
        self.soi_upper = float(soi_upper)
        self.soi_scale_factors = tuple(
            float(value) for value in soi_scale_factors
        )
        self._probes: list[KDProbe] = []
        self._selections: list[KDSelection] = []

    @property
    def probes(self) -> tuple[KDProbe, ...]:
        return tuple(self._probes)

    @property
    def selections(self) -> tuple[KDSelection, ...]:
        return tuple(self._selections)

    @staticmethod
    def _candidates(
        current: float,
        lower: float,
        upper: float,
        factors: tuple[float, ...],
    ) -> tuple[float, ...]:
        candidates = {
            round(min(upper, max(lower, current * factor)), 12)
            for factor in factors
        }
        candidates.add(round(current, 12))
        return tuple(sorted(candidates))

    @staticmethod
    def _probe(
        model: TNETrainableMultimodalModel,
        validation_batch: MultimodalBatch,
        *,
        epoch: int,
        K_D: float,
        soi_scale: float,
    ) -> KDProbe:
        set_dynamic_kd(model, K_D)
        set_dynamic_soi(model, soi_scale)
        try:
            evaluation = evaluate_multimodal_model(model, validation_batch)
            bounded_closure = sum(
                math.tanh(abs(value)) for value in evaluation.residuals.values()
            ) / max(1, len(evaluation.residuals))
            return KDProbe(
                epoch=epoch,
                K_D=K_D,
                soi_scale=soi_scale,
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
            return KDProbe(
                epoch,
                K_D,
                soi_scale,
                None,
                None,
                None,
                None,
                None,
                None,
                "obstructed",
                str(exc),
            )

    def select(
        self,
        model: TNETrainableMultimodalModel,
        validation_batch: MultimodalBatch,
        *,
        epoch: int,
    ) -> KDSelection:
        validation_batch.validate()
        previous = dynamic_kd_state(model).value
        previous_soi = dynamic_soi_state(model).value
        kd_probes = [
            self._probe(
                model,
                validation_batch,
                epoch=epoch,
                K_D=candidate,
                soi_scale=previous_soi,
            )
            for candidate in self._candidates(
                previous, self.lower, self.upper, self.scale_factors
            )
        ]
        valid_kd = tuple(
            probe for probe in kd_probes if probe.objective is not None
        )
        if not valid_kd:
            set_dynamic_kd(model, previous)
            set_dynamic_soi(model, previous_soi)
            raise AIObstructionError("all dynamic K_D candidates were obstructed")
        selected_kd = min(
            valid_kd,
            key=lambda probe: (float(probe.objective), probe.K_D),
        )
        soi_probes = [
            self._probe(
                model,
                validation_batch,
                epoch=epoch,
                K_D=selected_kd.K_D,
                soi_scale=candidate,
            )
            for candidate in self._candidates(
                previous_soi,
                self.soi_lower,
                self.soi_upper,
                self.soi_scale_factors,
            )
        ]
        valid_soi = tuple(
            probe for probe in soi_probes if probe.objective is not None
        )
        if not valid_soi:
            set_dynamic_kd(model, previous)
            set_dynamic_soi(model, previous_soi)
            raise AIObstructionError("all dynamic SOI candidates were obstructed")
        selected = min(
            valid_soi,
            key=lambda probe: (
                float(probe.objective),
                probe.soi_scale,
                probe.K_D,
            ),
        )
        previous_probe = min(
            valid_kd,
            key=lambda probe: (
                abs(probe.K_D - previous)
                + abs(probe.soi_scale - previous_soi)
            ),
        )
        set_dynamic_kd(model, selected.K_D)
        set_dynamic_soi(model, selected.soi_scale)
        selection = KDSelection(
            epoch=epoch,
            previous_K_D=previous,
            selected_K_D=selected.K_D,
            previous_soi_scale=previous_soi,
            selected_soi_scale=selected.soi_scale,
            previous_objective=float(previous_probe.objective),
            selected_objective=float(selected.objective),
            improvement=float(previous_probe.objective) - float(selected.objective),
            probes=tuple((*kd_probes, *soi_probes)),
        )
        self._probes.extend((*kd_probes, *soi_probes))
        self._selections.append(selection)
        return selection


# Explicit canonical name; the old name is retained for callers and manifests.
DynamicKDSOISearch = DynamicKDSearch
