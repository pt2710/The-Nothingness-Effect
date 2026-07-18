"""Exact finite potential-current closure for Elastic Dubler C01."""

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


SPEC = SPECS["elastic_dubler_effect"]
C_ID = SPEC.c_id
B_ENDPOINT, B_DIFFERENTIAL = SPEC.b_ids
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "the_elastic_dubler_effect/potential_current_contract.py"
)


@dataclass(frozen=True)
class PotentialCurrentInput:
    coordinates: np.ndarray
    entropy_source: np.ndarray
    elasticity: float
    alpha: float = 1.0
    endpoint_ratio: np.ndarray | None = None
    edge_current: np.ndarray | None = None
    production: np.ndarray | None = None
    tolerance: float = 1e-10


@dataclass(frozen=True)
class PotentialCurrentCertificate:
    spatial_domain: np.ndarray
    potential: np.ndarray
    endpoint_ratio: np.ndarray
    edge_current: np.ndarray
    production: np.ndarray
    local_operator: np.ndarray
    reconstructed_potential: np.ndarray
    endpoint_residual: float
    current_residual: float
    production_residual: float
    potential_reconstruction_residual: float
    circulation_residual: float
    gauge_ratio_residual: float
    gauge_current_residual: float
    gauge_production_residual: float
    endpoint_source_residual: float
    differential_source_residual: float
    classification_idempotence_residual: float
    closure_status: str


def _input(value: PotentialCurrentInput | FieldLawInput) -> PotentialCurrentInput:
    if isinstance(value, PotentialCurrentInput):
        return value
    if isinstance(value, FieldLawInput):
        return PotentialCurrentInput(
            coordinates=value.coordinates,
            entropy_source=value.source,
            elasticity=value.scale,
            alpha=value.frequency,
            tolerance=value.tolerance,
        )
    raise DomainViolationError(
        "Dubler potential-current closure requires PotentialCurrentInput or FieldLawInput"
    )


def _validated(value: PotentialCurrentInput) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray(value.coordinates, dtype=float)
    source = np.asarray(value.entropy_source, dtype=float)
    if x.ndim != 1 or x.size < 5 or source.shape != x.shape:
        raise DomainViolationError(
            "potential-current closure requires equal one-dimensional coordinate/source arrays with at least five samples"
        )
    ensure_finite((x, source), name="Dubler potential-current input")
    spacing = np.diff(x)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("coordinates must be strictly increasing")
    if not np.isfinite(value.elasticity) or value.elasticity <= 0.0:
        raise DomainViolationError("elasticity must be finite and strictly positive")
    if not np.isfinite(value.alpha) or value.alpha == 0.0:
        raise DomainViolationError("alpha must be finite and nonzero")
    if not np.isfinite(value.tolerance) or value.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return x, source, spacing


def potential_current_operator(
    value: PotentialCurrentInput | FieldLawInput,
) -> PotentialCurrentCertificate:
    source = _input(value)
    x, entropy, spacing = _validated(source)
    kd = float(source.elasticity)
    alpha = float(source.alpha)
    potential = -entropy / kd

    expected_ratio = np.exp(potential - potential[0])
    expected_edge_current = alpha * kd * np.diff(potential) / spacing
    gradient = np.gradient(potential, x, edge_order=2)
    laplacian = np.gradient(gradient, x, edge_order=2)
    expected_production = -alpha * kd * laplacian

    ratio = (
        expected_ratio
        if source.endpoint_ratio is None
        else np.asarray(source.endpoint_ratio, dtype=float)
    )
    current = (
        expected_edge_current
        if source.edge_current is None
        else np.asarray(source.edge_current, dtype=float)
    )
    production = (
        expected_production
        if source.production is None
        else np.asarray(source.production, dtype=float)
    )
    if ratio.shape != x.shape or production.shape != x.shape:
        raise DomainViolationError("endpoint ratio and production must match the spatial domain")
    if current.shape != (x.size - 1,):
        raise DomainViolationError("edge current must have one value per spatial edge")
    ensure_finite((ratio, current, production), name="potential-current channels")
    if np.any(ratio <= 0.0):
        raise DomainViolationError("endpoint ratios must be strictly positive")

    endpoint_residual = float(np.linalg.norm(np.log(ratio) - potential + potential[0]))
    current_residual = float(np.linalg.norm(current - expected_edge_current))
    production_residual = float(np.linalg.norm(production - expected_production))

    reconstructed = np.empty_like(potential)
    reconstructed[0] = potential[0]
    reconstructed[1:] = potential[0] + np.cumsum(
        current * spacing / (alpha * kd)
    )
    reconstruction_residual = float(np.linalg.norm(reconstructed - potential))
    circulation_residual = float(
        abs(
            np.sum(current * spacing / (alpha * kd))
            - (potential[-1] - potential[0])
        )
    )

    gauge_shift = 1.375
    shifted = potential + gauge_shift
    shifted_ratio = np.exp(shifted - shifted[0])
    shifted_current = alpha * kd * np.diff(shifted) / spacing
    shifted_gradient = np.gradient(shifted, x, edge_order=2)
    shifted_laplacian = np.gradient(shifted_gradient, x, edge_order=2)
    shifted_production = -alpha * kd * shifted_laplacian
    gauge_ratio = float(np.linalg.norm(shifted_ratio - expected_ratio))
    gauge_current = float(np.linalg.norm(shifted_current - expected_edge_current))
    gauge_production = float(
        np.linalg.norm(shifted_production - expected_production)
    )

    legacy = FieldLawInput(
        x,
        entropy,
        scale=kd,
        frequency=alpha,
        tolerance=source.tolerance,
    )
    first = derived_operator(
        B_ENDPOINT,
        SPEC.source_kinds[0],
        SPEC.source_kinds[1],
        legacy,
    )
    second = derived_operator(
        B_DIFFERENTIAL,
        SPEC.source_kinds[2],
        SPEC.source_kinds[3],
        legacy,
    )
    endpoint_source = float(np.linalg.norm(first.residual))
    differential_source = float(np.linalg.norm(second.residual))

    total = max(
        endpoint_residual,
        current_residual,
        production_residual,
        reconstruction_residual,
        circulation_residual,
        gauge_ratio,
        gauge_current,
        gauge_production,
        endpoint_source,
        differential_source,
    )
    classification = float(total > source.tolerance)
    classification_idempotence = abs(float(bool(classification)) - classification)
    closed = total <= source.tolerance and classification_idempotence <= source.tolerance
    local_operator = np.pad(current, (0, 1), mode="edge")
    return PotentialCurrentCertificate(
        x,
        potential,
        ratio,
        current,
        production,
        local_operator,
        reconstructed,
        endpoint_residual,
        current_residual,
        production_residual,
        reconstruction_residual,
        circulation_residual,
        gauge_ratio,
        gauge_current,
        gauge_production,
        endpoint_source,
        differential_source,
        classification_idempotence,
        "closed" if closed else "open",
    )


def _residual(
    value: PotentialCurrentInput | FieldLawInput,
    output: PotentialCurrentCertificate,
) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.endpoint_residual,
        output.current_residual,
        output.production_residual,
        output.potential_reconstruction_residual,
        output.circulation_residual,
        output.gauge_ratio_residual,
        output.gauge_current_residual,
        output.gauge_production_residual,
        output.endpoint_source_residual,
        output.differential_source_residual,
        output.classification_idempotence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "Dubler one-potential endpoint/current/production compatibility",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "common_potential_checked": True,
            "gauge_invariance_checked": True,
            "current_integrability_checked": True,
            "status_idempotence_checked": True,
        },
    )


def _flatten(output: PotentialCurrentCertificate) -> np.ndarray:
    return np.concatenate(
        (output.endpoint_ratio, output.edge_current, output.production)
    )


def _remove_endpoint(value) -> SourceRemovalResult:
    complete = potential_current_operator(value)
    removed = np.concatenate(
        (
            np.ones_like(complete.endpoint_ratio),
            complete.edge_current,
            complete.production,
        )
    )
    return source_removal_result(
        ComplexId(B_ENDPOINT),
        _flatten(complete),
        removed,
        tolerance=max(_input(value).tolerance, 1e-12),
    )


def _remove_differential(value) -> SourceRemovalResult:
    complete = potential_current_operator(value)
    removed = np.concatenate(
        (
            complete.endpoint_ratio,
            np.zeros_like(complete.edge_current),
            np.zeros_like(complete.production),
        )
    )
    return source_removal_result(
        ComplexId(B_DIFFERENTIAL),
        _flatten(complete),
        removed,
        tolerance=max(_input(value).tolerance, 1e-12),
    )


def contract() -> ComplexContract:
    return ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B_ENDPOINT), ComplexId(B_DIFFERENTIAL)),
        domain=DomainSpec(
            "common Elastic-Dubler potential realization",
            "finite connected one-dimensional domain, positive elasticity, nonzero alpha, and optional measured endpoint/current/production channels",
            (PotentialCurrentInput, FieldLawInput),
        ),
        codomain=CodomainSpec(
            "potential-current spatial closure certificate",
            "one potential, endpoint cocycle, exact edge current, production, gauge, reconstruction, integrability, and status classification",
            (PotentialCurrentCertificate,),
        ),
        operator=potential_current_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
        ),
        source_removal_checks=(_remove_endpoint, _remove_differential),
        artifact_spec=ArtifactSpec(
            ("potential_current_table", "channel_residual_plot", "source_removal_table"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
