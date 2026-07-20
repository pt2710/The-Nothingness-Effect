"""Four A-level Mathematical Closure source laws."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)

from .authoritative_obligations import (
    APPENDIX,
    APPENDIX_SHA256,
    OrientationTorsorCertificate,
    PhaseHarmonicCertificate,
    ResidualSpectralCertificate,
    SpectralMinimizerCertificate,
    certify_orientation_torsor,
    certify_phase_harmonic_embedding,
    certify_residual_spectrum,
    certify_spectral_minimizer,
)


@dataclass(frozen=True)
class OrientationInput:
    value: float
    reversed_orientation: bool = False


@dataclass(frozen=True)
class OrientationResult:
    orientation: int
    magnitude: float
    integer_unfolding: tuple[int, ...]
    neutral_boundary: bool
    authority_certificate: OrientationTorsorCertificate


def orientation_unfolding(value: OrientationInput) -> OrientationResult:
    certificate = certify_orientation_torsor(
        value.value,
        reversed_orientation=value.reversed_orientation,
    )
    unfolding = tuple(
        certificate.selected_orientation * (index + 1)
        for index in range(certificate.successor_index + 1)
    )
    return OrientationResult(
        certificate.selected_orientation,
        abs(float(value.value)),
        unfolding,
        False,
        certificate,
    )


@dataclass(frozen=True)
class OperationCovarianceInput:
    operation: Callable[..., complex]
    values: tuple[complex, ...]
    output_parity: int
    spectral_costs: tuple[float, ...] = (0.0,)
    minimizing_projector: np.ndarray | None = None
    phase_action: np.ndarray | None = None
    encoded_output: np.ndarray | None = None
    representation_compact: bool = True
    functional_lower_semicontinuous: bool = True
    functional_strictly_convex: bool = True


@dataclass(frozen=True)
class OperationCovarianceResult:
    direct: complex
    transformed: complex
    residual: float
    covariant: bool
    authority_certificate: SpectralMinimizerCertificate


def operation_covariance(
    value: OperationCovarianceInput,
) -> OperationCovarianceResult:
    if value.output_parity not in (0, 1):
        raise DomainViolationError("output parity must lie in C2")
    if not value.values:
        raise DomainViolationError("operation covariance needs at least one input")
    ensure_finite(value.values, name="operation inputs")
    direct = value.operation(*value.values)
    transformed_inputs = tuple(-item for item in value.values)
    transformed = value.operation(*transformed_inputs)
    oriented_direct = direct if value.output_parity == 0 else -direct
    ensure_finite((direct, transformed), name="operation outputs")
    residual = float(abs(oriented_direct - transformed))

    if value.encoded_output is None:
        encoded = np.array(
            [complex(direct).real, complex(direct).imag],
            dtype=complex,
        )
    else:
        encoded = np.asarray(value.encoded_output, dtype=complex)
        if encoded.ndim != 1 or encoded.size < 1:
            raise DomainViolationError("encoded operation output must be a vector")
    dimension = encoded.size
    projector = (
        np.eye(dimension, dtype=complex)
        if value.minimizing_projector is None
        else np.asarray(value.minimizing_projector, dtype=complex)
    )
    phase_action = (
        np.eye(dimension, dtype=complex)
        if value.phase_action is None
        else np.asarray(value.phase_action, dtype=complex)
    )
    certificate = certify_spectral_minimizer(
        value.spectral_costs,
        projector,
        phase_action,
        encoded,
        representation_compact=value.representation_compact,
        functional_lower_semicontinuous=(
            value.functional_lower_semicontinuous
        ),
        functional_strictly_convex=value.functional_strictly_convex,
    )
    return OperationCovarianceResult(
        complex(direct),
        complex(transformed),
        residual,
        residual <= 1e-10,
        certificate,
    )


@dataclass(frozen=True)
class PiApproximationInput:
    order: int
    damping: tuple[float, ...] = ()


@dataclass(frozen=True)
class PiApproximationResult:
    order: int
    value: float
    damping_defect: float
    actual_error: float
    certified_error_bound: float
    convergence_condition_observed: bool
    authority_certificate: ResidualSpectralCertificate


def _pi_prefix(order: int, damping: tuple[float, ...]) -> tuple[float, float]:
    terms = [
        ((-1) ** k) * (1.0 - damping[k]) / (2 * k + 1)
        for k in range(order + 1)
    ]
    defect = 4.0 * sum(
        ((-1) ** k) * damping[k] / (2 * k + 1)
        for k in range(order + 1)
    )
    return 4.0 * sum(terms), defect


def pi_approximation(value: PiApproximationInput) -> PiApproximationResult:
    if value.order < 0:
        raise DomainViolationError("approximation order must be non-negative")
    if value.damping and len(value.damping) != value.order + 1:
        raise DomainViolationError(
            "damping must be empty or contain order+1 values"
        )
    damping = value.damping or (0.0,) * (value.order + 1)
    ensure_finite(damping, name="damping sequence")
    approximation, defect = _pi_prefix(value.order, damping)
    actual_error = abs(np.pi - approximation)
    bound = 4.0 / (2 * value.order + 3) + abs(defect)
    errors = tuple(
        float(np.pi - _pi_prefix(index, damping[: index + 1])[0])
        for index in range(value.order + 1)
    )
    spectral = certify_residual_spectrum(errors)
    return PiApproximationResult(
        value.order,
        approximation,
        defect,
        actual_error,
        bound,
        (not value.damping) or abs(defect) <= bound,
        spectral,
    )


@dataclass(frozen=True)
class PhaseCoordinateInput:
    amplitude: complex
    theta: float
    samples: tuple[complex, ...]


@dataclass(frozen=True)
class PhaseCoordinateResult:
    coordinate: complex
    cosine_coordinate: float
    sine_coordinate: float
    periodicity_residual: float
    fourier_coefficients: tuple[complex, ...]
    reconstruction_residual: float
    parseval_residual: float
    authority_certificate: PhaseHarmonicCertificate


def phase_coordinates(value: PhaseCoordinateInput) -> PhaseCoordinateResult:
    ensure_finite(
        (value.amplitude, value.theta, value.samples),
        name="phase data",
    )
    if not value.samples:
        raise DomainViolationError(
            "Fourier reconstruction requires a nonempty finite sample"
        )
    coordinate = value.amplitude * np.exp(1j * value.theta)
    periodic = value.amplitude * np.exp(1j * (value.theta + 2 * np.pi))
    sample_array = np.asarray(value.samples, dtype=complex)
    coefficients = np.fft.fft(sample_array, norm="ortho")
    reconstruction = np.fft.ifft(coefficients, norm="ortho")
    reconstruction_residual = float(
        np.linalg.norm(reconstruction - sample_array)
    )
    parseval_residual = float(
        abs(
            np.vdot(sample_array, sample_array).real
            - np.vdot(coefficients, coefficients).real
        )
    )
    certificate = certify_phase_harmonic_embedding(
        value.amplitude,
        value.theta,
        sample_count=max(4, len(value.samples)),
    )
    return PhaseCoordinateResult(
        complex(coordinate),
        float(np.real(coordinate)),
        float(np.imag(coordinate)),
        float(abs(periodic - coordinate)),
        tuple(complex(item) for item in coefficients),
        reconstruction_residual,
        parseval_residual,
        certificate,
    )


def _residual(name: str, values: tuple[float, ...]) -> ResidualResult:
    norm = float(np.linalg.norm(values))
    return ResidualResult(
        name,
        values,
        1e-10,
        norm <= 1e-10,
        ClosureStatus.SATISFIED
        if norm <= 1e-10
        else ClosureStatus.OPEN,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId(
                "flowpoint_unity_orientation_and_integer_unfolding"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "oriented nonzero integer",
                "finite nonzero integer-valued real scalar",
                (OrientationInput,),
            ),
            CodomainSpec(
                "orientation torsor and unfolding",
                (
                    "orientation in {-1,+1}, successor index, and exact "
                    "integer reconstruction"
                ),
                (OrientationResult,),
            ),
            orientation_unfolding,
            residual=lambda _source, output: _residual(
                "orientation torsor",
                (
                    output.authority_certificate.equivariance_residual,
                    output.authority_certificate.gauge_reconstruction_residual,
                    float(
                        output.authority_certificate.reconstructed_integer
                        != output.integer_unfolding[-1]
                    ),
                ),
            ),
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/a_level.py"
            ),
        ),
        ComplexContract(
            ComplexId(
                "operation_covariance_and_spectral_minimization"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "typed partial operation and spectral witness",
                (
                    "callable, admitted operands, minimizer assumptions, "
                    "projector, and phase action"
                ),
                (OperationCovarianceInput,),
            ),
            CodomainSpec(
                "covariance and spectral minimizer result",
                (
                    "operation residual plus attainment, invariance, and "
                    "compression certificates"
                ),
                (OperationCovarianceResult,),
            ),
            operation_covariance,
            residual=lambda _source, output: _residual(
                "operation covariance and spectral minimization",
                (
                    output.residual,
                    0.0
                    if output.authority_certificate.attainment_certified
                    else 1.0,
                    output.authority_certificate.projector_idempotence_residual,
                    output.authority_certificate.phase_invariance_residual,
                    output.authority_certificate.compression_reconstruction_residual,
                ),
            ),
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/a_level.py"
            ),
        ),
        ComplexContract(
            ComplexId(
                "finite_approximation_and_vanishing_residual_energy"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "finite damped Leibniz prefix",
                "order and declared damping",
                (PiApproximationInput,),
            ),
            CodomainSpec(
                "bounded approximation and normalized residual spectrum",
                (
                    "value, damping defect, certified scalar bound, mean, "
                    "and nonconstant energy"
                ),
                (PiApproximationResult,),
            ),
            pi_approximation,
            residual=lambda _source, output: _residual(
                "pi approximation and residual spectrum",
                (
                    max(
                        0.0,
                        output.actual_error
                        - output.certified_error_bound,
                    ),
                    output.authority_certificate.parseval_residual,
                ),
            ),
            exact_semantics=False,
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/a_level.py"
            ),
        ),
        ComplexContract(
            ComplexId(
                "complex_phase_coordinates_and_fourier_reconstruction"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec(
                "complex phase and finite samples",
                "finite amplitude, phase, and sample",
                (PhaseCoordinateInput,),
            ),
            CodomainSpec(
                "phase/Fourier reconstruction",
                (
                    "unitary finite transform and phase-first-harmonic "
                    "certificate"
                ),
                (PhaseCoordinateResult,),
            ),
            phase_coordinates,
            residual=lambda _source, output: _residual(
                "phase and Fourier reconstruction",
                (
                    output.periodicity_residual,
                    output.reconstruction_residual,
                    output.parseval_residual,
                    output.authority_certificate.first_mode_residual,
                    output.authority_certificate.amplitude_reconstruction_residual,
                    output.authority_certificate.half_turn_gauge_residual,
                ),
            ),
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/a_level.py"
            ),
        ),
    )
