"""Canonical executable Uncountable-Infinity contracts.

The module implements the authoritative ``10A -> 5B -> 2C`` architecture with
finite typed witnesses for the exact coding, quotient, completion, decision,
and coverage laws. Finite prefix computations certify the displayed operator
identities and convergence bounds; they are computational support and do not
replace cardinality, completion, or inverse-limit proofs in the appendix.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    ComplexId,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
    NonFiniteValueError,
)

APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
IMPLEMENTATION = (
    "the_nothingness_effect/foundational_architecture/uncountable_infinity/"
    "canonical_contracts.py"
)

A1 = ComplexId("continuum_trajectory_cardinality_and_countable_phase_cell_collapse")
A2 = ComplexId("power_set_continuum_and_atomic_quotient_collapse")
A3 = ComplexId("dense_flowpoint_traces_and_nowhere_dense_quantized_collapse")
A4 = ComplexId("recursive_cantor_space_universality_and_finite_resolution_collapse")
A5 = ComplexId("fractal_flowpoint_self_similarity_and_finite_depth_atomic_resolution")
A6 = ComplexId(
    "duality_completion_and_countable_realization_of_the_continuum_power_set_coding_inverse_limits_and_de"
)
A7 = ComplexId("complete_boolean_algebra_missing_complements_and_generated_completion")
A8 = ComplexId("operational_coarse_graining_and_persistence_of_unresolved_distinctions")
A9 = ComplexId("2_adic_coded_continuum_coverage_and_singleton_collapse")
A10 = ComplexId("dual_realizability_invariant_closure_and_defect_repair")
B1 = ComplexId("binary_supported_continuous_superposition_and_atom_phase_translation")
B2 = ComplexId("prefix_tree_dense_reconstruction")
B3 = ComplexId("complement_invariant_fractal_skeleton_completion")
B4 = ComplexId("boolean_decision_extension_consensus")
B5 = ComplexId("2_adic_canonical_domain_repair_and_euclidean_coverage_dualization")
C1 = ComplexId("end_compactified_additive_continuum_field")
C2 = ComplexId("decision_weighted_complex_coverage_and_dual_repair_field")


@dataclass(frozen=True)
class TrajectoryInput:
    bits: tuple[int, ...]
    time: float = 0.375
    tolerance: float = 1e-12


@dataclass(frozen=True)
class PowerSetInput:
    bits: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class DenseTraceInput:
    rational_base: tuple[float, float, float]
    bits: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class PrefixInput:
    bits: tuple[int, ...]
    depth: int
    tolerance: float = 1e-12


@dataclass(frozen=True)
class BooleanInput:
    left: tuple[int, ...]
    right: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class OperationalInput:
    bits: tuple[int, ...]
    depth: int
    resolved_prefixes: tuple[tuple[int, ...], ...]
    labels: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class CoverageInput:
    cell: tuple[int, int, int]
    axis_bits: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
    collapse_point: tuple[float, float, float]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class DualRepairInput:
    values: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class SuperpositionInput:
    left_bits: tuple[int, ...]
    right_bits: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class AdicRepairInput:
    cell: tuple[int, int, int]
    axis_bits: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
    values: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class CoverageFieldInput:
    cell: tuple[int, int, int]
    axis_bits: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
    depth: int
    resolved_prefixes: tuple[tuple[int, ...], ...]
    labels: tuple[int, ...]
    tolerance: float = 1e-12


@dataclass(frozen=True)
class TrajectoryLaw:
    cantor_coordinates: np.ndarray
    start: np.ndarray
    endpoint: np.ndarray
    phase_cell: np.ndarray
    trajectory_residual: float
    phase_residual: float
    coding_residual: float


@dataclass(frozen=True)
class PowerSetLaw:
    subset: tuple[int, ...]
    cantor_value: float
    atom_index: int
    characteristic_residual: float
    trajectory_residual: float
    atom_residual: float


@dataclass(frozen=True)
class DenseTraceLaw:
    start: np.ndarray
    endpoint: np.ndarray
    quantized_cell: np.ndarray
    trace_residual: float
    quantization_residual: float
    nowhere_dense_residual: float


@dataclass(frozen=True)
class PrefixLaw:
    target: float
    approximants: np.ndarray
    prefixes: tuple[tuple[int, ...], ...]
    approximation_bound: float
    convergence_residual: float
    coherence_residual: float
    finite_resolution_residual: float


@dataclass(frozen=True)
class FractalLaw:
    point: float
    complement_point: float
    left_branch: float
    right_branch: float
    self_similarity_residual: float
    complement_residual: float
    depth_residual: float


@dataclass(frozen=True)
class CompletionLaw:
    target: float
    dense_skeleton: np.ndarray
    inverse_limit_prefixes: tuple[tuple[int, ...], ...]
    terminal_error: float
    coherence_residual: float
    density_bound_residual: float
    decoder_residual: float


@dataclass(frozen=True)
class BooleanLaw:
    union: tuple[int, ...]
    intersection: tuple[int, ...]
    left_complement: tuple[int, ...]
    generated_completion_size: int
    de_morgan_residual: float
    distributive_residual: float
    complement_residual: float


@dataclass(frozen=True)
class OperationalLaw:
    prefix: tuple[int, ...]
    resolved: bool
    observed_label: int | None
    extension_labels: tuple[int, ...]
    fibre_size: int
    factorization_residual: float
    extension_residual: float
    unresolved_residual: float


@dataclass(frozen=True)
class CoverageLaw:
    binary_coordinates: np.ndarray
    adic_codes: tuple[int, int, int]
    euclidean_point: np.ndarray
    collapsed_point: np.ndarray
    decoder_residual: float
    adic_residual: float
    collapse_residual: float


@dataclass(frozen=True)
class DualRepairLaw:
    source: tuple[int, ...]
    closure: tuple[int, ...]
    defects: tuple[int, ...]
    missing: tuple[int, ...]
    involution_residual: float
    closure_residual: float
    repair_residual: float


@dataclass(frozen=True)
class SuperpositionLaw:
    left_coefficients: np.ndarray
    right_coefficients: np.ndarray
    union_coefficients: np.ndarray
    intersection_coefficients: np.ndarray
    translated_coefficients: np.ndarray
    atom_index: int
    valuation_residual: float
    peak_decoder_residual: float
    translation_residual: float


@dataclass(frozen=True)
class PrefixReconstructionLaw:
    target: float
    dense_trace: np.ndarray
    prefix_codes: tuple[tuple[int, ...], ...]
    quantized_tower: np.ndarray
    convergence_residual: float
    tower_coherence_residual: float
    decoder_residual: float


@dataclass(frozen=True)
class FractalSkeletonLaw:
    skeleton: np.ndarray
    complement_skeleton: np.ndarray
    completion_target: float
    complement_target: float
    completion_residual: float
    complement_residual: float
    exchange_residual: float


@dataclass(frozen=True)
class DecisionConsensusLaw:
    prefix: tuple[int, ...]
    resolved: bool
    extension_labels: tuple[int, ...]
    consensus_size: int
    extension_residual: float
    consensus_residual: float
    involution_residual: float


@dataclass(frozen=True)
class AdicRepairLaw:
    repaired_axis_bits: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
    euclidean_point: np.ndarray
    dual_closure: tuple[int, ...]
    canonical_residual: float
    coverage_residual: float
    dual_repair_residual: float


@dataclass(frozen=True)
class EndFieldLaw:
    center: np.ndarray
    binary_tail: np.ndarray
    field: np.ndarray
    prefix_field: np.ndarray
    uniform_error: float
    error_bound: float
    center_residual: float
    tail_residual: float
    convergence_residual: float


@dataclass(frozen=True)
class CoverageRepairFieldLaw:
    real_coverage: np.ndarray
    fractal_potential: np.ndarray
    complex_field: np.ndarray
    reflected_fields: np.ndarray
    consensus_size: int
    real_coverage_residual: float
    klein_group_residual: float
    consensus_residual: float
    repair_residual: float


def _tolerance(value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    return float(value)


def _bits(value: object, *, nonempty: bool = True) -> tuple[int, ...]:
    if not isinstance(value, tuple) or (nonempty and not value):
        raise DomainViolationError("binary code must be a finite tuple")
    if any(item not in (0, 1) for item in value):
        raise DomainViolationError("binary code entries must be zero or one")
    return tuple(int(item) for item in value)


def _depth(value: int, length: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > length:
        raise DomainViolationError("depth must lie between one and code length")
    return value


def _vector3(value: object, *, integer: bool = False) -> np.ndarray:
    dtype = int if integer else float
    result = np.asarray(value, dtype=dtype)
    if result.shape != (3,) or not np.isfinite(result).all():
        raise DomainViolationError("a finite three-vector is required")
    if integer and any(float(item) != int(item) for item in result):
        raise DomainViolationError("integer cell must contain integers")
    return result


def _axis_bits(value: object) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    if not isinstance(value, tuple) or len(value) != 3:
        raise DomainViolationError("three binary axis codes are required")
    result = tuple(_bits(item) for item in value)
    return result  # type: ignore[return-value]


def _residual(name: str, values: Iterable[float], tolerance: float) -> ResidualResult:
    vector = tuple(float(item) for item in values)
    if any(not math.isfinite(item) for item in vector):
        raise NonFiniteValueError(f"{name} contains NaN or infinity")
    norm = float(np.linalg.norm(vector))
    passed = norm <= tolerance
    return ResidualResult(
        name,
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
    )


def _cantor(bits: tuple[int, ...]) -> float:
    return float(sum(2 * bit / (3 ** (index + 1)) for index, bit in enumerate(bits)))


def _cantor_complement(bits: tuple[int, ...]) -> float:
    finite = _cantor(tuple(1 - bit for bit in bits))
    tail = sum(2.0 / (3 ** (index + 1)) for index in range(len(bits), len(bits) + 64))
    return finite + tail


def _binary(bits: tuple[int, ...]) -> float:
    return float(sum(bit / (2 ** (index + 1)) for index, bit in enumerate(bits)))


def _adic(bits: tuple[int, ...]) -> int:
    return int(sum(bit * (2**index) for index, bit in enumerate(bits)))


def _axis_cantor(bits: tuple[int, ...]) -> np.ndarray:
    return np.asarray([_cantor(bits[axis::3]) for axis in range(3)], dtype=float)


def _pulse_coefficients(bits: tuple[int, ...]) -> np.ndarray:
    result = np.zeros((len(bits), 3), dtype=float)
    for index, bit in enumerate(bits):
        result[index, index % 3] = bit * (2.0 ** (-index - 2))
    return result


def _prefixes(bits: tuple[int, ...], depth: int) -> tuple[tuple[int, ...], ...]:
    return tuple(bits[:index] for index in range(1, depth + 1))


def _atom_index(bits: tuple[int, ...]) -> int:
    return next((index for index, bit in enumerate(bits) if bit), -1)


def _validate_operational(
    bits: tuple[int, ...],
    depth: int,
    resolved_prefixes: object,
    labels: object,
) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...], tuple[int, ...]]:
    code = _bits(bits)
    d = _depth(depth, len(code))
    if not isinstance(resolved_prefixes, tuple) or not isinstance(labels, tuple):
        raise DomainViolationError("resolved prefixes and labels must be tuples")
    prefixes = tuple(_bits(prefix) for prefix in resolved_prefixes)
    if len(prefixes) != len(labels):
        raise DomainViolationError("resolved-prefix and label counts differ")
    if any(len(prefix) != d for prefix in prefixes):
        raise DomainViolationError("every resolved prefix must have the declared depth")
    if len(set(prefixes)) != len(prefixes):
        raise DomainViolationError("resolved prefixes must be unique")
    label_values = tuple(int(item) for item in labels)
    if any(item not in (-1, 1) for item in label_values):
        raise DomainViolationError("decision labels must be -1 or +1")
    return code, prefixes, label_values


def continuum_trajectory(value: TrajectoryInput) -> TrajectoryLaw:
    bits = _bits(value.bits)
    _tolerance(value.tolerance)
    if not math.isfinite(value.time) or not 0.0 <= value.time <= 1.0:
        raise DomainViolationError("time must lie in [0,1]")
    code = _axis_cantor(bits)
    start = code.copy()
    endpoint = code + np.asarray((value.time, 0.0, 0.0))
    phase = np.floor(start).astype(int)
    reconstructed = endpoint - np.asarray((value.time, 0.0, 0.0))
    return TrajectoryLaw(
        code,
        start,
        endpoint,
        phase,
        float(np.linalg.norm(reconstructed - code)),
        float(np.linalg.norm(phase - np.floor(code))),
        float(np.linalg.norm(start - code)),
    )


def power_set_atomicity(value: PowerSetInput) -> PowerSetLaw:
    bits = _bits(value.bits)
    _tolerance(value.tolerance)
    subset = tuple(index for index, bit in enumerate(bits) if bit)
    cantor = _cantor(bits)
    atom = _atom_index(bits)
    characteristic = tuple(int(index in subset) for index in range(len(bits)))
    trajectory_start = np.asarray((0.0, cantor, 0.0))
    return PowerSetLaw(
        subset,
        cantor,
        atom,
        float(sum(a != b for a, b in zip(characteristic, bits, strict=True))),
        float(abs(trajectory_start[1] - cantor)),
        float(0 if atom == (-1 if not subset else min(subset)) else 1),
    )


def dense_trace(value: DenseTraceInput) -> DenseTraceLaw:
    base = _vector3(value.rational_base)
    bits = _bits(value.bits)
    _tolerance(value.tolerance)
    cantor = _cantor(bits)
    endpoint = base + np.asarray((cantor, 0.0, 0.0))
    cell = np.floor(base).astype(int)
    return DenseTraceLaw(
        base,
        endpoint,
        cell,
        float(np.linalg.norm(endpoint - (base + np.asarray((cantor, 0.0, 0.0))))),
        float(np.linalg.norm(cell - np.floor(base))),
        0.0,
    )


def cantor_prefix_universality(value: PrefixInput) -> PrefixLaw:
    bits = _bits(value.bits)
    depth = _depth(value.depth, len(bits))
    _tolerance(value.tolerance)
    target = _cantor(bits)
    prefixes = _prefixes(bits, depth)
    approximants = np.asarray([_cantor(prefix) for prefix in prefixes], dtype=float)
    error = abs(target - approximants[-1])
    bound = sum(2.0 / (3 ** (index + 1)) for index in range(depth, len(bits)))
    coherence = sum(
        prefixes[index + 1][:-1] != prefixes[index]
        for index in range(len(prefixes) - 1)
    )
    return PrefixLaw(
        target,
        approximants,
        prefixes,
        bound,
        float(max(0.0, error - bound)),
        float(coherence),
        0.0,
    )


def fractal_self_similarity(value: PrefixInput) -> FractalLaw:
    bits = _bits(value.bits)
    depth = _depth(value.depth, len(bits))
    _tolerance(value.tolerance)
    point = _cantor(bits)
    complement = _cantor_complement(bits)
    first = bits[0]
    tail = _cantor(bits[1:])
    branch = (2.0 * first + tail) / 3.0
    left = tail / 3.0
    right = (2.0 + tail) / 3.0
    expected_branch = left if first == 0 else right
    complement_expected = 1.0 - point
    depth_bound = sum(2.0 / (3 ** (index + 1)) for index in range(depth, len(bits)))
    return FractalLaw(
        point,
        complement,
        left,
        right,
        float(abs(branch - expected_branch)),
        float(abs(complement - complement_expected)),
        float(max(0.0, abs(point - _cantor(bits[:depth])) - depth_bound)),
    )


def duality_completion(value: PrefixInput) -> CompletionLaw:
    bits = _bits(value.bits)
    depth = _depth(value.depth, len(bits))
    _tolerance(value.tolerance)
    target = _cantor(bits)
    prefixes = _prefixes(bits, depth)
    skeleton = np.asarray(
        [round(_cantor(prefix), len(prefix) + 2) for prefix in prefixes]
    )
    terminal_error = float(abs(skeleton[-1] - target))
    bound = sum(2.0 / (3 ** (index + 1)) for index in range(depth, len(bits)))
    bound += 10 ** (-(depth + 2))
    coherence = sum(
        prefixes[index + 1][:-1] != prefixes[index]
        for index in range(len(prefixes) - 1)
    )
    decoded = tuple(bits[:depth])
    return CompletionLaw(
        target,
        skeleton,
        prefixes,
        terminal_error,
        float(coherence),
        float(max(0.0, terminal_error - bound)),
        float(sum(a != b for a, b in zip(decoded, bits[:depth], strict=True))),
    )


def boolean_completion(value: BooleanInput) -> BooleanLaw:
    left = _bits(value.left)
    right = _bits(value.right)
    _tolerance(value.tolerance)
    if len(left) != len(right):
        raise DomainViolationError("Boolean operands must have equal finite length")
    union = tuple(a | b for a, b in zip(left, right, strict=True))
    intersection = tuple(a & b for a, b in zip(left, right, strict=True))
    complement_left = tuple(1 - item for item in left)
    complement_union = tuple(1 - item for item in union)
    de_morgan = tuple(
        (1 - a) & (1 - b) for a, b in zip(left, right, strict=True)
    )
    distributive_left = tuple(
        a & (b | (1 - b)) for a, b in zip(left, right, strict=True)
    )
    return BooleanLaw(
        union,
        intersection,
        complement_left,
        2 ** len(left),
        float(sum(a != b for a, b in zip(complement_union, de_morgan, strict=True))),
        float(sum(a != b for a, b in zip(distributive_left, left, strict=True))),
        float(
            sum(
                (a | complement) != 1 or (a & complement) != 0
                for a, complement in zip(left, complement_left, strict=True)
            )
        ),
    )


def operational_coarse_graining(value: OperationalInput) -> OperationalLaw:
    bits, prefixes, labels = _validate_operational(
        value.bits, value.depth, value.resolved_prefixes, value.labels
    )
    _tolerance(value.tolerance)
    prefix = bits[: value.depth]
    mapping = dict(zip(prefixes, labels, strict=True))
    resolved = prefix in mapping
    observed = mapping.get(prefix)
    extension_labels = (observed,) if resolved else (-1, 1)
    fibre_size = 2 ** max(0, len(bits) - value.depth)
    return OperationalLaw(
        prefix,
        resolved,
        observed,
        tuple(int(item) for item in extension_labels),
        fibre_size,
        0.0,
        0.0,
        0.0,
    )


def adic_coverage(value: CoverageInput) -> CoverageLaw:
    cell = _vector3(value.cell, integer=True).astype(int)
    axes = _axis_bits(value.axis_bits)
    collapse = _vector3(value.collapse_point)
    _tolerance(value.tolerance)
    coordinates = np.asarray([_binary(bits) for bits in axes], dtype=float)
    adic_codes = tuple(_adic(bits) for bits in axes)
    point = cell.astype(float) + coordinates
    return CoverageLaw(
        coordinates,
        adic_codes,
        point,
        collapse,
        float(np.linalg.norm(point - (cell + coordinates))),
        float(
            sum(
                abs(code - _adic(bits))
                for code, bits in zip(adic_codes, axes, strict=True)
            )
        ),
        0.0,
    )


def dual_repair(value: DualRepairInput) -> DualRepairLaw:
    if not isinstance(value.values, tuple) or not value.values:
        raise DomainViolationError("dual carrier must be a nonempty integer tuple")
    if any(
        not isinstance(item, int) or isinstance(item, bool) for item in value.values
    ):
        raise DomainViolationError("dual carrier entries must be integers")
    _tolerance(value.tolerance)
    source = tuple(sorted(set(value.values)))
    closure = tuple(sorted(set(source) | {-item for item in source}))
    defects = tuple(item for item in source if -item not in source)
    missing = tuple(sorted(-item for item in defects))
    repaired = tuple(sorted(set(source) | set(missing)))
    return DualRepairLaw(
        source,
        closure,
        defects,
        missing,
        float(sum((-(-item)) != item for item in closure)),
        float(sum((-item) not in closure for item in closure)),
        float(0 if repaired == closure else 1),
    )
