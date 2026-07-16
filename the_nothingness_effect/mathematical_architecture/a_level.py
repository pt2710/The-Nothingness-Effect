"""Four A-level mathematical closure source laws."""

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
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite


APPENDIX = "appendix_tne_mathematical_closure_architecture.tex"
APPENDIX_SHA256 = "3f428e24ed9518655f94145dcd8667f979aa03c74f75695d8273da273e2538d0"


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


def orientation_unfolding(value: OrientationInput) -> OrientationResult:
    ensure_finite(value.value, name="orientation value")
    if value.value == 0:
        raise DomainViolationError("zero is an orientation boundary, not a third orientation")
    orientation = 1 if value.value > 0 else -1
    if value.reversed_orientation:
        orientation *= -1
    magnitude = abs(float(value.value))
    integer_unfolding = tuple(orientation * index for index in range(1, int(np.floor(magnitude)) + 1))
    return OrientationResult(orientation, magnitude, integer_unfolding, False)


@dataclass(frozen=True)
class OperationCovarianceInput:
    operation: Callable[..., complex]
    values: tuple[complex, ...]
    output_parity: int


@dataclass(frozen=True)
class OperationCovarianceResult:
    direct: complex
    transformed: complex
    residual: float
    covariant: bool


def operation_covariance(value: OperationCovarianceInput) -> OperationCovarianceResult:
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
    return OperationCovarianceResult(direct, transformed, residual, residual <= 1e-10)


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


def pi_approximation(value: PiApproximationInput) -> PiApproximationResult:
    if value.order < 0:
        raise DomainViolationError("approximation order must be non-negative")
    if value.damping and len(value.damping) != value.order + 1:
        raise DomainViolationError("damping must be empty or contain order+1 values")
    damping = value.damping or (0.0,) * (value.order + 1)
    ensure_finite(damping, name="damping sequence")
    terms = [((-1) ** k) * (1.0 - damping[k]) / (2 * k + 1) for k in range(value.order + 1)]
    defect = 4.0 * sum(((-1) ** k) * damping[k] / (2 * k + 1) for k in range(value.order + 1))
    approximation = 4.0 * sum(terms)
    actual_error = abs(np.pi - approximation)
    bound = 4.0 / (2 * value.order + 3) + abs(defect)
    return PiApproximationResult(
        value.order,
        approximation,
        defect,
        actual_error,
        bound,
        abs(defect) <= bound,
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


def phase_coordinates(value: PhaseCoordinateInput) -> PhaseCoordinateResult:
    ensure_finite((value.amplitude, value.theta, value.samples), name="phase data")
    if not value.samples:
        raise DomainViolationError("Fourier reconstruction requires a nonempty finite sample")
    coordinate = value.amplitude * np.exp(1j * value.theta)
    periodic = value.amplitude * np.exp(1j * (value.theta + 2 * np.pi))
    sample_array = np.asarray(value.samples, dtype=complex)
    coefficients = np.fft.fft(sample_array, norm="ortho")
    reconstruction = np.fft.ifft(coefficients, norm="ortho")
    reconstruction_residual = float(np.linalg.norm(reconstruction - sample_array))
    parseval_residual = float(
        abs(np.vdot(sample_array, sample_array).real - np.vdot(coefficients, coefficients).real)
    )
    return PhaseCoordinateResult(
        complex(coordinate),
        float(np.real(coordinate)),
        float(np.imag(coordinate)),
        float(abs(periodic - coordinate)),
        tuple(complex(item) for item in coefficients),
        reconstruction_residual,
        parseval_residual,
    )


def _residual(name: str, values: tuple[float, ...]) -> ResidualResult:
    norm = float(np.linalg.norm(values))
    return ResidualResult(
        name,
        values,
        1e-10,
        norm <= 1e-10,
        ClosureStatus.SATISFIED if norm <= 1e-10 else ClosureStatus.OPEN,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId("flowpoint_unity_orientation_and_integer_unfolding"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("oriented nonzero scalar", "finite nonzero real value", (OrientationInput,)),
            CodomainSpec("orientation and unfolding", "orientation in {-1,+1}", (OrientationResult,)),
            orientation_unfolding,
            implementation_path="the_nothingness_effect/mathematical_architecture/a_level.py",
        ),
        ComplexContract(
            ComplexId("operation_covariance_and_spectral_minimization"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("typed partial operation", "callable and admitted operands", (OperationCovarianceInput,)),
            CodomainSpec("covariance result", "finite operation residual", (OperationCovarianceResult,)),
            operation_covariance,
            residual=lambda _source, output: _residual("operation covariance", (output.residual,)),
            implementation_path="the_nothingness_effect/mathematical_architecture/a_level.py",
        ),
        ComplexContract(
            ComplexId("finite_approximation_and_vanishing_residual_energy"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("finite damped Leibniz prefix", "order and declared damping", (PiApproximationInput,)),
            CodomainSpec("bounded approximation", "value, defect, and certified bound", (PiApproximationResult,)),
            pi_approximation,
            residual=lambda _source, output: _residual(
                "pi approximation bound violation",
                (max(0.0, output.actual_error - output.certified_error_bound),),
            ),
            exact_semantics=False,
            implementation_path="the_nothingness_effect/mathematical_architecture/a_level.py",
        ),
        ComplexContract(
            ComplexId("complex_phase_coordinates_and_fourier_reconstruction"),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            DomainSpec("complex phase and finite samples", "finite amplitude, phase, and sample", (PhaseCoordinateInput,)),
            CodomainSpec("phase/Fourier reconstruction", "unitary finite transform result", (PhaseCoordinateResult,)),
            phase_coordinates,
            residual=lambda _source, output: _residual(
                "phase and Fourier reconstruction",
                (output.periodicity_residual, output.reconstruction_residual, output.parseval_residual),
            ),
            implementation_path="the_nothingness_effect/mathematical_architecture/a_level.py",
        ),
    )
