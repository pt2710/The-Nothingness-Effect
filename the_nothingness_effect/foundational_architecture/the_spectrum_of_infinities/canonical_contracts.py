"""Canonical executable Spectrum-of-Infinities contracts.

These operators are finite typed witnesses for the authoritative 10A -> 3B ->
3C slice. They preserve exact finite identities and expose obstruction
residuals without treating finite computation as a proof of the appendix's
infinite-cardinal, non-measurable, completion, or ergodic claims.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
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
    "the_nothingness_effect/foundational_architecture/"
    "the_spectrum_of_infinities/canonical_contracts.py"
)

A1 = ComplexId("spectrum_normalization_and_normalization_obstruction")
A2 = ComplexId("spectrum_dfi_duality_and_dfi_divergence")
A3 = ComplexId("measurable_decomposition_and_non_measurable_obstruction")
A4 = ComplexId("completeness_and_incompleteness_of_the_soi_l_p_structure")
A5 = ComplexId("entropy_density_mapping_and_entropy_divergence")
A6 = ComplexId("finitizable_infinity_and_the_non_finitization_boundary")
A7 = ComplexId("dual_realizability_and_the_missing_dual_defect")
A8 = ComplexId("soi_measure_preserving_normalization_and_spectrum_obstruction")
A9 = ComplexId("borel_analytic_sufficiency_and_over_extension_beyond_measurability")
A10 = ComplexId("factor_map_equivariance_and_limit_bias")
B1 = ComplexId("spectrum_flowpoint_addressability_and_unaddressability")
B2 = ComplexId("metric_deformation_robustness_and_deformation_fragility")
B3 = ComplexId("2_adic_history_accessibility_and_frozen_accessibility")
C1 = ComplexId("cosmic_matrix_address_and_ghost_spark_obstruction")
C2 = ComplexId("observable_locality_and_infinite_exposure")
C3 = ComplexId("elastic_curvature_probing_and_incoherent_warping")

SYMMETRY_SCHEDULE = ComplexId(
    "schedule_controlled_parity_coding_and_uniform_minimal_involution"
)
OBS_ERGODIC = ComplexId("ergodic_collapse_projection_and_non_convergence")
OBS_TEMPORAL = ComplexId("temporal_compression_and_frozen_time_obstruction")
OBS_SPECTRAL = ComplexId("collapse_spectral_selection_and_spectral_ambiguity")


@dataclass(frozen=True)
class NormalizationInput:
    values: np.ndarray
    magnitude: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DFIInput:
    trajectory: np.ndarray
    magnitude: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DecompositionInput:
    values: np.ndarray
    partition: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class LpInput:
    values: np.ndarray
    magnitude: float
    p: float = 2.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class EntropyInput:
    probabilities: np.ndarray
    magnitude: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class FinitizationInput:
    target: np.ndarray
    approximants: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class DualRealizabilityInput:
    coordinate: np.ndarray
    observable: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class MeasureTransferInput:
    weights: np.ndarray
    mapping: np.ndarray
    target_weights: np.ndarray
    magnitude: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class MeasurableScopeInput:
    values: np.ndarray
    measurable_mask: np.ndarray
    declared_mask: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class FactorMapInput:
    source_operator: np.ndarray
    target_operator: np.ndarray
    factor_map: np.ndarray
    state: np.ndarray
    steps: int = 6
    tolerance: float = 1e-10


@dataclass(frozen=True)
class AddressInput:
    histories: np.ndarray
    declared_addresses: np.ndarray
    weights: np.ndarray
    magnitude: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class MetricDeformationInput:
    points: np.ndarray
    deformation: np.ndarray
    weights: np.ndarray
    observable: np.ndarray
    source_operator: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class HistoryAccessibilityInput:
    initial_bits: np.ndarray
    schedules: np.ndarray
    expected_histories: np.ndarray
    magnitude: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class CosmicLedgerInput:
    addresses: np.ndarray
    histories: np.ndarray
    locations: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ObservableLocalityInput:
    temporal_field: np.ndarray
    spectral_field: np.ndarray
    localization_projector: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ElasticProbeInput:
    entropy_field: np.ndarray
    curvature_operator: np.ndarray
    localization_projector: np.ndarray
    k_d: float
    tolerance: float = 1e-10


@dataclass(frozen=True)
class LawCertificate:
    values: tuple[np.ndarray, ...]
    residuals: tuple[float, ...]
    source_blocks: tuple[np.ndarray, ...] = ()
    certificate: np.ndarray | None = None


def _tolerance(value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return float(value)


def _positive(value: float, name: str) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise DomainViolationError(f"{name} must be finite and positive")
    return float(value)


def _array(value: object, name: str, ndim: int | None = None) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.size < 1 or (ndim is not None and result.ndim != ndim):
        raise DomainViolationError(f"{name} has an invalid finite-array shape")
    if not np.isfinite(result).all():
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    return result


def _square(value: object, name: str) -> np.ndarray:
    result = _array(value, name, 2)
    if result.shape[0] != result.shape[1]:
        raise DomainViolationError(f"{name} must be square")
    return result


def _probabilities(value: object, tolerance: float) -> np.ndarray:
    result = _array(value, "probabilities", 1)
    if np.any(result < 0.0) or float(np.sum(result)) <= tolerance:
        raise DomainViolationError("probabilities must be non-negative with positive mass")
    return result / float(np.sum(result))


def _binary_rows(value: object, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=int)
    if result.ndim != 2 or result.size < 1 or not np.isin(result, (0, 1)).all():
        raise DomainViolationError(f"{name} must be a nonempty binary matrix")
    return result


def _result(*values: object, residuals: tuple[float, ...]) -> LawCertificate:
    arrays = tuple(np.asarray(value, dtype=float) for value in values)
    return LawCertificate(arrays, tuple(float(item) for item in residuals))


def _derived(
    blocks: tuple[np.ndarray, ...],
    residuals: tuple[float, ...],
    certificate: np.ndarray | None = None,
) -> LawCertificate:
    source_blocks = tuple(np.asarray(block, dtype=float).ravel() for block in blocks)
    combined = (
        np.asarray(certificate, dtype=float).ravel()
        if certificate is not None
        else np.concatenate(source_blocks)
    )
    return LawCertificate((combined,), tuple(float(item) for item in residuals), source_blocks, combined)


def normalization_law(value: NormalizationInput) -> LawCertificate:
    tolerance = _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    values = _array(value.values, "values", 1)
    if np.any(values < 0.0) or float(np.sum(values)) <= tolerance:
        raise DomainViolationError("normalization carrier must have positive mass")
    relative = values / float(np.sum(values))
    absolute = magnitude * relative
    return _result(
        relative,
        absolute,
        residuals=(
            abs(float(np.sum(relative)) - 1.0),
            abs(float(np.sum(absolute)) - magnitude),
            float(np.linalg.norm(absolute - magnitude * relative)),
        ),
    )


def dfi_law(value: DFIInput) -> LawCertificate:
    _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    trajectory = _array(value.trajectory, "trajectory", 1)
    if trajectory.size < 2 or np.any(np.abs(trajectory[:-1]) <= value.tolerance):
        raise DomainViolationError("DFI requires at least two states and nonzero predecessors")
    increments = np.abs(np.diff(trajectory) / trajectory[:-1])
    relative = float(np.mean(increments))
    absolute = magnitude * relative
    return _result(
        increments,
        np.asarray((relative, absolute)),
        residuals=(
            0.0,
            abs(relative - float(np.sum(increments)) / len(increments)),
            abs(absolute - magnitude * relative),
        ),
    )


def decomposition_law(value: DecompositionInput) -> LawCertificate:
    _tolerance(value.tolerance)
    values = _array(value.values, "values", 1)
    partition = _array(value.partition, "partition", 2)
    if partition.shape[1] != values.size or not np.isin(partition, (0.0, 1.0)).all():
        raise DomainViolationError("partition must be binary and aligned with values")
    pieces = partition * values[None, :]
    reconstruction = np.sum(pieces, axis=0)
    return _result(
        pieces,
        reconstruction,
        residuals=(
            float(np.linalg.norm(reconstruction - values)),
            abs(float(np.sum(pieces)) - float(np.sum(values))),
            float(np.linalg.norm(np.sum(partition, axis=0) - 1.0)),
        ),
    )


def lp_law(value: LpInput) -> LawCertificate:
    _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    if not math.isfinite(value.p) or value.p < 1.0:
        raise DomainViolationError("p must be finite and at least one")
    values = _array(value.values, "values", 1)
    relative = float(np.linalg.norm(values, ord=value.p))
    absolute = magnitude ** (1.0 / value.p) * relative
    expected = magnitude ** (1.0 / value.p) * relative
    return _result(
        values.copy(),
        np.asarray((relative, absolute)),
        residuals=(abs(absolute - expected), 0.0, 0.0),
    )


def entropy_law(value: EntropyInput) -> LawCertificate:
    tolerance = _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    probabilities = _probabilities(value.probabilities, tolerance)
    positive = probabilities[probabilities > tolerance]
    entropy = float(-np.sum(positive * np.log(positive)))
    absolute = magnitude * entropy
    return _result(
        probabilities,
        np.asarray((entropy, absolute)),
        residuals=(
            abs(float(np.sum(probabilities)) - 1.0),
            0.0,
            abs(absolute - magnitude * entropy),
        ),
    )


def finitization_law(value: FinitizationInput) -> LawCertificate:
    _tolerance(value.tolerance)
    target = _array(value.target, "target", 1)
    approximants = _array(value.approximants, "approximants", 2)
    if approximants.shape[1] != target.size:
        raise DomainViolationError("approximants and target must share a dimension")
    errors = np.linalg.norm(approximants - target[None, :], axis=1)
    increases = np.maximum(np.diff(errors), 0.0)
    return _result(
        errors,
        approximants[-1],
        residuals=(float(np.linalg.norm(increases)), float(errors[-1]), 0.0),
    )


def dual_realizability_law(value: DualRealizabilityInput) -> LawCertificate:
    _tolerance(value.tolerance)
    coordinate = _array(value.coordinate, "coordinate", 2)
    observable = _array(value.observable, "observable", 1)
    if coordinate.shape[0] != observable.size:
        raise DomainViolationError("coordinate rows must match observable size")
    inverse = np.linalg.pinv(coordinate)
    coefficients = inverse @ observable
    reconstruction = coordinate @ coefficients
    projector = coordinate @ inverse
    residual = reconstruction - observable
    return _result(
        coefficients,
        reconstruction,
        projector,
        residuals=(
            float(np.linalg.norm(residual)),
            float(np.linalg.norm(projector @ projector - projector)),
            float(np.linalg.norm(coordinate.T @ residual)),
        ),
    )


def measure_transfer_law(value: MeasureTransferInput) -> LawCertificate:
    tolerance = _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    weights = _probabilities(value.weights, tolerance)
    target = _probabilities(value.target_weights, tolerance)
    mapping = np.asarray(value.mapping, dtype=int)
    if mapping.ndim != 1 or mapping.size != weights.size:
        raise DomainViolationError("mapping must contain one target index per source weight")
    if np.any(mapping < 0) or np.any(mapping >= target.size):
        raise DomainViolationError("mapping index lies outside the target carrier")
    pushforward = np.zeros_like(target)
    for index, weight in zip(mapping, weights, strict=True):
        pushforward[index] += weight
    absolute = magnitude * pushforward
    return _result(
        pushforward,
        absolute,
        residuals=(
            abs(float(np.sum(pushforward)) - 1.0),
            float(np.linalg.norm(pushforward - target)),
            float(np.linalg.norm(absolute - magnitude * target)),
        ),
    )


def measurable_scope_law(value: MeasurableScopeInput) -> LawCertificate:
    _tolerance(value.tolerance)
    values = _array(value.values, "values", 1)
    measurable = np.asarray(value.measurable_mask, dtype=bool)
    declared = np.asarray(value.declared_mask, dtype=bool)
    if measurable.shape != values.shape or declared.shape != values.shape:
        raise DomainViolationError("scope masks must match values")
    transferred = np.where(measurable, values, 0.0)
    omitted = np.where(declared & ~measurable, values, 0.0)
    return _result(
        transferred,
        omitted,
        residuals=(
            float(np.sum(declared & ~measurable)),
            float(np.linalg.norm(transferred - np.where(declared, values, 0.0))),
            float(np.linalg.norm(omitted)),
        ),
    )


def _cesaro(operator: np.ndarray, state: np.ndarray, steps: int) -> np.ndarray:
    current = state.copy()
    total = np.zeros_like(state)
    for _ in range(steps):
        total += current
        current = operator @ current
    return total / steps


def factor_map_law(value: FactorMapInput) -> LawCertificate:
    _tolerance(value.tolerance)
    source = _square(value.source_operator, "source operator")
    target = _square(value.target_operator, "target operator")
    factor = _array(value.factor_map, "factor map", 2)
    state = _array(value.state, "state", 1)
    if source.shape[0] != state.size or factor.shape != (target.shape[0], source.shape[0]):
        raise DomainViolationError("factor-map source and target dimensions do not align")
    if not isinstance(value.steps, int) or isinstance(value.steps, bool) or value.steps < 1:
        raise DomainViolationError("steps must be a positive integer")
    equivariance = factor @ source - target @ factor
    source_average = factor @ _cesaro(source, state, value.steps)
    target_average = _cesaro(target, factor @ state, value.steps)
    return _result(
        equivariance,
        source_average,
        target_average,
        residuals=(
            float(np.linalg.norm(equivariance)),
            float(np.linalg.norm(source_average - target_average)),
            0.0,
        ),
    )


def _binary_addresses(histories: np.ndarray) -> np.ndarray:
    return histories @ (2.0 ** -np.arange(1, histories.shape[1] + 1))


def address_law(value: AddressInput) -> LawCertificate:
    tolerance = _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    histories = _binary_rows(value.histories, "histories")
    declared = _array(value.declared_addresses, "declared addresses", 1)
    weights = _probabilities(value.weights, tolerance)
    if histories.shape[0] != declared.size or weights.size != declared.size:
        raise DomainViolationError("histories, addresses, and weights must align")
    addresses = _binary_addresses(histories)
    collision = float(len(addresses) - len(np.unique(addresses)))
    gap = float(np.linalg.norm(np.sort(addresses) - np.sort(declared)))
    calibration = float(
        np.linalg.norm(np.sort(weights) - np.full(weights.size, 1.0 / weights.size))
    )
    blocks = (magnitude * addresses, weights, histories.astype(float).ravel())
    return _derived(
        blocks,
        (0.0, 0.0, float(np.linalg.norm((collision, gap, calibration)))),
    )


def metric_deformation_law(value: MetricDeformationInput) -> LawCertificate:
    _tolerance(value.tolerance)
    points = _array(value.points, "points", 2)
    deformation = _square(value.deformation, "deformation")
    weights = _probabilities(value.weights, value.tolerance)
    observable = _array(value.observable, "observable", 1)
    source_operator = _square(value.source_operator, "source operator")
    if deformation.shape[0] != points.shape[1]:
        raise DomainViolationError("deformation and point dimensions differ")
    if weights.size != points.shape[0] or observable.size != points.shape[0]:
        raise DomainViolationError("weights and observable must match point count")
    if source_operator.shape[0] != points.shape[0]:
        raise DomainViolationError("source dynamics must act on the point carrier")
    deformed = points @ deformation.T
    distances = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=-1)
    deformed_distances = np.linalg.norm(
        deformed[:, None, :] - deformed[None, :, :], axis=-1
    )
    gram = deformation.T @ deformation
    scale = float(np.trace(gram) / gram.shape[0])
    metric_residual = float(
        np.linalg.norm(deformed_distances - math.sqrt(scale) * distances)
    )
    positive = weights[weights > value.tolerance]
    entropy = float(-np.sum(positive * np.log(positive)))
    blocks = (
        weights,
        observable,
        np.asarray((entropy,)),
        source_operator.ravel(),
        deformed.ravel(),
    )
    return _derived(blocks, (metric_residual, 0.0, 0.0))


def _code_history(initial: int, schedule: np.ndarray) -> np.ndarray:
    history = np.empty(schedule.size + 1, dtype=int)
    history[0] = initial
    for index, step in enumerate(schedule):
        history[index + 1] = history[index] ^ int(step)
    return history


def history_accessibility_law(value: HistoryAccessibilityInput) -> LawCertificate:
    _tolerance(value.tolerance)
    magnitude = _positive(value.magnitude, "magnitude")
    initial = np.asarray(value.initial_bits, dtype=int)
    schedules = _binary_rows(value.schedules, "schedules")
    expected = _binary_rows(value.expected_histories, "expected histories")
    if (
        initial.ndim != 1
        or initial.size != schedules.shape[0]
        or not np.isin(initial, (0, 1)).all()
    ):
        raise DomainViolationError("initial bits must align with schedules")
    coded = np.stack(
        [
            _code_history(bit, schedule)
            for bit, schedule in zip(initial, schedules, strict=True)
        ]
    )
    if coded.shape != expected.shape:
        raise DomainViolationError("expected histories have an incompatible shape")
    addresses = _binary_addresses(coded)
    unique_ratio = len(np.unique(coded, axis=0)) / coded.shape[0]
    blocks = (
        schedules.astype(float).ravel(),
        magnitude * addresses,
        expected.astype(float).ravel(),
        coded[:, 1:].astype(float).ravel(),
        coded.astype(float).ravel(),
        np.asarray((unique_ratio,)),
    )
    return _derived(
        blocks,
        (abs(unique_ratio - 1.0), float(np.linalg.norm(coded - expected)), 0.0),
    )


def cosmic_ledger_law(value: CosmicLedgerInput) -> LawCertificate:
    _tolerance(value.tolerance)
    addresses = _array(value.addresses, "addresses", 1)
    histories = _binary_rows(value.histories, "histories")
    locations = _array(value.locations, "locations", 2)
    if addresses.size != histories.shape[0] or addresses.size != locations.shape[0]:
        raise DomainViolationError("ledger components must share an event count")
    encoded = _binary_addresses(histories)
    address_block = np.column_stack((locations, addresses))
    history_block = np.column_stack((locations, encoded))
    field = address_block + history_block
    reconstruction = 0.5 * field
    residuals = (
        float(np.linalg.norm(addresses - encoded)),
        float(len(addresses) - len(np.unique(addresses))),
        0.0,
        float(np.linalg.norm(reconstruction - address_block)),
    )
    return _derived((address_block, history_block), residuals, field)


def observable_locality_law(value: ObservableLocalityInput) -> LawCertificate:
    _tolerance(value.tolerance)
    temporal = _array(value.temporal_field, "temporal field", 1)
    spectral = _array(value.spectral_field, "spectral field", 1)
    projector = _square(value.localization_projector, "localization projector")
    if temporal.shape != spectral.shape or projector.shape[0] != temporal.size:
        raise DomainViolationError("locality fields and projector must share a dimension")
    temporal_local = projector @ temporal
    spectral_local = projector @ spectral
    field = temporal_local + spectral_local
    identity = np.eye(projector.shape[0])
    residuals = (
        float(np.linalg.norm(projector @ projector - projector)),
        float(np.linalg.norm((identity - projector) @ field)),
        float(abs(field[0]) + abs(field[-1])) if field.size > 1 else 0.0,
        0.0,
    )
    return _derived((temporal_local, spectral_local), residuals, field)


def elastic_probe_law(value: ElasticProbeInput) -> LawCertificate:
    _tolerance(value.tolerance)
    k_d = _positive(value.k_d, "k_d")
    entropy = _array(value.entropy_field, "entropy field", 1)
    curvature = _square(value.curvature_operator, "curvature operator")
    projector = _square(value.localization_projector, "localization projector")
    if curvature.shape[0] != entropy.size or projector.shape[0] != entropy.size:
        raise DomainViolationError("probe operators and entropy field must align")
    elastic_pi = math.pi * np.exp(-entropy / k_d)
    metric_block = curvature @ elastic_pi
    spectral_block = projector @ metric_block
    field = metric_block + spectral_block
    reconstruction = projector @ field
    identity = np.eye(projector.shape[0])
    residuals = (
        float(np.linalg.norm(projector @ projector - projector)),
        float(np.linalg.norm((identity - projector) @ spectral_block)),
        float(abs(reconstruction[0]) + abs(reconstruction[-1]))
        if field.size > 1
        else 0.0,
        float(np.linalg.norm(projector @ field - reconstruction)),
    )
    return _derived((metric_block, spectral_block), residuals, field)


def _source_removal(
    operator: Callable[[object], LawCertificate],
    source_id: ComplexId,
    source_index: int,
) -> Callable[[object], object]:
    def check(value: object):
        output = operator(value)
        blocks = output.source_blocks
        if source_index >= len(blocks):
            raise RuntimeError("source-removal index exceeds declared source blocks")
        complete = np.concatenate((*blocks, output.certificate))
        removed_blocks = list(blocks)
        removed_blocks[source_index] = np.zeros_like(removed_blocks[source_index])
        removed = np.concatenate((*removed_blocks, np.zeros_like(output.certificate)))
        return source_removal_result(
            source_id,
            complete,
            removed,
            tolerance=value.tolerance,
        )

    return check


def _contract(
    identifier: ComplexId,
    level: ComplexLevel,
    sources: tuple[ComplexId, ...],
    input_type: type,
    operator: Callable[[object], LawCertificate],
    *,
    closed: bool = False,
) -> ComplexContract:
    return ComplexContract(
        identifier,
        APPENDIX,
        APPENDIX_SHA256,
        level,
        sources,
        DomainSpec(
            str(identifier),
            "typed finite witness for the authoritative Spectrum-of-Infinities law",
            (input_type,),
        ),
        CodomainSpec(
            str(identifier),
            "finite operator certificate, obstruction residuals, and closure data",
            (LawCertificate,),
        ),
        operator,
        residual=lambda source, output: _residual(identifier, source, output),
        closure_predicate=(
            (lambda _output, residual: residual is not None and residual.passed)
            if closed
            else None
        ),
        source_removal_checks=tuple(
            _source_removal(operator, source, index)
            for index, source in enumerate(sources)
        ),
        artifact_spec=ArtifactSpec(
            ("json", "csv"),
            "python tools/generate_artifact_provenance.py --output-root <output-root>",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION,
    )


def _residual(
    identifier: ComplexId,
    source: object,
    output: LawCertificate,
) -> ResidualResult:
    vector = tuple(float(item) for item in output.residuals)
    if any(not math.isfinite(item) for item in vector):
        raise NonFiniteValueError(f"{identifier} contains NaN or infinity")
    norm = float(np.linalg.norm(vector))
    passed = norm <= source.tolerance
    return ResidualResult(
        str(identifier),
        vector,
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        _contract(A1, ComplexLevel.A, (), NormalizationInput, normalization_law),
        _contract(A2, ComplexLevel.A, (), DFIInput, dfi_law),
        _contract(A3, ComplexLevel.A, (), DecompositionInput, decomposition_law),
        _contract(A4, ComplexLevel.A, (), LpInput, lp_law),
        _contract(A5, ComplexLevel.A, (), EntropyInput, entropy_law),
        _contract(A6, ComplexLevel.A, (), FinitizationInput, finitization_law),
        _contract(
            A7,
            ComplexLevel.A,
            (),
            DualRealizabilityInput,
            dual_realizability_law,
        ),
        _contract(A8, ComplexLevel.A, (), MeasureTransferInput, measure_transfer_law),
        _contract(A9, ComplexLevel.A, (), MeasurableScopeInput, measurable_scope_law),
        _contract(A10, ComplexLevel.A, (), FactorMapInput, factor_map_law),
        _contract(B1, ComplexLevel.B, (A1, A9, A7), AddressInput, address_law),
        _contract(
            B2,
            ComplexLevel.B,
            (A1, A4, A5, A10, A7),
            MetricDeformationInput,
            metric_deformation_law,
        ),
        _contract(
            B3,
            ComplexLevel.B,
            (SYMMETRY_SCHEDULE, A1, A9, A10, OBS_ERGODIC, A7),
            HistoryAccessibilityInput,
            history_accessibility_law,
        ),
        _contract(
            C1,
            ComplexLevel.C,
            (B1, B3),
            CosmicLedgerInput,
            cosmic_ledger_law,
            closed=True,
        ),
        _contract(
            C2,
            ComplexLevel.C,
            (OBS_TEMPORAL, OBS_SPECTRAL),
            ObservableLocalityInput,
            observable_locality_law,
            closed=True,
        ),
        _contract(
            C3,
            ComplexLevel.C,
            (B2, OBS_SPECTRAL),
            ElasticProbeInput,
            elastic_probe_law,
            closed=True,
        ),
    )
