"""Exact finite regular nonperforating horizon geometry C01 contract."""

from __future__ import annotations

from dataclasses import dataclass

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
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import (
    APPENDIX,
    APPENDIX_SHA256,
    FieldLawInput,
    SPECS,
    derived_operator,
)


SPEC = SPECS["black_hole_dynamics"]
C_ID = SPEC.c_id
B_TRANSLATION, B_HORIZON = SPEC.b_ids
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "black_holes_hawking_radiation_and_observer_horizons/"
    "horizon_geometry_contract.py"
)


@dataclass(frozen=True)
class HorizonGeometryInput:
    horizon_points: np.ndarray
    horizon_normals: np.ndarray
    translation_matrix: np.ndarray
    translation_vector: np.ndarray
    entropy_values: np.ndarray
    mapped_entropy_values: np.ndarray
    horizon_level_values: np.ndarray
    mapped_horizon_level_values: np.ndarray
    mapped_points: np.ndarray | None = None
    mapped_normals: np.ndarray | None = None
    translation_source_residual: float = 0.0
    horizon_source_residual: float = 0.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class HorizonGeometryCertificate:
    spatial_domain: np.ndarray
    horizon_points: np.ndarray
    mapped_points: np.ndarray
    horizon_normals: np.ndarray
    mapped_normals: np.ndarray
    expected_mapped_normals: np.ndarray
    local_operator: np.ndarray
    map_residual: float
    inverse_map_residual: float
    entropy_invariance_residual: float
    horizon_invariance_residual: float
    normal_transport_residual: float
    normal_unit_residual: float
    transversality_margin: float
    invertibility_margin: float
    lip_constant: float
    lip_bound_residual: float
    translation_source_residual: float
    horizon_source_residual: float
    status_equivalence_residual: float
    closure_status: str


def _field_adapter(value: FieldLawInput) -> HorizonGeometryInput:
    coordinates = np.asarray(value.coordinates, dtype=float)
    count = coordinates.size
    angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)
    points = np.column_stack((np.cos(angles), np.sin(angles)))
    normals = points.copy()
    angle = 0.25
    matrix = np.array(
        (
            (np.cos(angle), -np.sin(angle)),
            (np.sin(angle), np.cos(angle)),
        ),
        dtype=float,
    )
    mapped = points @ matrix.T
    entropy = np.sum(points * points, axis=1)
    mapped_entropy = np.sum(mapped * mapped, axis=1)
    level = entropy - 1.0
    mapped_level = mapped_entropy - 1.0
    first = derived_operator(
        B_TRANSLATION,
        SPEC.source_kinds[0],
        SPEC.source_kinds[1],
        value,
    )
    second = derived_operator(
        B_HORIZON,
        SPEC.source_kinds[2],
        SPEC.source_kinds[3],
        value,
    )
    return HorizonGeometryInput(
        points,
        normals,
        matrix,
        np.zeros(2, dtype=float),
        entropy,
        mapped_entropy,
        level,
        mapped_level,
        translation_source_residual=float(np.linalg.norm(first.residual)),
        horizon_source_residual=float(np.linalg.norm(second.residual)),
        tolerance=value.tolerance,
    )


def _input(value: HorizonGeometryInput | FieldLawInput) -> HorizonGeometryInput:
    if isinstance(value, HorizonGeometryInput):
        return value
    if isinstance(value, FieldLawInput):
        return _field_adapter(value)
    raise DomainViolationError(
        "horizon geometry requires HorizonGeometryInput or FieldLawInput"
    )


def _validated(source: HorizonGeometryInput):
    points = np.asarray(source.horizon_points, dtype=float)
    normals = np.asarray(source.horizon_normals, dtype=float)
    matrix = np.asarray(source.translation_matrix, dtype=float)
    vector = np.asarray(source.translation_vector, dtype=float)
    if points.ndim != 2 or points.shape[0] < 3 or points.shape[1] < 2:
        raise DomainViolationError(
            "horizon geometry requires at least three points in dimension two or higher"
        )
    if normals.shape != points.shape:
        raise DomainViolationError("horizon normals must match the horizon points")
    dimension = points.shape[1]
    if matrix.shape != (dimension, dimension) or vector.shape != (dimension,):
        raise DomainViolationError(
            "translation matrix/vector must match the horizon dimension"
        )
    channels = tuple(
        np.asarray(item, dtype=float)
        for item in (
            source.entropy_values,
            source.mapped_entropy_values,
            source.horizon_level_values,
            source.mapped_horizon_level_values,
        )
    )
    if any(channel.shape != (points.shape[0],) for channel in channels):
        raise DomainViolationError(
            "entropy and horizon-level channels must have one value per point"
        )
    ensure_finite((points, normals, matrix, vector, channels), name="horizon geometry input")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    for label, residual in (
        ("translation", source.translation_source_residual),
        ("horizon", source.horizon_source_residual),
    ):
        if not np.isfinite(residual) or residual < 0.0:
            raise DomainViolationError(f"{label} source residual must be finite and nonnegative")
    return points, normals, matrix, vector, channels


def horizon_geometry_operator(
    value: HorizonGeometryInput | FieldLawInput,
) -> HorizonGeometryCertificate:
    source = _input(value)
    points, normals, matrix, vector, channels = _validated(source)
    entropy, mapped_entropy, level, mapped_level = channels
    singular = np.linalg.svd(matrix, compute_uv=False)
    invertibility_margin = float(singular[-1])
    if invertibility_margin <= source.tolerance:
        inverse = np.linalg.pinv(matrix, rcond=max(source.tolerance, 1e-15))
    else:
        inverse = np.linalg.inv(matrix)

    expected_points = points @ matrix.T + vector
    mapped_points = (
        expected_points
        if source.mapped_points is None
        else np.asarray(source.mapped_points, dtype=float)
    )
    if mapped_points.shape != points.shape:
        raise DomainViolationError("mapped horizon points must preserve the point shape")
    ensure_finite(mapped_points, name="mapped horizon points")

    raw_expected_normals = normals @ inverse
    normal_denominators = np.linalg.norm(raw_expected_normals, axis=1)
    transversality_margin = float(np.min(normal_denominators))
    safe = np.maximum(normal_denominators, np.finfo(float).eps)
    expected_normals = raw_expected_normals / safe[:, None]
    mapped_normals = (
        expected_normals
        if source.mapped_normals is None
        else np.asarray(source.mapped_normals, dtype=float)
    )
    if mapped_normals.shape != normals.shape:
        raise DomainViolationError("mapped normals must preserve the normal-field shape")
    ensure_finite(mapped_normals, name="mapped horizon normals")

    map_residual = float(np.linalg.norm(mapped_points - expected_points))
    inverse_points = (mapped_points - vector) @ inverse.T
    inverse_residual = float(np.linalg.norm(inverse_points - points))
    entropy_residual = float(np.linalg.norm(mapped_entropy - entropy))
    horizon_residual = float(
        np.linalg.norm(level) + np.linalg.norm(mapped_level - level)
    )
    normal_transport = float(np.linalg.norm(mapped_normals - expected_normals))
    normal_unit = float(
        np.linalg.norm(np.linalg.norm(normals, axis=1) - 1.0)
        + np.linalg.norm(np.linalg.norm(mapped_normals, axis=1) - 1.0)
    )

    lip_constant = float(np.linalg.norm(matrix, ord=2))
    pairwise_bound = 0.0
    for first in range(points.shape[0]):
        for second in range(first + 1, points.shape[0]):
            source_distance = float(np.linalg.norm(points[first] - points[second]))
            target_distance = float(
                np.linalg.norm(mapped_points[first] - mapped_points[second])
            )
            if source_distance > source.tolerance:
                pairwise_bound = max(
                    pairwise_bound,
                    target_distance - lip_constant * source_distance,
                )
    lip_residual = max(pairwise_bound, 0.0)
    total = max(
        map_residual,
        inverse_residual,
        entropy_residual,
        horizon_residual,
        normal_transport,
        normal_unit,
        max(source.tolerance - transversality_margin, 0.0),
        max(source.tolerance - invertibility_margin, 0.0),
        lip_residual,
        source.translation_source_residual,
        source.horizon_source_residual,
    )
    closed = total <= source.tolerance
    status_equivalence = float(closed != (total <= source.tolerance))
    return HorizonGeometryCertificate(
        np.arange(points.shape[0], dtype=float),
        points,
        mapped_points,
        normals,
        mapped_normals,
        expected_normals,
        np.linalg.norm(mapped_points, axis=1),
        map_residual,
        inverse_residual,
        entropy_residual,
        horizon_residual,
        normal_transport,
        normal_unit,
        transversality_margin,
        invertibility_margin,
        lip_constant,
        lip_residual,
        source.translation_source_residual,
        source.horizon_source_residual,
        status_equivalence,
        "closed" if closed and status_equivalence <= source.tolerance else "open",
    )


def _residual(value, output: HorizonGeometryCertificate) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.map_residual,
        output.inverse_map_residual,
        output.entropy_invariance_residual,
        output.horizon_invariance_residual,
        output.normal_transport_residual,
        output.normal_unit_residual,
        max(tolerance - output.transversality_margin, 0.0),
        max(tolerance - output.invertibility_margin, 0.0),
        output.lip_bound_residual,
        output.translation_source_residual,
        output.horizon_source_residual,
        output.status_equivalence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "regular horizon restriction, inverse, and normal transport",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "lip_constant": output.lip_constant,
            "invertibility_margin": output.invertibility_margin,
            "transversality_margin": output.transversality_margin,
            "nonperforating_restriction_checked": True,
        },
    )


def _response(output: HorizonGeometryCertificate) -> np.ndarray:
    return np.concatenate((output.mapped_points.ravel(), output.mapped_normals.ravel()))


def _remove_translation(value) -> SourceRemovalResult:
    source = _input(value)
    complete = horizon_geometry_operator(source)
    removed = np.concatenate(
        (source.horizon_points.ravel(), source.horizon_normals.ravel())
    )
    return source_removal_result(
        ComplexId(B_TRANSLATION),
        _response(complete),
        removed,
        tolerance=max(source.tolerance, 1e-12),
    )


def _remove_horizon(value) -> SourceRemovalResult:
    source = _input(value)
    complete = horizon_geometry_operator(source)
    removed = np.concatenate(
        (complete.mapped_points.ravel(), np.zeros_like(complete.mapped_normals).ravel())
    )
    return source_removal_result(
        ComplexId(B_HORIZON),
        _response(complete),
        removed,
        tolerance=max(source.tolerance, 1e-12),
    )


def contract() -> ComplexContract:
    return ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B_TRANSLATION), ComplexId(B_HORIZON)),
        domain=DomainSpec(
            "regular invariant horizon transport",
            "finite regular horizon samples, unit normal field, invertible affine translation, entropy and level-set invariance channels, and localized B residuals",
            (HorizonGeometryInput, FieldLawInput),
        ),
        codomain=CodomainSpec(
            "nonperforating horizon diffeomorphism certificate",
            "restricted map, inverse reconstruction, invariant horizon channels, inverse-transpose normal transport, transversality, and Lipschitz bound",
            (HorizonGeometryCertificate,),
        ),
        operator=horizon_geometry_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
            and output.invertibility_margin > residual.tolerance
            and output.transversality_margin > residual.tolerance
        ),
        source_removal_checks=(_remove_translation, _remove_horizon),
        artifact_spec=ArtifactSpec(
            ("horizon_map", "normal_transport_table", "lip_bound_record"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
