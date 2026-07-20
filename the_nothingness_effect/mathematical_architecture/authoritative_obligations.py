"""Typed finite obligations from the recertified Mathematical Closure appendix.

These helpers expose the source-level attainment, spectral, orientation, and
quotient conditions that were previously compressed into scalar proxy outputs.
They are executable witnesses only and do not replace the appendix proofs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)


APPENDIX = "appendix_tne_mathematical_closure_architecture.tex"
APPENDIX_SHA256 = "3cd520d5b025f6f241c7eb09417528276f0c6904e07aa088057c7b57803bf011"


@dataclass(frozen=True)
class OrientationTorsorCertificate:
    selected_orientation: int
    successor_index: int
    reconstructed_integer: int
    positive_specialization: tuple[int, int]
    negative_specialization: tuple[int, int]
    equivariance_residual: float
    gauge_reconstruction_residual: float


def certify_orientation_torsor(
    value: float,
    *,
    reversed_orientation: bool = False,
) -> OrientationTorsorCertificate:
    """Realize the two Unity orientations and reconstruct a nonzero integer."""

    ensure_finite(value, name="orientation value")
    scalar = float(value)
    if scalar == 0.0:
        raise DomainViolationError(
            "zero is the neutral boundary, not a third Unity orientation"
        )
    if not scalar.is_integer():
        raise DomainViolationError(
            "integer unfolding requires a nonzero integer-valued scalar"
        )
    integer = int(scalar)
    selected = 1 if integer > 0 else -1
    if reversed_orientation:
        selected *= -1
    index = abs(integer) - 1
    reconstructed = selected * (index + 1)
    positive = (1, -1)
    negative = (-1, 1)
    equivariance = float(abs(positive[1] - (-positive[0])))
    gauge = float(
        abs(positive[0] - (-negative[0]))
        + abs(positive[1] - (-negative[1]))
    )
    return OrientationTorsorCertificate(
        selected,
        index,
        reconstructed,
        positive,
        negative,
        equivariance,
        gauge,
    )


@dataclass(frozen=True)
class SpectralMinimizerCertificate:
    minimizer_indices: tuple[int, ...]
    minimum_value: float
    attainment_certified: bool
    uniqueness_certified: bool
    projector_idempotence_residual: float
    phase_invariance_residual: float
    compression_reconstruction_residual: float


def certify_spectral_minimizer(
    costs: tuple[float, ...],
    projector: np.ndarray,
    phase_action: np.ndarray,
    encoded_output: np.ndarray,
    *,
    representation_compact: bool,
    functional_lower_semicontinuous: bool,
    functional_strictly_convex: bool,
    tolerance: float = 1e-10,
) -> SpectralMinimizerCertificate:
    """Certify finite attainment and the phase-invariant minimizing image."""

    if not costs:
        raise DomainViolationError("spectral minimization requires candidates")
    ensure_finite(costs, name="spectral costs")
    minimum = float(min(costs))
    minimizers = tuple(
        index
        for index, cost in enumerate(costs)
        if abs(float(cost) - minimum) <= tolerance
    )
    p = np.asarray(projector, dtype=complex)
    u = np.asarray(phase_action, dtype=complex)
    output = np.asarray(encoded_output, dtype=complex)
    if p.ndim != 2 or p.shape[0] != p.shape[1]:
        raise DomainViolationError("minimizing projector must be square")
    if u.shape != p.shape or output.shape != (p.shape[0],):
        raise DomainViolationError(
            "phase action, projector, and encoded output require one common codomain"
        )
    ensure_finite((p, u, output), name="spectral minimizer witness")
    if abs(np.linalg.det(u)) <= tolerance:
        raise DomainViolationError("phase action must be invertible")
    attained = (
        representation_compact
        and functional_lower_semicontinuous
        and bool(minimizers)
    )
    unique = attained and functional_strictly_convex and len(minimizers) == 1
    idempotence = float(np.linalg.norm(p @ p - p))
    conjugated = u @ p @ np.linalg.inv(u)
    phase_residual = float(np.linalg.norm(conjugated - p))
    compression = float(np.linalg.norm((np.eye(p.shape[0]) - p) @ output))
    return SpectralMinimizerCertificate(
        minimizers,
        minimum,
        attained,
        unique,
        idempotence,
        phase_residual,
        compression,
    )


@dataclass(frozen=True)
class ResidualSpectralCertificate:
    errors: tuple[float, ...]
    mean_error: float
    centered_spectral_energy: float
    parseval_residual: float
    joint_certificate: float


def certify_residual_spectrum(
    errors: tuple[float, ...],
) -> ResidualSpectralCertificate:
    """Compute the normalized nonconstant residual energy and joint certificate."""

    if not errors:
        raise DomainViolationError("residual spectrum requires a nonempty history")
    ensure_finite(errors, name="approximation errors")
    array = np.asarray(errors, dtype=float)
    mean = float(np.mean(array))
    centered = array - mean
    energy = float(np.mean(np.abs(centered) ** 2))
    coefficients = np.fft.fft(centered, norm="ortho")
    spectral_energy = float(np.sum(np.abs(coefficients[1:]) ** 2) / array.size)
    parseval = float(abs(energy - spectral_energy))
    joint = float(max(abs(array[-1]), np.sqrt(energy), abs(mean)))
    return ResidualSpectralCertificate(
        tuple(float(item) for item in array),
        mean,
        energy,
        parseval,
        joint,
    )


@dataclass(frozen=True)
class PhaseHarmonicCertificate:
    phase_defined: bool
    first_mode_coefficient: complex
    first_mode_residual: float
    amplitude_reconstruction_residual: float
    half_turn_gauge_residual: float


def certify_phase_harmonic_embedding(
    amplitude: complex,
    theta: float,
    *,
    sample_count: int,
) -> PhaseHarmonicCertificate:
    """Verify the normalized phase orbit and its single first harmonic."""

    if sample_count < 4:
        raise DomainViolationError(
            "phase-harmonic embedding needs at least four samples"
        )
    ensure_finite((amplitude, theta), name="phase harmonic input")
    amplitude_value = complex(amplitude)
    if abs(amplitude_value) == 0.0:
        return PhaseHarmonicCertificate(False, 0j, 0.0, 0.0, 0.0)
    grid = 2.0 * np.pi * np.arange(sample_count) / sample_count
    orbit = amplitude_value * np.exp(1j * (float(theta) + grid))
    normalized = orbit / abs(amplitude_value)
    coefficients = np.fft.fft(normalized, norm="ortho")
    expected = np.zeros(sample_count, dtype=complex)
    expected[1] = np.sqrt(sample_count) * np.exp(
        1j * (np.angle(amplitude_value) + float(theta))
    )
    first_mode_residual = float(np.linalg.norm(coefficients - expected))
    amplitude_residual = float(
        np.linalg.norm(np.abs(orbit) - abs(amplitude_value))
    )
    half_turn = float(
        abs(
            (-amplitude_value) * np.exp(1j * float(theta))
            - amplitude_value * np.exp(1j * (float(theta) + np.pi))
        )
    )
    return PhaseHarmonicCertificate(
        True,
        complex(coefficients[1]),
        first_mode_residual,
        amplitude_residual,
        half_turn,
    )


@dataclass(frozen=True)
class OrientationGradedCompressionCertificate:
    transported_projector: np.ndarray
    projector_cocycle_residual: float
    phase_involution_residual: float
    compression_reconstruction_residual: float
    lossless: bool


def certify_orientation_graded_compression(
    projector: np.ndarray,
    phase_action: np.ndarray,
    encoded_output: np.ndarray,
    *,
    orientation: int,
    tolerance: float = 1e-10,
) -> OrientationGradedCompressionCertificate:
    """Transport the minimizing projector and localize compression loss."""

    if orientation not in (0, 1):
        raise DomainViolationError("projector orientation lies in C2")
    p = np.asarray(projector, dtype=complex)
    u = np.asarray(phase_action, dtype=complex)
    output = np.asarray(encoded_output, dtype=complex)
    if p.ndim != 2 or p.shape[0] != p.shape[1]:
        raise DomainViolationError("minimizing projector must be square")
    if u.shape != p.shape or output.shape != (p.shape[0],):
        raise DomainViolationError(
            "compressed operation requires one common spectral codomain"
        )
    ensure_finite((p, u, output), name="graded compression")
    if abs(np.linalg.det(u)) <= tolerance:
        raise DomainViolationError("phase action must be invertible")
    identity = np.eye(p.shape[0], dtype=complex)
    u_power = identity if orientation == 0 else u
    transported = u_power @ p @ np.linalg.inv(u_power)
    twice = u @ transported @ np.linalg.inv(u)
    cocycle_target = p if orientation == 1 else u @ p @ np.linalg.inv(u)
    cocycle = float(np.linalg.norm(twice - cocycle_target))
    involution = float(np.linalg.norm(u @ u - identity))
    compression = float(np.linalg.norm((identity - transported) @ output))
    return OrientationGradedCompressionCertificate(
        transported,
        cocycle,
        involution,
        compression,
        compression <= tolerance,
    )


@dataclass(frozen=True)
class SignedPolarClosureCertificate:
    gauge_residual: float
    norm_residual: float
    initial_reconstruction_residual: float


def certify_signed_polar_field(
    radius: float,
    phase_unit: complex,
    field: tuple[complex, ...],
) -> SignedPolarClosureCertificate:
    """Verify signed-polar gauge invariance and field reconstruction."""

    if not field:
        raise DomainViolationError("signed-polar closure requires a nonempty field")
    ensure_finite((radius, phase_unit, field), name="signed-polar field")
    canonical_radius = abs(float(radius))
    canonical_phase = complex(phase_unit)
    if radius < 0:
        canonical_phase = -canonical_phase
    values = np.asarray(field, dtype=complex)
    gauge_initial = (-float(radius)) * (-complex(phase_unit))
    canonical_initial = canonical_radius * canonical_phase
    gauge = float(abs(gauge_initial - canonical_initial))
    norm_residual = float(np.max(np.abs(np.abs(values) - canonical_radius)))
    initial = float(abs(values[0] - canonical_initial))
    return SignedPolarClosureCertificate(gauge, norm_residual, initial)
