"""Authoritative EDI barrier, identifiability, and variational inverse laws."""

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
from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    SpatialClosureInput,
    additive_contract,
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


APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
IMPLEMENTATION = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "elastic_dubler_interferometry_probing_gravitational_curvature/derived_contracts.py"
)
BARRIER_ID = "2_adic_curvature_regularity_barrier"
STABILITY_ID = "stability_conditioned_geometric_identifiability"
C_ID = "regularized_stable_geometric_reconstruction"


B_SPECS = (
    (
        BARRIER_ID,
        (
            "bridge_duality_and_the_2_adic_criterion",
            "elastic_curvature_smoothness_curvature_singularity",
        ),
    ),
    (
        STABILITY_ID,
        (
            "elastic_entropic_stability_entropic_instability",
            "elastic_geometric_consistency_geometric_degeneracy",
        ),
    ),
)


@dataclass(frozen=True)
class RegularizedGeometryInput:
    observation_matrix: np.ndarray
    geometry_matrix: np.ndarray
    observed_data: np.ndarray
    barrier_matrix: np.ndarray
    dynamic_matrix: np.ndarray
    barrier_weight: float = 1.0
    dynamic_weight: float = 1.0
    candidate: np.ndarray | None = None
    admissible: bool = True
    barrier_regular: bool = True
    stability_identifiable: bool = True
    tolerance: float = 1e-10


@dataclass(frozen=True)
class RegularizedGeometryCertificate:
    forward_matrix: np.ndarray
    hessian: np.ndarray
    linear_term: np.ndarray
    minimizer: np.ndarray
    reconstructed_geometry: np.ndarray
    achieved_objective: float
    data_residual: float
    barrier_energy: float
    dynamic_energy: float
    stationarity_residual: float
    candidate_optimality_residual: float
    coercivity_margin: float
    convexity_margin: float
    identifying_singular_value: float
    stability_constant: float
    perturbation_norm: float
    geometry_perturbation_norm: float
    stability_bound_residual: float
    lower_semicontinuity_residual: float
    attainment_residual: float
    admissible_set_defect: float
    noncoercive_defect: float
    nonidentifying_defect: float
    barrier_source_residual: float
    stability_source_residual: float
    status_equivalence_residual: float
    closure_status: str


def _as_matrix(value: object, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 1:
        raise DomainViolationError(f"{name} must be a nonempty finite matrix")
    ensure_finite(array, name=name)
    return array


def _as_vector(value: object, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1 or array.size < 1:
        raise DomainViolationError(f"{name} must be a nonempty finite vector")
    ensure_finite(array, name=name)
    return array


def _adapt_spatial(value: SpatialClosureInput) -> RegularizedGeometryInput:
    required = {BARRIER_ID, STABILITY_ID}
    if set(value.source_fields) != required:
        missing = sorted(required - set(value.source_fields))
        extra = sorted(set(value.source_fields) - required)
        raise DomainViolationError(
            f"regularized geometry source mismatch; missing={missing}, extra={extra}"
        )
    barrier_field = np.asarray(value.source_fields[BARRIER_ID], dtype=float).ravel()
    stability_field = np.asarray(value.source_fields[STABILITY_ID], dtype=float).ravel()
    if barrier_field.size != stability_field.size or barrier_field.size < 1:
        raise DomainViolationError(
            "barrier and stability fields require one common finite dimension"
        )
    ensure_finite((barrier_field, stability_field), name="regularized geometry fields")
    scale_barrier = 0.25 + np.abs(barrier_field) / (1.0 + np.abs(barrier_field))
    scale_dynamic = 0.25 + np.abs(stability_field) / (1.0 + np.abs(stability_field))
    dimension = barrier_field.size
    return RegularizedGeometryInput(
        observation_matrix=np.eye(dimension),
        geometry_matrix=np.eye(dimension),
        observed_data=0.5 * (barrier_field + stability_field),
        barrier_matrix=np.diag(scale_barrier),
        dynamic_matrix=np.diag(scale_dynamic),
        barrier_weight=1.0,
        dynamic_weight=1.0,
        tolerance=value.tolerance,
    )


def _input(
    value: RegularizedGeometryInput | SpatialClosureInput,
) -> RegularizedGeometryInput:
    if isinstance(value, RegularizedGeometryInput):
        return value
    if isinstance(value, SpatialClosureInput):
        return _adapt_spatial(value)
    raise DomainViolationError(
        "regularized geometry requires RegularizedGeometryInput or SpatialClosureInput"
    )


def _validated(source: RegularizedGeometryInput):
    observation = _as_matrix(source.observation_matrix, name="observation matrix")
    geometry = _as_matrix(source.geometry_matrix, name="geometry map")
    barrier = _as_matrix(source.barrier_matrix, name="barrier matrix")
    dynamic = _as_matrix(source.dynamic_matrix, name="dynamic energy matrix")
    data = _as_vector(source.observed_data, name="observed data")
    parameter_dimension = geometry.shape[1]
    if observation.shape[1] != geometry.shape[0]:
        raise DomainViolationError("observation and geometry matrices do not compose")
    if data.shape != (observation.shape[0],):
        raise DomainViolationError("observed data must match the observation codomain")
    if barrier.shape[1] != parameter_dimension or dynamic.shape[1] != parameter_dimension:
        raise DomainViolationError(
            "barrier and dynamic matrices must act on the parameter domain"
        )
    for name, scalar in (
        ("barrier_weight", source.barrier_weight),
        ("dynamic_weight", source.dynamic_weight),
    ):
        if not np.isfinite(scalar) or scalar <= 0.0:
            raise DomainViolationError(f"{name} must be finite and strictly positive")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    candidate = None
    if source.candidate is not None:
        candidate = _as_vector(source.candidate, name="candidate geometry parameter")
        if candidate.shape != (parameter_dimension,):
            raise DomainViolationError("candidate must match the parameter dimension")
    return observation, geometry, data, barrier, dynamic, candidate


def _solve_components(
    source: RegularizedGeometryInput,
    *,
    include_barrier: bool = True,
    include_stability: bool = True,
):
    observation, geometry, data, barrier, dynamic, candidate = _validated(source)
    if not source.admissible:
        raise DomainViolationError("regularized geometry admissible set is empty")
    forward = observation @ geometry if include_stability else np.zeros(
        (observation.shape[0], geometry.shape[1]), dtype=float
    )
    barrier_term = barrier if include_barrier else np.zeros_like(barrier)
    dynamic_term = dynamic if include_stability else np.zeros_like(dynamic)
    hessian = (
        forward.T @ forward
        + source.barrier_weight * (barrier_term.T @ barrier_term)
        + source.dynamic_weight * (dynamic_term.T @ dynamic_term)
    )
    linear = forward.T @ data
    eigenvalues = np.linalg.eigvalsh(0.5 * (hessian + hessian.T))
    margin = float(eigenvalues[0])
    if margin <= source.tolerance:
        minimizer = np.linalg.pinv(hessian, rcond=max(source.tolerance, 1e-15)) @ linear
    else:
        minimizer = np.linalg.solve(hessian, linear)
    return (
        observation,
        geometry,
        data,
        barrier_term,
        dynamic_term,
        candidate,
        forward,
        hessian,
        linear,
        minimizer,
        margin,
    )


def regularized_geometry_operator(
    value: RegularizedGeometryInput | SpatialClosureInput,
) -> RegularizedGeometryCertificate:
    source = _input(value)
    (
        observation,
        geometry,
        data,
        barrier,
        dynamic,
        candidate,
        forward,
        hessian,
        linear,
        minimizer,
        margin,
    ) = _solve_components(source)

    geometry_output = geometry @ minimizer
    data_vector = forward @ minimizer - data
    barrier_vector = barrier @ minimizer
    dynamic_vector = dynamic @ minimizer
    data_residual = float(np.linalg.norm(data_vector) ** 2)
    barrier_energy = float(
        source.barrier_weight * np.linalg.norm(barrier_vector) ** 2
    )
    dynamic_energy = float(
        source.dynamic_weight * np.linalg.norm(dynamic_vector) ** 2
    )
    objective = data_residual + barrier_energy + dynamic_energy
    stationarity = float(np.linalg.norm(hessian @ minimizer - linear))
    candidate_residual = (
        0.0
        if candidate is None
        else float(np.linalg.norm(hessian @ candidate - linear))
    )

    singular_values = np.linalg.svd(forward, compute_uv=False)
    identifying = float(singular_values[-1]) if singular_values.size else 0.0
    convexity = margin
    if margin > source.tolerance:
        stability_operator = geometry @ np.linalg.solve(hessian, forward.T)
        stability_constant = float(np.linalg.norm(stability_operator, ord=2))
    else:
        stability_constant = float("inf")

    perturbation = np.linspace(0.25, 0.75, data.size, dtype=float) * 1e-6
    perturbed_linear = forward.T @ (data + perturbation)
    if margin > source.tolerance:
        perturbed_minimizer = np.linalg.solve(hessian, perturbed_linear)
    else:
        perturbed_minimizer = np.linalg.pinv(
            hessian, rcond=max(source.tolerance, 1e-15)
        ) @ perturbed_linear
    perturbation_norm = float(np.linalg.norm(perturbation))
    geometry_perturbation = float(
        np.linalg.norm(geometry @ (perturbed_minimizer - minimizer))
    )
    stability_residual = (
        float("inf")
        if not np.isfinite(stability_constant)
        else max(
            geometry_perturbation
            - stability_constant * perturbation_norm
            - 10.0 * np.finfo(float).eps,
            0.0,
        )
    )

    lower_semicontinuity = float(
        np.linalg.norm(hessian - hessian.T)
        + max(-float(np.min(np.linalg.eigvalsh(0.5 * (hessian + hessian.T)))), 0.0)
    )
    attainment = stationarity
    admissible_defect = float(not source.admissible)
    noncoercive_defect = float(
        (not source.barrier_regular) or margin <= source.tolerance
    )
    nonidentifying_defect = float(
        (not source.stability_identifiable)
        or identifying <= source.tolerance
        or margin <= source.tolerance
    )

    barrier_source_residual = 0.0 if source.barrier_regular else 1.0
    stability_source_residual = 0.0 if source.stability_identifiable else 1.0
    structural = max(
        admissible_defect,
        noncoercive_defect,
        nonidentifying_defect,
        barrier_source_residual,
        stability_source_residual,
    )
    reconstructed = bool(
        structural <= source.tolerance
        and stationarity <= source.tolerance
        and candidate_residual <= source.tolerance
        and stability_residual <= source.tolerance
        and lower_semicontinuity <= source.tolerance
    )
    status_equivalence = float(
        reconstructed
        != (
            source.admissible
            and source.barrier_regular
            and source.stability_identifiable
            and margin > source.tolerance
            and identifying > source.tolerance
            and stationarity <= source.tolerance
            and candidate_residual <= source.tolerance
        )
    )
    return RegularizedGeometryCertificate(
        forward,
        hessian,
        linear,
        minimizer,
        geometry_output,
        objective,
        data_residual,
        barrier_energy,
        dynamic_energy,
        stationarity,
        candidate_residual,
        margin,
        convexity,
        identifying,
        stability_constant,
        perturbation_norm,
        geometry_perturbation,
        stability_residual,
        lower_semicontinuity,
        attainment,
        admissible_defect,
        noncoercive_defect,
        nonidentifying_defect,
        barrier_source_residual,
        stability_source_residual,
        status_equivalence,
        "closed" if reconstructed and status_equivalence <= source.tolerance else "open",
    )


def _residual(value, output: RegularizedGeometryCertificate) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.stationarity_residual,
        output.candidate_optimality_residual,
        output.stability_bound_residual,
        output.lower_semicontinuity_residual,
        output.attainment_residual,
        output.admissible_set_defect,
        output.noncoercive_defect,
        output.nonidentifying_defect,
        output.barrier_source_residual,
        output.stability_source_residual,
        output.status_equivalence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "regularized geometry attainment, coercivity, uniqueness, and stability",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "coercivity_margin": output.coercivity_margin,
            "convexity_margin": output.convexity_margin,
            "identifying_singular_value": output.identifying_singular_value,
            "stability_constant": output.stability_constant,
            "minimum_attained": output.attainment_residual <= tolerance,
        },
    )


def _response(output: RegularizedGeometryCertificate) -> np.ndarray:
    return np.concatenate((output.minimizer, output.reconstructed_geometry))


def _remove_barrier(value) -> SourceRemovalResult:
    source = _input(value)
    complete = regularized_geometry_operator(source)
    components = _solve_components(source, include_barrier=False)
    removed_minimizer = components[9]
    removed_geometry = components[1] @ removed_minimizer
    return source_removal_result(
        ComplexId(BARRIER_ID),
        _response(complete),
        np.concatenate((removed_minimizer, removed_geometry)),
        tolerance=max(source.tolerance, 1e-12),
    )


def _remove_stability(value) -> SourceRemovalResult:
    source = _input(value)
    complete = regularized_geometry_operator(source)
    components = _solve_components(source, include_stability=False)
    removed_minimizer = components[9]
    removed_geometry = components[1] @ removed_minimizer
    return source_removal_result(
        ComplexId(STABILITY_ID),
        _response(complete),
        np.concatenate((removed_minimizer, removed_geometry)),
        tolerance=max(source.tolerance, 1e-12),
    )


def contracts():
    b_contracts = tuple(
        additive_contract(
            complex_id,
            source_ids,
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        )
        for complex_id, source_ids in B_SPECS
    )
    c_contract = ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(BARRIER_ID), ComplexId(STABILITY_ID)),
        domain=DomainSpec(
            "regularized stable geometric inverse",
            "nonempty finite admissible parameter domain, composable observation/geometry maps, positive barrier and dynamic weights, and identifying positive-definite objective",
            (RegularizedGeometryInput, SpatialClosureInput),
        ),
        codomain=CodomainSpec(
            "attained unique stable geometry certificate",
            "exact quadratic minimizer, objective decomposition, positive coercivity/convexity/identifiability margins, perturbation bound, and exhaustive defect status",
            (RegularizedGeometryCertificate,),
        ),
        operator=regularized_geometry_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
            and output.coercivity_margin > residual.tolerance
            and output.identifying_singular_value > residual.tolerance
        ),
        source_removal_checks=(_remove_barrier, _remove_stability),
        artifact_spec=ArtifactSpec(
            ("objective_decomposition", "margin_table", "stability_perturbation_record"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.derived_contracts",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    return (*b_contracts, c_contract)
