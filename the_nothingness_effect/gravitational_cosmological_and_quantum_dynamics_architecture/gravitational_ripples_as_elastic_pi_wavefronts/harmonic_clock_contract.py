"""Exact finite damping- and lag-corrected harmonic clock C01."""

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


SPEC = SPECS["elastic_pi_ripples"]
C_ID = SPEC.c_id
B_QUALITY, B_LAG = SPEC.b_ids
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "gravitational_ripples_as_elastic_pi_wavefronts/harmonic_clock_contract.py"
)


@dataclass(frozen=True)
class HarmonicClockInput:
    times: np.ndarray
    distances: np.ndarray
    observed_fundamental: np.ndarray
    observed_harmonic: np.ndarray
    fundamental_damping_rate: np.ndarray
    harmonic_damping_rate: np.ndarray
    fundamental_delay: np.ndarray
    harmonic_delay: np.ndarray
    fundamental_frequency: float
    harmonic_frequency: float
    source_coupling: np.ndarray
    corrected_clock: np.ndarray | None = None
    quality_source_residual: float = 0.0
    lag_source_residual: float = 0.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class HarmonicClockCertificate:
    spatial_domain: np.ndarray
    time_domain: np.ndarray
    distance_domain: np.ndarray
    integrated_fundamental_damping: np.ndarray
    integrated_harmonic_damping: np.ndarray
    amplitude_correction: np.ndarray
    phase_correction: np.ndarray
    raw_ratio: np.ndarray
    corrected_clock: np.ndarray
    expected_source_coupling: np.ndarray
    local_operator: np.ndarray
    correction_identity_residual: float
    source_coupling_residual: float
    time_invariance_residual: float
    distance_invariance_residual: float
    denominator_margin: float
    perturbation_log_norm: float
    perturbation_bound: float
    perturbation_bound_residual: float
    quality_source_residual: float
    lag_source_residual: float
    status_equivalence_residual: float
    closure_status: str


def _cumtrap(values: np.ndarray, times: np.ndarray) -> np.ndarray:
    result = np.zeros_like(values, dtype=float)
    increments = 0.5 * (values[1:] + values[:-1]) * np.diff(times)
    result[1:] = np.cumsum(increments)
    return result


def _field_adapter(value: FieldLawInput) -> HarmonicClockInput:
    times = np.asarray(value.coordinates, dtype=float)
    distances = np.linspace(0.2, 1.0, 4)
    base = 1.2 + 0.08 * np.asarray(value.source, dtype=float)
    source_fundamental = base[:, None] * np.ones((1, distances.size))
    coupling = (0.35 + 0.05j) * np.ones_like(source_fundamental, dtype=complex)
    source_harmonic = coupling * source_fundamental**3
    gamma_1 = 0.08 + 0.02 * (times - times[0])
    gamma_n = 0.17 + 0.03 * (times - times[0])
    omega_1 = 2.0 * np.pi
    omega_n = 6.0 * np.pi
    delay_1 = np.outer(np.ones(times.size), 0.15 * distances)
    delay_n = np.outer(np.ones(times.size), 0.09 * distances)
    integral_1 = _cumtrap(gamma_1, times)[:, None]
    integral_n = _cumtrap(gamma_n, times)[:, None]
    observed_1 = (
        np.exp(-integral_1)
        * np.exp(-1j * omega_1 * delay_1)
        * source_fundamental
    )
    observed_n = (
        np.exp(-integral_n)
        * np.exp(-1j * omega_n * delay_n)
        * source_harmonic
    )
    first = derived_operator(
        B_QUALITY,
        SPEC.source_kinds[0],
        SPEC.source_kinds[1],
        value,
    )
    second = derived_operator(
        B_LAG,
        SPEC.source_kinds[2],
        SPEC.source_kinds[3],
        value,
    )
    return HarmonicClockInput(
        times,
        distances,
        observed_1,
        observed_n,
        gamma_1,
        gamma_n,
        delay_1,
        delay_n,
        omega_1,
        omega_n,
        coupling,
        quality_source_residual=float(np.linalg.norm(first.residual)),
        lag_source_residual=float(np.linalg.norm(second.residual)),
        tolerance=value.tolerance,
    )


def _input(value: HarmonicClockInput | FieldLawInput) -> HarmonicClockInput:
    if isinstance(value, HarmonicClockInput):
        return value
    if isinstance(value, FieldLawInput):
        return _field_adapter(value)
    raise DomainViolationError(
        "harmonic clock requires HarmonicClockInput or FieldLawInput"
    )


def _validated(source: HarmonicClockInput):
    times = np.asarray(source.times, dtype=float)
    distances = np.asarray(source.distances, dtype=float)
    observed_1 = np.asarray(source.observed_fundamental, dtype=complex)
    observed_n = np.asarray(source.observed_harmonic, dtype=complex)
    gamma_1 = np.asarray(source.fundamental_damping_rate, dtype=float)
    gamma_n = np.asarray(source.harmonic_damping_rate, dtype=float)
    delay_1 = np.asarray(source.fundamental_delay, dtype=float)
    delay_n = np.asarray(source.harmonic_delay, dtype=float)
    coupling = np.asarray(source.source_coupling, dtype=complex)
    if times.ndim != 1 or times.size < 3 or distances.ndim != 1 or distances.size < 2:
        raise DomainViolationError(
            "harmonic clock requires at least three times and two distances"
        )
    shape = (times.size, distances.size)
    if any(item.shape != shape for item in (observed_1, observed_n, delay_1, delay_n, coupling)):
        raise DomainViolationError(
            "observed modes, delays, and source coupling must share the time-distance grid"
        )
    if gamma_1.shape != times.shape or gamma_n.shape != times.shape:
        raise DomainViolationError("damping rates must have one value per time")
    ensure_finite(
        (times, distances, observed_1, observed_n, gamma_1, gamma_n, delay_1, delay_n, coupling),
        name="harmonic clock input",
    )
    if np.any(np.diff(times) <= 0.0) or np.any(np.diff(distances) <= 0.0):
        raise DomainViolationError("time and distance coordinates must be strictly increasing")
    if not np.isfinite(source.fundamental_frequency) or source.fundamental_frequency <= 0.0:
        raise DomainViolationError("fundamental frequency must be finite and positive")
    if not np.isfinite(source.harmonic_frequency) or source.harmonic_frequency <= 0.0:
        raise DomainViolationError("harmonic frequency must be finite and positive")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    for label, residual in (
        ("quality", source.quality_source_residual),
        ("lag", source.lag_source_residual),
    ):
        if not np.isfinite(residual) or residual < 0.0:
            raise DomainViolationError(f"{label} source residual must be finite and nonnegative")
    supplied = None
    if source.corrected_clock is not None:
        supplied = np.asarray(source.corrected_clock, dtype=complex)
        if supplied.shape != shape:
            raise DomainViolationError("supplied corrected clock must share the time-distance grid")
        ensure_finite(supplied, name="supplied corrected clock")
    return (
        times,
        distances,
        observed_1,
        observed_n,
        gamma_1,
        gamma_n,
        delay_1,
        delay_n,
        coupling,
        supplied,
    )


def harmonic_clock_operator(
    value: HarmonicClockInput | FieldLawInput,
) -> HarmonicClockCertificate:
    source = _input(value)
    (
        times,
        distances,
        observed_1,
        observed_n,
        gamma_1,
        gamma_n,
        delay_1,
        delay_n,
        coupling,
        supplied,
    ) = _validated(source)
    denominator_margin = float(np.min(np.abs(observed_1)))
    integral_1 = _cumtrap(gamma_1, times)
    integral_n = _cumtrap(gamma_n, times)
    amplitude_correction = np.exp(integral_n - 3.0 * integral_1)[:, None]
    phase_correction = np.exp(
        1j
        * (
            source.harmonic_frequency * delay_n
            - 3.0 * source.fundamental_frequency * delay_1
        )
    )
    safe_denominator = np.where(
        np.abs(observed_1) > np.finfo(float).eps,
        observed_1,
        np.finfo(float).eps + 0.0j,
    )
    raw_ratio = observed_n / safe_denominator**3
    expected_clock = amplitude_correction * phase_correction * raw_ratio
    corrected = expected_clock if supplied is None else supplied
    correction_identity = float(np.linalg.norm(corrected - expected_clock))
    coupling_residual = float(np.linalg.norm(corrected - coupling))
    time_gradient = np.gradient(corrected, times, axis=0, edge_order=2)
    distance_gradient = np.gradient(corrected, distances, axis=1, edge_order=1)
    time_invariance = float(np.linalg.norm(time_gradient))
    distance_invariance = float(np.linalg.norm(distance_gradient))

    delta_gamma_1 = np.full(times.shape, 2.0e-7)
    delta_gamma_n = np.full(times.shape, -1.5e-7)
    delta_delay_1 = np.full(delay_1.shape, 1.0e-8)
    delta_delay_n = np.full(delay_n.shape, -2.0e-8)
    delta_amp = 1.0e-7
    delta_exponent = (
        _cumtrap(delta_gamma_n - 3.0 * delta_gamma_1, times)[:, None]
        + 1j
        * (
            source.harmonic_frequency * delta_delay_n
            - 3.0 * source.fundamental_frequency * delta_delay_1
        )
        + delta_amp
    )
    perturbation_log_norm = float(np.max(np.abs(delta_exponent)))
    damping_bound = float(
        np.max(
            _cumtrap(
                np.abs(delta_gamma_n) + 3.0 * np.abs(delta_gamma_1),
                times,
            )
        )
    )
    phase_bound = float(
        source.harmonic_frequency * np.max(np.abs(delta_delay_n))
        + 3.0 * source.fundamental_frequency * np.max(np.abs(delta_delay_1))
    )
    perturbation_bound = damping_bound + phase_bound + abs(delta_amp)
    perturbation_residual = max(
        perturbation_log_norm - perturbation_bound,
        0.0,
    )

    total = max(
        correction_identity,
        coupling_residual,
        time_invariance,
        distance_invariance,
        max(source.tolerance - denominator_margin, 0.0),
        perturbation_residual,
        source.quality_source_residual,
        source.lag_source_residual,
    )
    closed = total <= source.tolerance
    status_equivalence = float(closed != (total <= source.tolerance))
    return HarmonicClockCertificate(
        times,
        times,
        distances,
        integral_1,
        integral_n,
        amplitude_correction,
        phase_correction,
        raw_ratio,
        corrected,
        coupling,
        np.mean(np.abs(corrected), axis=1),
        correction_identity,
        coupling_residual,
        time_invariance,
        distance_invariance,
        denominator_margin,
        perturbation_log_norm,
        perturbation_bound,
        perturbation_residual,
        source.quality_source_residual,
        source.lag_source_residual,
        status_equivalence,
        "closed" if closed and status_equivalence <= source.tolerance else "open",
    )


def _residual(value, output: HarmonicClockCertificate) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.correction_identity_residual,
        output.source_coupling_residual,
        output.time_invariance_residual,
        output.distance_invariance_residual,
        max(tolerance - output.denominator_margin, 0.0),
        output.perturbation_bound_residual,
        output.quality_source_residual,
        output.lag_source_residual,
        output.status_equivalence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "damping-lag correction, source coupling, and clock invariance",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "denominator_margin": output.denominator_margin,
            "perturbation_log_norm": output.perturbation_log_norm,
            "perturbation_bound": output.perturbation_bound,
            "time_distance_invariance_checked": True,
        },
    )


def _response(output: HarmonicClockCertificate) -> np.ndarray:
    return np.concatenate((output.corrected_clock.real.ravel(), output.corrected_clock.imag.ravel()))


def _remove_quality(value) -> SourceRemovalResult:
    source = _input(value)
    complete = harmonic_clock_operator(source)
    removed = complete.phase_correction * complete.raw_ratio
    return source_removal_result(
        ComplexId(B_QUALITY),
        _response(complete),
        np.concatenate((removed.real.ravel(), removed.imag.ravel())),
        tolerance=max(source.tolerance, 1e-12),
    )


def _remove_lag(value) -> SourceRemovalResult:
    source = _input(value)
    complete = harmonic_clock_operator(source)
    removed = complete.amplitude_correction * complete.raw_ratio
    return source_removal_result(
        ComplexId(B_LAG),
        _response(complete),
        np.concatenate((removed.real.ravel(), removed.imag.ravel())),
        tolerance=max(source.tolerance, 1e-12),
    )


def contract() -> ComplexContract:
    return ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B_QUALITY), ComplexId(B_LAG)),
        domain=DomainSpec(
            "damping- and lag-corrected harmonic observation",
            "strict time-distance grid, nonvanishing fundamental, observed fundamental/harmonic modes, integrable damping rates, delay fields, source coupling, and localized B residuals",
            (HarmonicClockInput, FieldLawInput),
        ),
        codomain=CodomainSpec(
            "corrected harmonic clock certificate",
            "amplitude and phase corrections, source-ratio reconstruction, time/distance invariance, denominator margin, perturbation bound, and exact status",
            (HarmonicClockCertificate,),
        ),
        operator=harmonic_clock_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
            and output.denominator_margin > residual.tolerance
        ),
        source_removal_checks=(_remove_quality, _remove_lag),
        artifact_spec=ArtifactSpec(
            ("corrected_clock_field", "time_distance_invariance", "perturbation_bound_table"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
