"""Exact finite spatial closure for the pDFI third-order functional."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
    SourceRemovalResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.closure_contracts import (
    _functional,
    _functional_reference,
    _involutive_permutation,
)

from . import contracts as _base


SOURCE_IDS = tuple(str(item) for item in _base.B_IDS)
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "parity_adapted_dynamic_fluctuation_index/closure_contracts.py"
)


@dataclass(frozen=True)
class ExactSpatialParityInput:
    source_energy_fields_1b: Mapping[str, np.ndarray]
    source_energy_fields_2b: Mapping[str, np.ndarray]
    source_weights_1b: Mapping[str, float]
    source_weights_2b: Mapping[str, float]
    spatial_reflection: tuple[int, ...]
    source_exchange: tuple[int, ...] = (0, 1, 2)
    gradient_weight: float = 1.0
    boundary_weight: float = 1.0
    grid_spacing: float = 1.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ExactSpatialParityClosure:
    source_fields_1b: np.ndarray
    source_fields_2b: np.ndarray
    transformed_source_fields_2b: np.ndarray
    defect_potential_1b: np.ndarray
    defect_potential_2b: np.ndarray
    volume_energy_1b: float
    gradient_energy_1b: float
    boundary_energy_1b: float
    spatial_energy_1b: float
    volume_energy_2b: float
    gradient_energy_2b: float
    boundary_energy_2b: float
    spatial_energy_2b: float
    exchange_involution_residual: float
    joint_energy: float
    coercive_lower_bound_1b: float
    coercive_lower_bound_2b: float
    coercivity_margin_1b: float
    coercivity_margin_2b: float
    reference_residual_1b: float
    reference_residual_2b: float
    reference_residual_joint: float
    closure_status: str


def _legacy_exact_input(value: _base.ParityDFIInput) -> ExactSpatialParityInput:
    trajectory = np.asarray(value.trajectory)
    if trajectory.ndim != 1 or trajectory.size < 3:
        raise DomainViolationError("pDFI spatial closure requires at least three trajectory samples")
    ensure_finite(trajectory, name="pDFI trajectory")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("pDFI tolerance must be finite and non-negative")

    transport = _base.transport_operator(value)
    predictive = _base.predictability_observation_operator(value)
    elastic = _base.elastic_completeness_operator(value)
    defects = {
        SOURCE_IDS[0]: float(np.linalg.norm(transport.commutator_residual)) ** 2,
        SOURCE_IDS[1]: float(np.linalg.norm(predictive.tracking_residual)) ** 2,
        SOURCE_IDS[2]: float(abs(elastic.calibration_residual)) ** 2,
    }
    fields = {
        source: np.full(trajectory.size, defect, dtype=float)
        for source, defect in defects.items()
    }
    weights = {source: 1.0 for source in SOURCE_IDS}
    return ExactSpatialParityInput(
        source_energy_fields_1b=fields,
        source_energy_fields_2b={source: field.copy() for source, field in fields.items()},
        source_weights_1b=weights,
        source_weights_2b=dict(weights),
        spatial_reflection=tuple(reversed(range(trajectory.size))),
        source_exchange=(0, 1, 2),
        tolerance=value.tolerance,
    )


def _exact_input(value: ExactSpatialParityInput | _base.ParityDFIInput) -> ExactSpatialParityInput:
    if isinstance(value, ExactSpatialParityInput):
        return value
    if isinstance(value, _base.ParityDFIInput):
        return _legacy_exact_input(value)
    raise DomainViolationError("pDFI C01 requires ExactSpatialParityInput or ParityDFIInput")


def _matrix(fields: Mapping[str, np.ndarray], *, label: str) -> np.ndarray:
    if set(fields) != set(SOURCE_IDS):
        missing = sorted(set(SOURCE_IDS) - set(fields))
        extra = sorted(set(fields) - set(SOURCE_IDS))
        raise DomainViolationError(f"{label} source mismatch; missing={missing}, extra={extra}")
    arrays = tuple(np.asarray(fields[source], dtype=float) for source in SOURCE_IDS)
    if any(array.ndim != 1 or array.size < 2 for array in arrays):
        raise DomainViolationError(f"{label} fields must be one-dimensional with at least two samples")
    if len({array.shape for array in arrays}) != 1:
        raise DomainViolationError(f"{label} fields must share one spatial shape")
    matrix = np.stack(arrays, axis=0)
    ensure_finite(matrix, name=label)
    if np.any(matrix < 0.0):
        raise DomainViolationError(f"{label} source energies must be nonnegative")
    return matrix


def _weights(weights: Mapping[str, float], *, label: str) -> np.ndarray:
    if set(weights) != set(SOURCE_IDS):
        missing = sorted(set(SOURCE_IDS) - set(weights))
        extra = sorted(set(weights) - set(SOURCE_IDS))
        raise DomainViolationError(f"{label} weight mismatch; missing={missing}, extra={extra}")
    result = np.asarray([weights[source] for source in SOURCE_IDS], dtype=float)
    ensure_finite(result, name=label)
    if np.any(result <= 0.0):
        raise DomainViolationError(f"{label} weights must be strictly positive")
    return result


def spatial_parity_closure_operator(
    value: ExactSpatialParityInput | _base.ParityDFIInput,
) -> ExactSpatialParityClosure:
    source = _exact_input(value)
    for name, scalar in (
        ("gradient_weight", source.gradient_weight),
        ("boundary_weight", source.boundary_weight),
        ("grid_spacing", source.grid_spacing),
    ):
        if not np.isfinite(scalar) or scalar <= 0.0:
            raise DomainViolationError(f"{name} must be finite and strictly positive")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")

    fields_1b = _matrix(source.source_energy_fields_1b, label="pDFI 1B")
    fields_2b = _matrix(source.source_energy_fields_2b, label="pDFI 2B")
    if fields_1b.shape != fields_2b.shape:
        raise DomainViolationError("pDFI 1B and 2B fields must share one domain")
    weights_1b = _weights(source.source_weights_1b, label="pDFI 1B")
    weights_2b = _weights(source.source_weights_2b, label="pDFI 2B")
    reflection = _involutive_permutation(
        source.spatial_reflection,
        fields_1b.shape[1],
        label="pDFI spatial_reflection",
    )
    exchange = _involutive_permutation(
        source.source_exchange,
        len(SOURCE_IDS),
        label="pDFI source_exchange",
    )

    transformed_2b = fields_2b[exchange][:, reflection]
    transformed_weights_2b = weights_2b[exchange]
    twice = transformed_2b[exchange][:, reflection]
    involution = float(np.linalg.norm(twice - fields_2b))

    potential_1b, volume_1b, gradient_1b, boundary_1b, energy_1b = _functional(
        fields_1b,
        weights_1b,
        spacing=source.grid_spacing,
        gradient_weight=source.gradient_weight,
        boundary_weight=source.boundary_weight,
    )
    potential_2b, volume_2b, gradient_2b, boundary_2b, energy_2b = _functional(
        transformed_2b,
        transformed_weights_2b,
        spacing=source.grid_spacing,
        gradient_weight=source.gradient_weight,
        boundary_weight=source.boundary_weight,
    )
    joint = float(energy_1b + energy_2b + involution * involution)
    lower_1b = float(np.min(weights_1b) * source.grid_spacing * np.sum(fields_1b))
    lower_2b = float(
        np.min(transformed_weights_2b)
        * source.grid_spacing
        * np.sum(transformed_2b)
    )
    margin_1b = float(energy_1b - lower_1b)
    margin_2b = float(energy_2b - lower_2b)

    reference_1b = _functional_reference(
        fields_1b,
        weights_1b,
        spacing=source.grid_spacing,
        gradient_weight=source.gradient_weight,
        boundary_weight=source.boundary_weight,
    )
    reference_2b = _functional_reference(
        transformed_2b,
        transformed_weights_2b,
        spacing=source.grid_spacing,
        gradient_weight=source.gradient_weight,
        boundary_weight=source.boundary_weight,
    )
    reference_joint = reference_1b + reference_2b + involution * involution
    residual_1b = abs(energy_1b - reference_1b)
    residual_2b = abs(energy_2b - reference_2b)
    residual_joint = abs(joint - reference_joint)
    closed = max(
        joint,
        residual_1b,
        residual_2b,
        residual_joint,
        max(-margin_1b, 0.0),
        max(-margin_2b, 0.0),
    ) <= source.tolerance

    return ExactSpatialParityClosure(
        fields_1b,
        fields_2b,
        transformed_2b,
        potential_1b,
        potential_2b,
        volume_1b,
        gradient_1b,
        boundary_1b,
        energy_1b,
        volume_2b,
        gradient_2b,
        boundary_2b,
        energy_2b,
        involution,
        joint,
        lower_1b,
        lower_2b,
        margin_1b,
        margin_2b,
        residual_1b,
        residual_2b,
        residual_joint,
        "closed" if closed else "open",
    )


def _residual(
    value: ExactSpatialParityInput | _base.ParityDFIInput,
    output: ExactSpatialParityClosure,
) -> ResidualResult:
    source = _exact_input(value)
    vector = (
        output.reference_residual_1b,
        output.reference_residual_2b,
        output.reference_residual_joint,
        max(-output.coercivity_margin_1b, 0.0),
        max(-output.coercivity_margin_2b, 0.0),
        output.exchange_involution_residual,
    )
    passed = max(vector) <= source.tolerance
    return ResidualResult(
        "pDFI C01 independent formula and coercivity residual",
        vector,
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def _predicate(output: ExactSpatialParityClosure, residual: ResidualResult | None) -> bool:
    return bool(
        residual is not None
        and residual.passed
        and output.closure_status == "closed"
        and output.joint_energy <= residual.tolerance
    )


def _source_removal(source_id: str, source_index: int):
    def check(value: ExactSpatialParityInput | _base.ParityDFIInput) -> SourceRemovalResult:
        _exact_input(value)
        fields = np.zeros((len(SOURCE_IDS), 3), dtype=float)
        fields[source_index, 1] = 1.0
        complete_weights = np.ones(len(SOURCE_IDS), dtype=float)
        removed_weights = complete_weights.copy()
        removed_weights[source_index] = 0.0
        _, _, _, _, complete = _functional(
            fields,
            complete_weights,
            spacing=1.0,
            gradient_weight=1.0,
            boundary_weight=1.0,
        )
        _, _, _, _, removed = _functional(
            fields,
            removed_weights,
            spacing=1.0,
            gradient_weight=1.0,
            boundary_weight=1.0,
        )
        return source_removal_result(
            ComplexId(source_id),
            np.array([complete]),
            np.array([removed]),
            tolerance=1e-12,
        )

    return check


def _replacement_contract() -> ComplexContract:
    return ComplexContract(
        complex_id=_base.C_ID,
        appendix=_base.APPENDIX,
        appendix_source_sha256=_base.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=_base.B_IDS,
        domain=DomainSpec(
            "complete spatial pDFI defect fields",
            "nonnegative 1B/2B source energies, positive weights, and involutive spatial/source exchange",
            (ExactSpatialParityInput, _base.ParityDFIInput),
        ),
        codomain=CodomainSpec(
            "coercive spatial parity-elastic closure",
            "source-volume, normalized-defect gradient, boundary leakage, coercivity, and exchange certificate",
            (ExactSpatialParityClosure,),
        ),
        operator=spatial_parity_closure_operator,
        residual=_residual,
        closure_predicate=_predicate,
        source_removal_checks=tuple(
            _source_removal(source_id, index)
            for index, source_id in enumerate(SOURCE_IDS)
        ),
        artifact_spec=ArtifactSpec(
            ("transition_csv", "parity_plot", "coercivity_table"),
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )


def contracts() -> tuple[ComplexContract, ...]:
    replacement = _replacement_contract()
    return tuple(
        replacement if contract.complex_id == replacement.complex_id else contract
        for contract in _base.contracts()
    )
