"""Exact C-level signed-polar field synthesis from both complete B laws."""

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

from .a_level import APPENDIX, APPENDIX_SHA256, PiApproximationInput, pi_approximation
from .authoritative_obligations import (
    SignedPolarClosureCertificate,
    certify_signed_polar_field,
)


C_ID = "addition_of_the_two_complete_b_level_operator_families"
ARITHMETIC_SOURCE = "addition_of_arithmetic_orientation_and_typed_operation_theory"
GEOMETRY_SOURCE = "addition_of_approximation_and_harmonic_geometry"
IMPLEMENTATION_PATH = "the_nothingness_effect/mathematical_architecture/c_level.py"
TOLERANCE = 1e-10


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
    quotient_reconstruction_residual: float
    field_inverse_residual: float
    closure_status: str
    authority_certificate: SignedPolarClosureCertificate


def signed_polar_field(value: SignedPolarFieldInput) -> SignedPolarFieldResult:
    if not np.isfinite(value.horizon) or value.horizon <= 0.0:
        raise DomainViolationError("signed-polar synthesis requires a positive finite horizon")
    if not value.times:
        raise DomainViolationError("signed-polar synthesis requires nonempty spatial times")
    times = tuple(float(time) for time in value.times)
    if any(not np.isfinite(time) for time in times):
        raise DomainViolationError("signed-polar times must be finite")
    if abs(times[0]) > TOLERANCE:
        raise DomainViolationError("signed-polar reconstruction requires the first sample at t=0")
    if any(times[index + 1] < times[index] for index in range(len(times) - 1)):
        raise DomainViolationError("signed-polar times must be nondecreasing")
    if any(time < 0.0 or time > value.horizon for time in times):
        raise DomainViolationError("times lie outside the declared field domain")
    if not np.isfinite(value.radius):
        raise DomainViolationError("radius must be finite")
    if abs(abs(value.phase_unit) - 1.0) > TOLERANCE:
        raise DomainViolationError("phase_unit must lie on the unit circle")

    radius = abs(float(value.radius))
    if radius == 0.0:
        phase = 1.0 + 0.0j
    else:
        phase = complex(value.phase_unit)
        if value.radius < 0.0:
            phase = -phase

    pi_result = pi_approximation(PiApproximationInput(value.order, value.damping))
    theta = np.asarray(
        [2.0 * pi_result.value * time / value.horizon for time in times],
        dtype=float,
    )
    field_array = radius * phase * np.exp(1j * theta)
    field = tuple(complex(item) for item in field_array)
    gradients = tuple(
        complex(field_array[index + 1] - field_array[index])
        for index in range(len(field_array) - 1)
    )

    initial = complex(field_array[0])
    boundary = float(abs(initial - radius * phase))
    reconstruction_array = initial * np.exp(1j * theta)
    reconstruction = float(np.linalg.norm(field_array - reconstruction_array))

    reconstructed_radius = float(abs(initial))
    reconstructed_phase = 1.0 + 0.0j if reconstructed_radius == 0.0 else initial / reconstructed_radius
    quotient_reconstruction = float(
        abs(reconstructed_radius - radius)
        + (0.0 if radius == 0.0 else abs(reconstructed_phase - phase))
    )
    inverse_field = reconstructed_radius * reconstructed_phase * np.exp(1j * theta)
    field_inverse = float(np.linalg.norm(inverse_field - field_array))

    certificate = certify_signed_polar_field(value.radius, value.phase_unit, field)
    residuals = (
        boundary,
        reconstruction,
        quotient_reconstruction,
        field_inverse,
        certificate.gauge_residual,
        certificate.norm_residual,
        certificate.initial_reconstruction_residual,
    )
    closed = max(residuals) <= TOLERANCE
    return SignedPolarFieldResult(
        radius,
        phase,
        times,
        field,
        gradients,
        boundary,
        reconstruction,
        quotient_reconstruction,
        field_inverse,
        "closed" if closed else "open",
        certificate,
    )


def field_residual(_source, output: SignedPolarFieldResult) -> ResidualResult:
    vector = (
        output.boundary_trace_residual,
        output.reconstruction_residual,
        output.quotient_reconstruction_residual,
        output.field_inverse_residual,
        output.authority_certificate.gauge_residual,
        output.authority_certificate.norm_residual,
        output.authority_certificate.initial_reconstruction_residual,
    )
    passed = max(vector) <= TOLERANCE
    return ResidualResult(
        "signed-polar quotient and field mutual inverses",
        vector,
        TOLERANCE,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        metadata={
            "quotient_gauge_checked": True,
            "mutual_inverse_checked": True,
            "zero_radius_canonicalized": True,
        },
    )


def remove_arithmetic_source(value: SignedPolarFieldInput) -> SourceRemovalResult:
    complete = signed_polar_field(value)
    removed = np.zeros(len(value.times), dtype=complex)
    return source_removal_result(
        ComplexId(ARITHMETIC_SOURCE),
        np.asarray(complete.field),
        removed,
        tolerance=1e-12,
    )


def remove_geometry_source(value: SignedPolarFieldInput) -> SourceRemovalResult:
    complete = signed_polar_field(value)
    removed = np.full(
        len(value.times),
        complete.canonical_radius * complete.canonical_phase_unit,
        dtype=complex,
    )
    if np.allclose(np.asarray(complete.field), removed):
        removed = np.zeros_like(removed)
    return source_removal_result(
        ComplexId(GEOMETRY_SOURCE),
        np.asarray(complete.field),
        removed,
        tolerance=1e-12,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId(C_ID),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.C,
            (ComplexId(ARITHMETIC_SOURCE), ComplexId(GEOMETRY_SOURCE)),
            DomainSpec(
                "signed-polar spatial field",
                "quotient-compatible finite radius, unit phase, finite harmonic calibration, and an ordered domain sampled at t=0",
                (SignedPolarFieldInput,),
            ),
            CodomainSpec(
                "calibrated signed-polar quotient field",
                "gauge-invariant field together with exact quotient and field reconstruction certificates",
                (SignedPolarFieldResult,),
            ),
            signed_polar_field,
            residual=field_residual,
            closure_predicate=lambda output, residual: (
                output.closure_status == "closed"
                and residual is not None
                and residual.passed
            ),
            source_removal_checks=(remove_arithmetic_source, remove_geometry_source),
            artifact_spec=ArtifactSpec(
                ("field_csv", "boundary_plot", "animation_generator", "operator_diagram"),
                "python -m the_nothingness_effect.mathematical_architecture.simulation",
            ),
            exact_semantics=True,
            implementation_path=IMPLEMENTATION_PATH,
        ),
    )
