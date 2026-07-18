"""Exact finite realization of the spatial DFI C01 closure law.

The appendix C functional is a sum of strictly positive source-volume terms,
a spatial-gradient term, a boundary-trace term, and a joint involution term.
This module implements that zero-set theorem directly on a finite ordered grid.
It does not infer closure from a generic reconstruction candidate.
"""

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

from . import contracts as _legacy
from . import recertified_contracts as _base
from .dfi import dfi_rescaling_residual


SOURCE_IDS = (
    "scale_normalized_dfi_homogeneity_invariant",
    "entropic_applicability_response_operator",
    "flowpoint_certified_dfi_validation_functional",
)
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/fluctuation_and_elastic_dynamics/"
    "dynamic_fluctuation_index/closure_contracts.py"
)


@dataclass(frozen=True)
class ExactSpatialDFIInput:
    """Complete nonnegative 1B/2B defect fields on one finite spatial grid."""

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
class ExactSpatialDFIClosure:
    source_fields_1b: np.ndarray
    source_fields_2b: np.ndarray
    transformed_source_fields_2b: np.ndarray
    source_weights_1b: np.ndarray
    transformed_source_weights_2b: np.ndarray
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


def _legacy_exact_input(value: _legacy.SpatialDFIInput) -> ExactSpatialDFIInput:
    data = np.asarray(value.data, dtype=float)
    if data.ndim != 2 or data.shape[0] < 2 or data.shape[1] < 2:
        raise DomainViolationError("spatial DFI closure requires at least a 2x2 finite matrix")
    ensure_finite(data, name="spatial DFI legacy data")
    if not np.isfinite(value.spectrum_scale) or value.spectrum_scale <= 0.0:
        raise DomainViolationError("spectrum_scale must be finite and strictly positive")
    if not np.isfinite(value.validation_weight) or value.validation_weight <= 0.0:
        raise DomainViolationError("validation_weight must be finite and strictly positive")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")

    homogeneity = dfi_rescaling_residual(
        data,
        value.spectrum_scale,
        2.0 * value.spectrum_scale,
    )
    applicability = _base.entropic_applicability_operator(
        _base.ContextualApplicabilityInput(
            data=data,
            comparison_data=data.copy(),
            spectrum_scale=value.spectrum_scale,
            threshold=value.tolerance,
        )
    ).energy
    validation = abs(float(value.validation_weight) - 1.0)
    scalar_defects = {
        SOURCE_IDS[0]: float(homogeneity) ** 2,
        SOURCE_IDS[1]: float(applicability),
        SOURCE_IDS[2]: float(validation) ** 2,
    }
    fields = {
        key: np.full(data.shape[0], defect, dtype=float)
        for key, defect in scalar_defects.items()
    }
    weights = {key: 1.0 for key in SOURCE_IDS}
    return ExactSpatialDFIInput(
        source_energy_fields_1b=fields,
        source_energy_fields_2b={key: item.copy() for key, item in fields.items()},
        source_weights_1b=weights,
        source_weights_2b=dict(weights),
        spatial_reflection=tuple(reversed(range(data.shape[0]))),
        source_exchange=(0, 1, 2),
        gradient_weight=1.0,
        boundary_weight=1.0,
        grid_spacing=1.0,
        tolerance=value.tolerance,
    )


def _exact_input(value: ExactSpatialDFIInput | _legacy.SpatialDFIInput) -> ExactSpatialDFIInput:
    if isinstance(value, ExactSpatialDFIInput):
        return value
    if isinstance(value, _legacy.SpatialDFIInput):
        return _legacy_exact_input(value)
    raise DomainViolationError(
        "DFI C01 requires ExactSpatialDFIInput or legacy SpatialDFIInput"
    )


def _field_matrix(fields: Mapping[str, np.ndarray], *, label: str) -> np.ndarray:
    if set(fields) != set(SOURCE_IDS):
        missing = sorted(set(SOURCE_IDS) - set(fields))
        extra = sorted(set(fields) - set(SOURCE_IDS))
        raise DomainViolationError(f"{label} source mismatch; missing={missing}, extra={extra}")
    arrays = tuple(np.asarray(fields[source], dtype=float) for source in SOURCE_IDS)
    if any(item.ndim != 1 or item.size < 2 for item in arrays):
        raise DomainViolationError(f"{label} fields must be one-dimensional with at least two samples")
    if len({item.shape for item in arrays}) != 1:
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


def _involutive_permutation(values: tuple[int, ...], size: int, *, label: str) -> np.ndarray:
    permutation = np.asarray(tuple(int(item) for item in values), dtype=int)
    if permutation.shape != (size,) or sorted(permutation.tolist()) != list(range(size)):
        raise DomainViolationError(f"{label} must be a complete permutation")
    if not np.array_equal(permutation[permutation], np.arange(size)):
        raise DomainViolationError(f"{label} must be involutive")
    return permutation


def _functional(
    fields: np.ndarray,
    weights: np.ndarray,
    *,
    spacing: float,
    gradient_weight: float,
    boundary_weight: float,
) -> tuple[np.ndarray, float, float, float, float]:
    potential = weights @ fields
    volume = float(spacing * np.sum(weights[:, None] * fields))
    gradient = np.diff(potential) / spacing
    gradient_energy = float(gradient_weight * spacing * np.sum(gradient * gradient))
    boundary = float(
        boundary_weight * (potential[0] ** 2 + potential[-1] ** 2)
    )
    total = volume + gradient_energy + boundary
    ensure_finite(
        (potential, volume, gradient_energy, boundary, total),
        name="DFI spatial functional",
    )
    return potential, volume, gradient_energy, boundary, total


def _functional_reference(
    fields: np.ndarray,
    weights: np.ndarray,
    *,
    spacing: float,
    gradient_weight: float,
    boundary_weight: float,
) -> float:
    source_count, sample_count = fields.shape
    potential = [
        sum(float(weights[source]) * float(fields[source, point]) for source in range(source_count))
        for point in range(sample_count)
    ]
    volume = spacing * sum(
        float(weights[source]) * float(fields[source, point])
        for source in range(source_count)
        for point in range(sample_count)
    )
    gradient = gradient_weight * spacing * sum(
        ((potential[point + 1] - potential[point]) / spacing) ** 2
        for point in range(sample_count - 1)
    )
    boundary = boundary_weight * (potential[0] ** 2 + potential[-1] ** 2)
    return float(volume + gradient + boundary)


def spatial_closure_operator(
    value: ExactSpatialDFIInput | _legacy.SpatialDFIInput,
) -> ExactSpatialDFIClosure:
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

    fields_1b = _field_matrix(source.source_energy_fields_1b, label="DFI 1B")
    fields_2b = _field_matrix(source.source_energy_fields_2b, label="DFI 2B")
    if fields_1b.shape != fields_2b.shape:
        raise DomainViolationError("DFI 1B and 2B fields must share one domain")
    weights_1b = _weights(source.source_weights_1b, label="DFI 1B")
    weights_2b = _weights(source.source_weights_2b, label="DFI 2B")
    reflection = _involutive_permutation(
        source.spatial_reflection,
        fields_1b.shape[1],
        label="spatial_reflection",
    )
    exchange = _involutive_permutation(
        source.source_exchange,
        len(SOURCE_IDS),
        label="source_exchange",
    )

    transformed_2b = fields_2b[exchange][:, reflection]
    transformed_weights_2b = weights_2b[exchange]
    twice_transformed = transformed_2b[exchange][:, reflection]
    involution = float(np.linalg.norm(twice_transformed - fields_2b))

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

    lower_1b = float(
        np.min(weights_1b) * source.grid_spacing * np.sum(fields_1b)
    )
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
    ref_residual_1b = abs(energy_1b - reference_1b)
    ref_residual_2b = abs(energy_2b - reference_2b)
    ref_residual_joint = abs(joint - reference_joint)

    closed = max(
        joint,
        ref_residual_1b,
        ref_residual_2b,
        ref_residual_joint,
        max(-margin_1b, 0.0),
        max(-margin_2b, 0.0),
    ) <= source.tolerance
    return ExactSpatialDFIClosure(
        fields_1b,
        fields_2b,
        transformed_2b,
        weights_1b,
        transformed_weights_2b,
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
        ref_residual_1b,
        ref_residual_2b,
        ref_residual_joint,
        "closed" if closed else "open",
    )


def _residual(
    source: ExactSpatialDFIInput | _legacy.SpatialDFIInput,
    output: ExactSpatialDFIClosure,
) -> ResidualResult:
    exact = _exact_input(source)
    vector = (
        output.reference_residual_1b,
        output.reference_residual_2b,
        output.reference_residual_joint,
        max(-output.coercivity_margin_1b, 0.0),
        max(-output.coercivity_margin_2b, 0.0),
        output.exchange_involution_residual,
    )
    passed = max(vector) <= exact.tolerance
    return ResidualResult(
        "DFI C01 independent formula and coercivity residual",
        vector,
        exact.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def _predicate(output: ExactSpatialDFIClosure, residual: ResidualResult | None) -> bool:
    return bool(
        residual is not None
        and residual.passed
        and output.closure_status == "closed"
        and output.joint_energy <= residual.tolerance
    )


def _source_removal(source_id: str, source_index: int):
    def check(
        value: ExactSpatialDFIInput | _legacy.SpatialDFIInput,
    ) -> SourceRemovalResult:
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
        complex_id=ComplexId("spatially_localized_dfi_consistency_closure"),
        appendix=_base.APPENDIX,
        appendix_source_sha256=_base.APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=tuple(ComplexId(item) for item in SOURCE_IDS),
        domain=DomainSpec(
            "complete spatial DFI defect fields",
            "nonnegative 1B/2B source energies, strictly positive weights, and involutive spatial/source exchange",
            (ExactSpatialDFIInput, _legacy.SpatialDFIInput),
        ),
        codomain=CodomainSpec(
            "coercive spatial DFI closure",
            "volume, gradient, boundary, coercivity, exchange, and independent-reference certificate",
            (ExactSpatialDFIClosure,),
        ),
        operator=spatial_closure_operator,
        residual=_residual,
        closure_predicate=_predicate,
        source_removal_checks=tuple(
            _source_removal(source_id, index)
            for index, source_id in enumerate(SOURCE_IDS)
        ),
        artifact_spec=ArtifactSpec(
            ("field_csv", "boundary_plot", "coercivity_table"),
            "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )


def contracts() -> tuple[ComplexContract, ...]:
    replacement = _replacement_contract()
    return tuple(
        replacement
        if str(contract.complex_id) == str(replacement.complex_id)
        else contract
        for contract in _base.contracts()
    )
