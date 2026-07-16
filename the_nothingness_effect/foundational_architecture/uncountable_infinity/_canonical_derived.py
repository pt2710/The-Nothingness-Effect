"""Derived B/C operators for canonical Uncountable-Infinity contracts."""

from __future__ import annotations

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)

from ._canonical_core import (
    A1,
    A2,
    A3,
    A4,
    A5,
    A6,
    A7,
    A8,
    A9,
    A10,
    B1,
    B2,
    B3,
    B4,
    B5,
    AdicRepairInput,
    AdicRepairLaw,
    CoverageFieldInput,
    CoverageRepairFieldLaw,
    DecisionConsensusLaw,
    DualRepairInput,
    EndFieldLaw,
    FractalSkeletonLaw,
    OperationalInput,
    PrefixInput,
    PrefixReconstructionLaw,
    SuperpositionInput,
    SuperpositionLaw,
    _atom_index,
    _axis_bits,
    _axis_cantor,
    _binary,
    _bits,
    _cantor,
    _depth,
    _prefixes,
    _pulse_coefficients,
    _tolerance,
    _validate_operational,
    _vector3,
    dual_repair,
)


def binary_superposition(value: SuperpositionInput) -> SuperpositionLaw:
    left = _bits(value.left_bits)
    right = _bits(value.right_bits)
    _tolerance(value.tolerance)
    if len(left) != len(right):
        raise DomainViolationError("superposition codes must have equal length")
    left_coeff = _pulse_coefficients(left)
    right_coeff = _pulse_coefficients(right)
    union = tuple(a | b for a, b in zip(left, right, strict=True))
    intersection = tuple(a & b for a, b in zip(left, right, strict=True))
    union_coeff = _pulse_coefficients(union)
    intersection_coeff = _pulse_coefficients(intersection)
    atom = _atom_index(left)
    translated = left_coeff.copy()
    translated[:, 0] += atom
    recovered = translated.copy()
    recovered[:, 0] -= atom
    return SuperpositionLaw(
        left_coeff,
        right_coeff,
        union_coeff,
        intersection_coeff,
        translated,
        atom,
        float(
            np.linalg.norm(
                union_coeff + intersection_coeff - left_coeff - right_coeff
            )
        ),
        float(np.linalg.norm(left_coeff - _pulse_coefficients(left))),
        float(np.linalg.norm(recovered - left_coeff)),
    )


def prefix_tree_reconstruction(value: PrefixInput) -> PrefixReconstructionLaw:
    bits = _bits(value.bits)
    depth = _depth(value.depth, len(bits))
    _tolerance(value.tolerance)
    target = _cantor(bits)
    prefixes = _prefixes(bits, depth)
    dense = np.asarray([_cantor(prefix) for prefix in prefixes], dtype=float)
    quantized = np.floor(dense * (3 ** np.arange(1, depth + 1))).astype(int)
    bound = sum(2.0 / (3 ** (index + 1)) for index in range(depth, len(bits)))
    decoded = prefixes[-1]
    return PrefixReconstructionLaw(
        target,
        dense,
        prefixes,
        quantized,
        float(max(0.0, abs(dense[-1] - target) - bound)),
        float(
            sum(
                prefixes[index + 1][:-1] != prefixes[index]
                for index in range(len(prefixes) - 1)
            )
        ),
        float(sum(a != b for a, b in zip(decoded, bits[:depth], strict=True))),
    )


def fractal_skeleton_completion(value: PrefixInput) -> FractalSkeletonLaw:
    bits = _bits(value.bits)
    depth = _depth(value.depth, len(bits))
    _tolerance(value.tolerance)
    prefixes = _prefixes(bits, depth)
    skeleton = np.asarray([_cantor(prefix) for prefix in prefixes], dtype=float)
    complements = np.asarray([1.0 - item for item in skeleton], dtype=float)
    target = _cantor(bits)
    complement_target = 1.0 - target
    bound = sum(2.0 / (3 ** (index + 1)) for index in range(depth, len(bits)))
    return FractalSkeletonLaw(
        skeleton,
        complements,
        target,
        complement_target,
        float(max(0.0, abs(skeleton[-1] - target) - bound)),
        float(max(0.0, abs(complements[-1] - complement_target) - bound)),
        float(np.linalg.norm(complements - (1.0 - skeleton))),
    )


def boolean_decision_consensus(value: OperationalInput) -> DecisionConsensusLaw:
    bits, prefixes, labels = _validate_operational(
        value.bits, value.depth, value.resolved_prefixes, value.labels
    )
    _tolerance(value.tolerance)
    prefix = bits[: value.depth]
    mapping = dict(zip(prefixes, labels, strict=True))
    resolved = prefix in mapping
    extension_labels = (mapping[prefix],) if resolved else (-1, 1)
    reflected = tuple(-label for label in extension_labels)
    return DecisionConsensusLaw(
        prefix,
        resolved,
        tuple(int(item) for item in extension_labels),
        len(set(extension_labels)),
        0.0,
        float(abs(len(set(extension_labels)) - (1 if resolved else 2))),
        float(0 if set(reflected) == {-item for item in extension_labels} else 1),
    )


def adic_domain_repair(value: AdicRepairInput) -> AdicRepairLaw:
    cell = _vector3(value.cell, integer=True).astype(int)
    axes = _axis_bits(value.axis_bits)
    _tolerance(value.tolerance)
    repaired = tuple(
        bits[:-1] + (0,)
        if len(bits) >= 2 and all(bit == 1 for bit in bits[-2:])
        else bits
        for bits in axes
    )
    point = cell.astype(float) + np.asarray(
        [_binary(bits) for bits in repaired]
    )
    dual = dual_repair(DualRepairInput(value.values, value.tolerance))
    canonical = float(
        sum(
            int(len(bits) >= 2 and all(bit == 1 for bit in bits[-2:]))
            for bits in repaired
        )
    )
    return AdicRepairLaw(
        repaired,  # type: ignore[arg-type]
        point,
        dual.closure,
        canonical,
        float(
            np.linalg.norm(
                point - (cell + np.asarray([_binary(bits) for bits in repaired]))
            )
        ),
        float(dual.closure_residual + dual.repair_residual),
    )


def end_compactified_field(value: PrefixInput) -> EndFieldLaw:
    bits = _bits(value.bits)
    depth = _depth(value.depth, len(bits))
    _tolerance(value.tolerance)
    center = _axis_cantor(bits)
    tail = np.sum(_pulse_coefficients(bits), axis=0)
    field = center + tail
    prefix_bits = bits[:depth]
    prefix_center = _axis_cantor(prefix_bits)
    prefix_tail = np.sum(_pulse_coefficients(prefix_bits), axis=0)
    prefix_field = prefix_center + prefix_tail
    error = float(np.linalg.norm(field - prefix_field))
    center_bound = float(np.linalg.norm(center - prefix_center))
    tail_bound = float(np.linalg.norm(tail - prefix_tail))
    bound = center_bound + tail_bound
    return EndFieldLaw(
        center,
        tail,
        field,
        prefix_field,
        error,
        bound,
        float(np.linalg.norm(field - tail - center)),
        float(np.linalg.norm(field - center - tail)),
        float(max(0.0, error - bound)),
    )


def coverage_repair_field(value: CoverageFieldInput) -> CoverageRepairFieldLaw:
    cell = _vector3(value.cell, integer=True).astype(int)
    axes = _axis_bits(value.axis_bits)
    code = tuple(bit for axis in axes for bit in axis)
    depth = _depth(value.depth, len(code))
    _tolerance(value.tolerance)
    _, prefixes, labels = _validate_operational(
        code, depth, value.resolved_prefixes, value.labels
    )
    real = cell.astype(float) + np.asarray([_binary(bits) for bits in axes])
    omega = np.asarray([2.0 * _cantor(bits) - 1.0 for bits in axes])
    prefix = code[:depth]
    mapping = dict(zip(prefixes, labels, strict=True))
    decisions = (mapping[prefix],) if prefix in mapping else (-1, 1)
    fields = np.asarray(
        [real.astype(complex) + 1j * decision * omega for decision in decisions]
    )
    z = fields[0]
    v = np.conjugate(z)
    n = -np.conjugate(z)
    p = -z
    reflected = np.stack((z, v, n, p))
    vv = np.conjugate(v)
    nn = -np.conjugate(n)
    pp = -p
    repair = dual_repair(
        DualRepairInput(tuple(int(item) for item in cell), value.tolerance)
    )
    return CoverageRepairFieldLaw(
        real,
        omega,
        fields,
        reflected,
        len(fields),
        float(np.linalg.norm(np.real(fields) - real)),
        float(
            np.linalg.norm(vv - z)
            + np.linalg.norm(nn - z)
            + np.linalg.norm(pp - z)
        ),
        float(abs(len(fields) - (1 if prefix in mapping else 2))),
        float(repair.closure_residual + repair.repair_residual),
    )


def _remove(
    contract_id: ComplexId,
    complete: object,
    removed: object,
    tolerance: float,
):
    return source_removal_result(
        contract_id, complete, removed, tolerance=tolerance
    )


def _b1_remove_a1(value: SuperpositionInput):
    output = binary_superposition(value)
    complete = np.concatenate(
        (output.left_coefficients.ravel(), output.translated_coefficients.ravel())
    )
    removed = np.concatenate(
        (
            np.zeros_like(output.left_coefficients).ravel(),
            np.zeros_like(output.translated_coefficients).ravel(),
        )
    )
    return _remove(A1, complete, removed, value.tolerance)


def _b1_remove_a2(value: SuperpositionInput):
    output = binary_superposition(value)
    complete = np.asarray(
        (output.atom_index, np.linalg.norm(output.union_coefficients)), dtype=float
    )
    removed = np.asarray(
        (-1.0, np.linalg.norm(output.left_coefficients)), dtype=float
    )
    return _remove(A2, complete, removed, value.tolerance)


def _b2_remove_a3(value: PrefixInput):
    output = prefix_tree_reconstruction(value)
    return _remove(
        A3, output.dense_trace, np.zeros_like(output.dense_trace), value.tolerance
    )


def _b2_remove_a4(value: PrefixInput):
    output = prefix_tree_reconstruction(value)
    complete = np.asarray(
        [len(item) for item in output.prefix_codes], dtype=float
    )
    return _remove(A4, complete, np.zeros_like(complete), value.tolerance)


def _b3_remove_a5(value: PrefixInput):
    output = fractal_skeleton_completion(value)
    return _remove(
        A5, output.skeleton, np.zeros_like(output.skeleton), value.tolerance
    )


def _b3_remove_a6(value: PrefixInput):
    output = fractal_skeleton_completion(value)
    return _remove(
        A6,
        output.complement_skeleton,
        np.zeros_like(output.complement_skeleton),
        value.tolerance,
    )


def _b4_remove_a7(value: OperationalInput):
    output = boolean_decision_consensus(value)
    complete = np.asarray(output.extension_labels, dtype=float)
    return _remove(A7, complete, np.zeros_like(complete), value.tolerance)


def _b4_remove_a8(value: OperationalInput):
    output = boolean_decision_consensus(value)
    complete = np.asarray(
        (output.consensus_size, int(output.resolved)), dtype=float
    )
    return _remove(A8, complete, np.zeros_like(complete), value.tolerance)


def _b5_remove_a9(value: AdicRepairInput):
    output = adic_domain_repair(value)
    return _remove(
        A9,
        output.euclidean_point,
        np.zeros_like(output.euclidean_point),
        value.tolerance,
    )


def _b5_remove_a10(value: AdicRepairInput):
    output = adic_domain_repair(value)
    complete = np.asarray(output.dual_closure, dtype=float)
    return _remove(A10, complete, np.zeros_like(complete), value.tolerance)


def _c1_remove_b1(value: PrefixInput):
    output = end_compactified_field(value)
    return _remove(
        B1,
        output.binary_tail,
        np.zeros_like(output.binary_tail),
        value.tolerance,
    )


def _c1_remove_b2(value: PrefixInput):
    output = end_compactified_field(value)
    return _remove(
        B2, output.center, np.zeros_like(output.center), value.tolerance
    )


def _c2_remove(value: CoverageFieldInput, source: ComplexId, component: str):
    output = coverage_repair_field(value)
    if component == "fractal":
        complete = output.fractal_potential
    elif component == "decision":
        complete = np.asarray(
            (output.consensus_size, *np.imag(output.complex_field[0])),
            dtype=float,
        )
    else:
        complete = np.asarray(output.real_coverage, dtype=float)
    return _remove(source, complete, np.zeros_like(complete), value.tolerance)
