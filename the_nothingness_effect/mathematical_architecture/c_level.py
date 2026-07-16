"""C-level signed-polar field synthesis from both complete B laws."""

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

from .a_level import (
    APPENDIX,
    APPENDIX_SHA256,
    PiApproximationInput,
    pi_approximation,
)
from .authoritative_obligations import (
    SignedPolarClosureCertificate,
    certify_signed_polar_field,
)


@dataclass(frozen=True)
class SignedPolarFieldInput:
    radius: float
    phase_unit: complex
    order: int
    damping: tuple[float, ...]
    times: tuple[float, ...]
    horizon: float


@dataclass(frozen=True)
class SignedPolarFieldResult:
    canonical_radius: float
    canonical_phase_unit: complex
    times: tuple[float, ...]
    field: tuple[complex, ...]
    local_gradient: tuple[complex, ...]
    boundary_trace_residual: float
    reconstruction_residual: float
    closure_status: str
    authority_certificate: SignedPolarClosureCertificate


def signed_polar_field(
    value: SignedPolarFieldInput,
) -> SignedPolarFieldResult:
    if value.horizon <= 0 or not value.times:
        raise DomainViolationError(
            "positive horizon and nonempty spatial times are required"
        )
    if abs(abs(value.phase_unit) - 1.0) > 1e-10:
        raise DomainViolationError("phase_unit must lie on the unit circle")
    if any(time < 0 or time > value.horizon for time in value.times):
        raise DomainViolationError(
            "times lie outside the declared field domain"
        )
    radius = float(value.radius)
    phase = complex(value.phase_unit)
    if radius < 0:
        radius = -radius
        phase = -phase
    pi_result = pi_approximation(
        PiApproximationInput(value.order, value.damping)
    )
    theta = tuple(
        2 * pi_result.value * time / value.horizon
        for time in value.times
    )
    field = tuple(radius * phase * np.exp(1j * item) for item in theta)
    gradients = tuple(
        field[index + 1] - field[index]
        for index in range(len(field) - 1)
    )
    expected_initial = radius * phase * np.exp(1j * theta[0])
    boundary = float(abs(field[0] - expected_initial))
    reconstruction = float(
        np.linalg.norm(
            np.asarray(field)
            - field[0] * np.exp(1j * (np.asarray(theta) - theta[0]))
        )
    )
    certificate = certify_signed_polar_field(
        value.radius,
        value.phase_unit,
        tuple(complex(item) for item in field),
    )
    typed_residual = max(
        certificate.gauge_residual,
        certificate.norm_residual,
        certificate.initial_reconstruction_residual,
    )
    closed = (
        boundary <= 1e-10
        and reconstruction <= 1e-10
        and typed_residual <= 1e-10
    )
    return SignedPolarFieldResult(
        radius,
        phase,
        value.times,
        tuple(complex(item) for item in field),
        tuple(complex(item) for item in gradients),
        boundary,
        reconstruction,
        "numerical_candidate" if closed else "open",
        certificate,
    )


def field_residual(
    _source,
    output: SignedPolarFieldResult,
) -> ResidualResult:
    vector = (
        output.boundary_trace_residual,
        output.reconstruction_residual,
        output.authority_certificate.gauge_residual,
        output.authority_certificate.norm_residual,
        output.authority_certificate.initial_reconstruction_residual,
    )
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        "signed-polar spatial field",
        vector,
        1e-10,
        norm <= 1e-10,
        ClosureStatus.NUMERICAL_CANDIDATE
        if norm <= 1e-10
        else ClosureStatus.OPEN,
        metadata={
            "candidate_not_minimizer": True,
            "quotient_gauge_checked": True,
        },
    )


def remove_arithmetic_source(
    value: SignedPolarFieldInput,
) -> SourceRemovalResult:
    complete = signed_polar_field(value)
    removed = signed_polar_field(
        SignedPolarFieldInput(
            1.0,
            value.phase_unit,
            value.order,
            value.damping,
            value.times,
            value.horizon,
        )
    )
    return source_removal_result(
        ComplexId(
            "addition_of_arithmetic_orientation_and_typed_operation_theory"
        ),
        np.asarray(complete.field),
        np.asarray(removed.field),
        tolerance=1e-12,
    )


def remove_geometry_source(
    value: SignedPolarFieldInput,
) -> SourceRemovalResult:
    complete = signed_polar_field(value)
    removed = np.full(
        len(value.times),
        complete.canonical_radius * complete.canonical_phase_unit,
        dtype=complex,
    )
    return source_removal_result(
        ComplexId("addition_of_approximation_and_harmonic_geometry"),
        np.asarray(complete.field),
        removed,
        tolerance=1e-12,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId(
                "addition_of_the_two_complete_b_level_operator_families"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.C,
            (
                ComplexId(
                    "addition_of_arithmetic_orientation_and_typed_operation_theory"
                ),
                ComplexId(
                    "addition_of_approximation_and_harmonic_geometry"
                ),
            ),
            DomainSpec(
                "signed-polar spatial field",
                (
                    "quotient-compatible radius, phase, approximation, and "
                    "spatial times"
                ),
                (SignedPolarFieldInput,),
            ),
            CodomainSpec(
                "calibrated complex quotient field",
                (
                    "field, local gradients, signed-polar gauge, boundary, "
                    "and reconstruction residuals"
                ),
                (SignedPolarFieldResult,),
            ),
            signed_polar_field,
            residual=field_residual,
            closure_predicate=lambda output, residual: (
                output.closure_status == "numerical_candidate"
                and residual is not None
                and residual.passed
            ),
            source_removal_checks=(
                remove_arithmetic_source,
                remove_geometry_source,
            ),
            artifact_spec=ArtifactSpec(
                (
                    "field_csv",
                    "boundary_plot",
                    "animation_generator",
                    "operator_diagram",
                ),
                (
                    "python -m "
                    "the_nothingness_effect.mathematical_architecture.simulation"
                ),
            ),
            exact_semantics=False,
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/c_level.py"
            ),
        ),
    )
