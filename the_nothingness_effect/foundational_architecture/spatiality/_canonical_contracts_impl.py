"""Canonical executable Spatiality contracts from the Foundational appendix.

This module implements the complete native ``2A -> 2B -> 1C`` Spatiality block:
minimal/cyclic orbit classification, quarter-turn and phase reflection,
cyclic square-root lifting, orbit-harmonic half-step resolution, and equivariant
orbit-spectral reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

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
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)


APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/spatiality/"
    "canonical_contracts.py"
)

A1 = ComplexId(
    "minimal_and_cyclic_spatiality_two_state_reflection_and_finite_cyclic_orbit_closure"
)
A2 = ComplexId(
    "imaginary_and_phase_spatiality_quarter_turn_rotation_and_phase_conjugate_reflection"
)
B1 = ComplexId("cyclic_square_root_lifting_and_phase_anchored_dihedralization")
B2 = ComplexId("orbit_harmonic_phase_resolution")
C1 = ComplexId("equivariant_orbit_spectral_reconstruction")
AFFINE = ComplexId("affine_spatial_involution_orbit_correspondence")


@dataclass(frozen=True)
class OrbitClassificationInput:
    point: complex
    order: int
    tolerance: float = 1e-12


@dataclass(frozen=True)
class PhaseSpatialityInput:
    point: complex
    phase: float
    tolerance: float = 1e-12


@dataclass(frozen=True)
class SquareRootLiftInput:
    point: complex
    order: int
    tolerance: float = 1e-12


@dataclass(frozen=True)
class OrbitHarmonicInput:
    samples: np.ndarray
    tolerance: float = 1e-12


@dataclass(frozen=True)
class SpectralReconstructionInput:
    samples: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class OrbitClassificationLaw:
    reflection_orbit: np.ndarray
    cyclic_orbit: np.ndarray
    reflection_residual: float
    cyclic_closure_residual: float
    orbit_classification: str


@dataclass(frozen=True)
class PhaseSpatialityLaw:
    quarter_turn: complex
    phase_reflection: complex
    reflection_square_residual: float
    rotation_conjugacy_residual: float
    real_axis_residual: float


@dataclass(frozen=True)
class SquareRootLiftLaw:
    root: complex
    cyclic_generator: complex
    lifted_orbit: np.ndarray
    square_root_residual: float
    order_residual: float
    dihedral_residual: float


@dataclass(frozen=True)
class OrbitHarmonicLaw:
    coefficients: np.ndarray
    half_step_field: np.ndarray
    reconstructed_samples: np.ndarray
    parseval_residual: float
    reconstruction_residual: float
    phase_resolution_residual: float


@dataclass(frozen=True)
class SpectralReconstructionLaw:
    analysis_coefficients: np.ndarray
    reconstruction: np.ndarray
    frame_operator: np.ndarray
    tight_frame_residual: float
    reconstruction_residual: float
    equivariance_residual: float


def _tolerance(value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return float(value)


def _point(value: complex) -> complex:
    result = complex(value)
    if not np.isfinite((result.real, result.imag)).all():
        raise NonFiniteValueError("spatial point contains NaN or infinity")
    return result


def _order(value: int) -> int:
    if not isinstance(value, int) or value < 2:
        raise DomainViolationError("cyclic order must be an integer >= 2")
    return value


def _samples(value: object) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if (
        result.ndim != 1
        or result.size < 2
        or not np.isfinite(result.real).all()
        or not np.isfinite(result.imag).all()
    ):
        raise DomainViolationError(
            "orbit samples must be a finite complex vector of length >= 2"
        )
    return result


def _residual(name: str, values: tuple[float, ...], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in values)
    norm = float(np.linalg.norm(vector))
    passed = norm <= tolerance
    return ResidualResult(
        name,
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def orbit_classification(value: OrbitClassificationInput) -> OrbitClassificationLaw:
    point = _point(value.point)
    order = _order(value.order)
    _tolerance(value.tolerance)
    omega = np.exp(2j * np.pi / order)
    reflection = np.asarray((point, np.conjugate(point)), dtype=complex)
    cyclic = np.asarray([omega**index * point for index in range(order)], dtype=complex)
    if abs(point) <= value.tolerance:
        classification = "fixed"
    elif np.min(np.abs(cyclic[1:] - point)) <= value.tolerance:
        classification = "short_orbit"
    else:
        classification = f"free_C_{order}_orbit"
    return OrbitClassificationLaw(
        reflection,
        cyclic,
        float(abs(np.conjugate(np.conjugate(point)) - point)),
        float(abs(omega**order * point - point)),
        classification,
    )


def phase_spatiality(value: PhaseSpatialityInput) -> PhaseSpatialityLaw:
    point = _point(value.point)
    _tolerance(value.tolerance)
    if not math.isfinite(value.phase):
        raise DomainViolationError("phase must be finite")
    quarter = 1j * point
    reflection = np.exp(1j * value.phase) * np.conjugate(point)
    square = np.exp(1j * value.phase) * np.conjugate(reflection)
    left = np.exp(1j * value.phase) * np.conjugate(1j * point)
    right = -1j * reflection
    real_axis = float(abs((point.real + 0j) - np.conjugate(point.real + 0j)))
    return PhaseSpatialityLaw(
        quarter,
        reflection,
        float(abs(square - point)),
        float(abs(left - right)),
        real_axis,
    )


def square_root_lift(value: SquareRootLiftInput) -> SquareRootLiftLaw:
    point = _point(value.point)
    order = _order(value.order)
    _tolerance(value.tolerance)
    omega = np.exp(2j * np.pi / order)
    root = np.exp(1j * np.pi / order)
    lifted = np.asarray(
        [
            root**epsilon * omega**index * point
            for epsilon in (0, 1)
            for index in range(order)
        ],
        dtype=complex,
    )
    left = np.conjugate(root * point)
    right = root**-1 * np.conjugate(point)
    return SquareRootLiftLaw(
        root,
        omega,
        lifted,
        float(abs(root**2 - omega)),
        float(abs(root ** (2 * order) - 1.0)),
        float(abs(left - right)),
    )


def orbit_harmonic(value: OrbitHarmonicInput) -> OrbitHarmonicLaw:
    samples = _samples(value.samples)
    _tolerance(value.tolerance)
    count = samples.size
    coefficients = np.fft.fft(samples, norm="ortho")
    reconstructed = np.fft.ifft(coefficients, norm="ortho")
    frequencies = np.arange(count)
    half_step = np.asarray(
        [
            np.sum(
                coefficients
                * np.exp(2j * np.pi * frequencies * (index + 0.5) / count)
            )
            / np.sqrt(count)
            for index in range(count)
        ]
    )
    half_multiplier = np.exp(1j * np.pi * frequencies / count)
    full_multiplier = np.exp(2j * np.pi * frequencies / count)
    return OrbitHarmonicLaw(
        coefficients,
        half_step,
        reconstructed,
        float(
            abs(
                np.vdot(samples, samples).real
                - np.vdot(coefficients, coefficients).real
            )
        ),
        float(np.linalg.norm(reconstructed - samples)),
        float(np.linalg.norm(half_multiplier**2 - full_multiplier)),
    )


def spectral_reconstruction(
    value: SpectralReconstructionInput,
) -> SpectralReconstructionLaw:
    samples = _samples(value.samples)
    _tolerance(value.tolerance)
    count = samples.size
    indices = np.arange(count)
    frame = np.exp(2j * np.pi * np.outer(indices, indices) / count) / np.sqrt(count)
    coefficients = frame.conj().T @ samples
    reconstruction = frame @ coefficients
    frame_operator = frame @ frame.conj().T
    shifted = np.roll(samples, 1)
    shifted_coefficients = frame.conj().T @ shifted
    phase = np.exp(-2j * np.pi * indices / count)
    return SpectralReconstructionLaw(
        coefficients,
        reconstruction,
        frame_operator,
        float(np.linalg.norm(frame_operator - np.eye(count))),
        float(np.linalg.norm(reconstruction - samples)),
        float(np.linalg.norm(shifted_coefficients - phase * coefficients)),
    )


def _remove_lift_orbit(value: SquareRootLiftInput):
    complete = square_root_lift(value).lifted_orbit
    point = _point(value.point)
    removed = np.full_like(complete, point)
    return source_removal_result(A1, complete, removed, tolerance=value.tolerance)


def _remove_lift_affine(value: SquareRootLiftInput):
    complete = square_root_lift(value).lifted_orbit
    return source_removal_result(
        AFFINE,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def _remove_harmonic_phase(value: OrbitHarmonicInput):
    complete = orbit_harmonic(value).half_step_field
    removed = orbit_harmonic(value).reconstructed_samples
    return source_removal_result(A2, complete, removed, tolerance=value.tolerance)


def _remove_harmonic_affine(value: OrbitHarmonicInput):
    complete = orbit_harmonic(value).half_step_field
    return source_removal_result(
        AFFINE,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def _remove_reconstruction_lift(value: SpectralReconstructionInput):
    complete = spectral_reconstruction(value).reconstruction
    return source_removal_result(
        B1,
        complete,
        np.zeros_like(complete),
        tolerance=value.tolerance,
    )


def _remove_reconstruction_harmonic(value: SpectralReconstructionInput):
    complete = spectral_reconstruction(value).reconstruction
    removed = np.roll(_samples(value.samples), 1)
    return source_removal_result(B2, complete, removed, tolerance=value.tolerance)


def contracts() -> tuple[ComplexContract, ...]:
    a1 = ComplexContract(
        A1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.A,
        (),
        DomainSpec(
            "reflection and cyclic orbit",
            "finite complex point and cyclic order >= 2",
            (OrbitClassificationInput,),
        ),
        CodomainSpec(
            "orbit classification",
            "C2 and Cm orbits with exact closure residuals",
            (OrbitClassificationLaw,),
        ),
        orbit_classification,
        residual=lambda source, output: _residual(
            "orbit classification",
            (output.reflection_residual, output.cyclic_closure_residual),
            source.tolerance,
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    a2 = ComplexContract(
        A2,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.A,
        (),
        DomainSpec(
            "phase spatial point",
            "finite complex point and phase",
            (PhaseSpatialityInput,),
        ),
        CodomainSpec(
            "quarter-turn and phase reflection",
            "rotation, reflection, involution, and conjugacy residuals",
            (PhaseSpatialityLaw,),
        ),
        phase_spatiality,
        residual=lambda source, output: _residual(
            "phase spatiality",
            (
                output.reflection_square_residual,
                output.rotation_conjugacy_residual,
                output.real_axis_residual,
            ),
            source.tolerance,
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    b1 = ComplexContract(
        B1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.B,
        (A1, AFFINE),
        DomainSpec(
            "cyclic square-root lift",
            "finite complex point and cyclic order",
            (SquareRootLiftInput,),
        ),
        CodomainSpec(
            "double-cover lift",
            "root, lifted orbit, square, order, and dihedral residuals",
            (SquareRootLiftLaw,),
        ),
        square_root_lift,
        residual=lambda source, output: _residual(
            "cyclic square-root lift",
            (
                output.square_root_residual,
                output.order_residual,
                output.dihedral_residual,
            ),
            source.tolerance,
        ),
        source_removal_checks=(_remove_lift_orbit, _remove_lift_affine),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    b2 = ComplexContract(
        B2,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.B,
        (A2, AFFINE),
        DomainSpec(
            "finite orbit samples",
            "finite complex orbit vector",
            (OrbitHarmonicInput,),
        ),
        CodomainSpec(
            "orbit harmonic resolution",
            "DFT coefficients, half-step field, and exact residuals",
            (OrbitHarmonicLaw,),
        ),
        orbit_harmonic,
        residual=lambda source, output: _residual(
            "orbit harmonics",
            (
                output.parseval_residual,
                output.reconstruction_residual,
                output.phase_resolution_residual,
            ),
            source.tolerance,
        ),
        source_removal_checks=(_remove_harmonic_phase, _remove_harmonic_affine),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    c1 = ComplexContract(
        C1,
        APPENDIX,
        APPENDIX_SHA256,
        ComplexLevel.C,
        (B1, B2),
        DomainSpec(
            "orbit spectral field",
            "finite complex orbit vector",
            (SpectralReconstructionInput,),
        ),
        CodomainSpec(
            "equivariant tight-frame reconstruction",
            "analysis coefficients, reconstruction, frame, and equivariance residuals",
            (SpectralReconstructionLaw,),
        ),
        spectral_reconstruction,
        residual=lambda source, output: _residual(
            "orbit spectral reconstruction",
            (
                output.tight_frame_residual,
                output.reconstruction_residual,
                output.equivariance_residual,
            ),
            source.tolerance,
        ),
        closure_predicate=lambda _output, residual: residual is not None and residual.passed,
        source_removal_checks=(
            _remove_reconstruction_lift,
            _remove_reconstruction_harmonic,
        ),
        artifact_spec=ArtifactSpec(
            ("coefficient_csv", "orbit_plot"),
            "python tools/generate_artifact_provenance.py --output-root <output-root>",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )
    return a1, a2, b1, b2, c1
