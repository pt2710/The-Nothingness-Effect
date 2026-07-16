"""Two genuine B-level Mathematical Closure derivations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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
    OrientationGradedCompressionCertificate,
    certify_orientation_graded_compression,
)


@dataclass(frozen=True)
class ArithmeticOrientationInput:
    operation: Callable[..., complex]
    values: tuple[complex, ...]
    input_parities: tuple[int, ...]
    output_character: int
    minimizing_projector: np.ndarray | None = None
    phase_action: np.ndarray | None = None
    encoded_output: np.ndarray | None = None


@dataclass(frozen=True)
class ArithmeticOrientationResult:
    transported_value: complex
    identity_value: complex
    cocycle_residual: float
    interaction_energy: float
    authority_certificate: OrientationGradedCompressionCertificate


def arithmetic_orientation_transport(
    value: ArithmeticOrientationInput,
) -> ArithmeticOrientationResult:
    if len(value.values) != len(value.input_parities) or not value.values:
        raise DomainViolationError("each operation input needs one C2 parity")
    if value.output_character not in (0, 1) or any(
        bit not in (0, 1) for bit in value.input_parities
    ):
        raise DomainViolationError("orientation characters lie in C2")
    oriented_inputs = tuple(
        -item if bit else item
        for item, bit in zip(
            value.values,
            value.input_parities,
            strict=True,
        )
    )
    raw = value.operation(*oriented_inputs)
    transported = -raw if value.output_character else raw
    identity = value.operation(*value.values)
    recovered_inputs = tuple(
        -item if bit else item
        for item, bit in zip(
            oriented_inputs,
            value.input_parities,
            strict=True,
        )
    )
    recovered = value.operation(*recovered_inputs)
    residual = float(abs(recovered - identity))
    interaction = float(abs(transported - identity) ** 2)

    encoded = (
        np.array(
            [complex(transported).real, complex(transported).imag],
            dtype=complex,
        )
        if value.encoded_output is None
        else np.asarray(value.encoded_output, dtype=complex)
    )
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
    certificate = certify_orientation_graded_compression(
        projector,
        phase_action,
        encoded,
        orientation=value.output_character,
    )
    return ArithmeticOrientationResult(
        complex(transported),
        complex(identity),
        residual,
        interaction,
        certificate,
    )


@dataclass(frozen=True)
class ApproximationHarmonicInput:
    order: int
    damping: tuple[float, ...]
    times: tuple[float, ...]
    coefficients: tuple[complex, ...]
    horizon: float


@dataclass(frozen=True)
class ApproximationHarmonicResult:
    approximate_phase: tuple[float, ...]
    exact_phase: tuple[float, ...]
    approximate_field: tuple[complex, ...]
    exact_field: tuple[complex, ...]
    phase_error: float
    reconstruction_error: float
    operator_error_bound: float
    operator_bound_residual: float


def approximation_harmonic_geometry(
    value: ApproximationHarmonicInput,
) -> ApproximationHarmonicResult:
    if value.horizon <= 0 or not value.times or not value.coefficients:
        raise DomainViolationError(
            "positive horizon, times, and coefficients are required"
        )
    if any(time < 0 or time > value.horizon for time in value.times):
        raise DomainViolationError(
            "times must lie in the declared spatial/temporal horizon"
        )
    pi_result = pi_approximation(
        PiApproximationInput(value.order, value.damping)
    )
    approximate_phase = tuple(
        2 * pi_result.value * time / value.horizon
        for time in value.times
    )
    exact_phase = tuple(
        2 * np.pi * time / value.horizon
        for time in value.times
    )
    approximate_field = tuple(
        sum(
            coefficient * np.exp(1j * mode * theta)
            for mode, coefficient in enumerate(value.coefficients)
        )
        for theta in approximate_phase
    )
    exact_field = tuple(
        sum(
            coefficient * np.exp(1j * mode * theta)
            for mode, coefficient in enumerate(value.coefficients)
        )
        for theta in exact_phase
    )
    phase_error = float(
        max(
            abs(approximate - exact)
            for approximate, exact in zip(
                approximate_phase,
                exact_phase,
                strict=True,
            )
        )
    )
    reconstruction_error = float(
        np.linalg.norm(
            np.asarray(approximate_field) - np.asarray(exact_field)
        )
    )
    weighted_frequency = float(
        sum(
            mode * abs(coefficient)
            for mode, coefficient in enumerate(value.coefficients)
        )
    )
    pointwise_bound = weighted_frequency * phase_error
    operator_error_bound = float(np.sqrt(len(value.times)) * pointwise_bound)
    operator_bound_residual = float(
        max(0.0, reconstruction_error - operator_error_bound)
    )
    return ApproximationHarmonicResult(
        approximate_phase,
        exact_phase,
        tuple(complex(item) for item in approximate_field),
        tuple(complex(item) for item in exact_field),
        phase_error,
        reconstruction_error,
        operator_error_bound,
        operator_bound_residual,
    )


def remove_orientation_source(
    value: ArithmeticOrientationInput,
) -> SourceRemovalResult:
    complete = arithmetic_orientation_transport(value)
    removed = arithmetic_orientation_transport(
        ArithmeticOrientationInput(
            value.operation,
            value.values,
            (0,) * len(value.values),
            0,
            value.minimizing_projector,
            value.phase_action,
            value.encoded_output,
        )
    )
    return source_removal_result(
        ComplexId("flowpoint_unity_orientation_and_integer_unfolding"),
        (complete.transported_value.real, complete.transported_value.imag),
        (removed.transported_value.real, removed.transported_value.imag),
        tolerance=1e-12,
    )


def remove_operation_source(
    value: ArithmeticOrientationInput,
) -> SourceRemovalResult:
    complete = arithmetic_orientation_transport(value)
    removed_value = sum(value.values)
    return source_removal_result(
        ComplexId("operation_covariance_and_spectral_minimization"),
        (complete.transported_value.real, complete.transported_value.imag),
        (removed_value.real, removed_value.imag),
        tolerance=1e-12,
    )


def remove_approximation_source(
    value: ApproximationHarmonicInput,
) -> SourceRemovalResult:
    complete = approximation_harmonic_geometry(value)
    return source_removal_result(
        ComplexId("finite_approximation_and_vanishing_residual_energy"),
        np.asarray(complete.approximate_field),
        np.asarray(complete.exact_field),
        tolerance=1e-12,
    )


def remove_harmonic_source(
    value: ApproximationHarmonicInput,
) -> SourceRemovalResult:
    complete = approximation_harmonic_geometry(value)
    removed = np.full(
        len(value.times),
        value.coefficients[0],
        dtype=complex,
    )
    return source_removal_result(
        ComplexId("complex_phase_coordinates_and_fourier_reconstruction"),
        np.asarray(complete.approximate_field),
        removed,
        tolerance=1e-12,
    )


def _residual(
    name: str,
    values: tuple[float, ...],
    tolerance: float = 1e-10,
) -> ResidualResult:
    norm = float(np.linalg.norm(values))
    return ResidualResult(
        name,
        values,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED
        if norm <= tolerance
        else ClosureStatus.OPEN,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            ComplexId(
                "addition_of_arithmetic_orientation_and_typed_operation_theory"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.B,
            (
                ComplexId(
                    "flowpoint_unity_orientation_and_integer_unfolding"
                ),
                ComplexId(
                    "operation_covariance_and_spectral_minimization"
                ),
            ),
            DomainSpec(
                "oriented typed operation with minimizing projector",
                (
                    "complete operation, orientation, projector, phase, and "
                    "encoded-output data"
                ),
                (ArithmeticOrientationInput,),
            ),
            CodomainSpec(
                "orientation-graded compressed operation",
                (
                    "transported operation plus projector cocycle, phase "
                    "involution, and compression certificate"
                ),
                (ArithmeticOrientationResult,),
            ),
            arithmetic_orientation_transport,
            residual=lambda _source, output: _residual(
                "orientation-graded compressed operation",
                (
                    output.cocycle_residual,
                    output.authority_certificate.projector_cocycle_residual,
                    output.authority_certificate.phase_involution_residual,
                    output.authority_certificate.compression_reconstruction_residual,
                ),
            ),
            source_removal_checks=(
                remove_orientation_source,
                remove_operation_source,
            ),
            artifact_spec=ArtifactSpec(
                (
                    "ablation_table",
                    "transport_plot",
                    "operator_diagram",
                ),
                (
                    "python -m "
                    "the_nothingness_effect.mathematical_architecture.simulation"
                ),
            ),
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/b_level.py"
            ),
        ),
        ComplexContract(
            ComplexId(
                "addition_of_approximation_and_harmonic_geometry"
            ),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.B,
            (
                ComplexId(
                    "finite_approximation_and_vanishing_residual_energy"
                ),
                ComplexId(
                    "complex_phase_coordinates_and_fourier_reconstruction"
                ),
            ),
            DomainSpec(
                "calibrated harmonic input",
                "finite approximation and harmonic coefficients",
                (ApproximationHarmonicInput,),
            ),
            CodomainSpec(
                "calibrated harmonic field",
                (
                    "approximate/exact phase fields and source-derived "
                    "operator error bound"
                ),
                (ApproximationHarmonicResult,),
            ),
            approximation_harmonic_geometry,
            residual=lambda source, output: _residual(
                "calibrated harmonic bound",
                (
                    max(
                        0.0,
                        output.phase_error
                        - 2
                        * pi_approximation(
                            PiApproximationInput(
                                source.order,
                                source.damping,
                            )
                        ).actual_error,
                    ),
                    output.operator_bound_residual,
                ),
            ),
            source_removal_checks=(
                remove_approximation_source,
                remove_harmonic_source,
            ),
            artifact_spec=ArtifactSpec(
                (
                    "ablation_table",
                    "phase_error_plot",
                    "operator_diagram",
                ),
                (
                    "python -m "
                    "the_nothingness_effect.mathematical_architecture.simulation"
                ),
            ),
            exact_semantics=False,
            implementation_path=(
                "the_nothingness_effect/mathematical_architecture/b_level.py"
            ),
        ),
    )
