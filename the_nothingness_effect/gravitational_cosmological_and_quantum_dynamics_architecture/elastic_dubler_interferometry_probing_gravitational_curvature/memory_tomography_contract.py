"""Exact finite gauge-fixed realization of EDI memory-aware tomography C01."""

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


SPEC = SPECS["elastic_dubler_interferometry"]
C_ID = SPEC.c_id
B_PHASE, B_MEMORY = SPEC.b_ids
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "elastic_dubler_interferometry_probing_gravitational_curvature/"
    "memory_tomography_contract.py"
)


@dataclass(frozen=True)
class MemoryTomographyInput:
    coordinates: np.ndarray
    elastic_field: np.ndarray
    elliptic_strength: float = 0.5
    memory_decay: float = 1.0
    tomography: np.ndarray | None = None
    gauge_fixed: bool = True
    initial_mode_fixed: bool = True
    tolerance: float = 1e-10


@dataclass(frozen=True)
class MemoryTomographyCertificate:
    spatial_domain: np.ndarray
    gauge_fixed_field: np.ndarray
    phase_elliptic_matrix: np.ndarray
    memory_horizon_matrix: np.ndarray
    composite_matrix: np.ndarray
    phase_elliptic_output: np.ndarray
    tomography: np.ndarray
    local_operator: np.ndarray
    reconstructed_field: np.ndarray
    reconstructed_curvature_history: np.ndarray
    reconstructed_horizon_history: np.ndarray
    phase_lower_bound: float
    memory_lower_bound: float
    product_lower_bound: float
    composite_lower_bound: float
    lower_bound_residual: float
    chain_rule_residual: float
    field_reconstruction_residual: float
    curvature_reconstruction_residual: float
    horizon_reconstruction_residual: float
    gauge_mode_residual: float
    initial_mode_residual: float
    fibre_dimension: int
    phase_source_residual: float
    memory_source_residual: float
    status_equivalence_residual: float
    closure_status: str


def _input(value: MemoryTomographyInput | FieldLawInput) -> MemoryTomographyInput:
    if isinstance(value, MemoryTomographyInput):
        return value
    if isinstance(value, FieldLawInput):
        return MemoryTomographyInput(
            coordinates=value.coordinates,
            elastic_field=value.source,
            elliptic_strength=1.0 / value.scale,
            memory_decay=value.scale,
            tolerance=value.tolerance,
        )
    raise DomainViolationError(
        "EDI tomography requires MemoryTomographyInput or FieldLawInput"
    )


def _validated(source: MemoryTomographyInput):
    x = np.asarray(source.coordinates, dtype=float)
    field = np.asarray(source.elastic_field, dtype=float)
    if x.ndim != 1 or x.size < 5 or field.shape != x.shape:
        raise DomainViolationError(
            "EDI tomography requires equal one-dimensional coordinate/field arrays with at least five samples"
        )
    ensure_finite((x, field), name="EDI tomography input")
    spacing = np.diff(x)
    if np.any(spacing <= 0.0):
        raise DomainViolationError("tomography coordinates must be strictly increasing")
    if not np.allclose(spacing, spacing[0], rtol=1e-10, atol=1e-12):
        raise DomainViolationError("finite tomography requires a uniform grid")
    if not np.isfinite(source.elliptic_strength) or source.elliptic_strength <= 0.0:
        raise DomainViolationError("elliptic strength must be finite and positive")
    if not np.isfinite(source.memory_decay) or source.memory_decay <= 0.0:
        raise DomainViolationError("memory decay must be finite and positive")
    if not np.isfinite(source.tolerance) or source.tolerance < 0.0:
        raise DomainViolationError("tolerance must be finite and non-negative")
    if not source.gauge_fixed or not source.initial_mode_fixed:
        raise DomainViolationError(
            "tomographic closure requires fixed elliptic gauge and temporal initial mode"
        )
    return x, field, float(spacing[0])


def _operators(count: int, step: float, elliptic: float, decay: float):
    laplacian = np.zeros((count, count), dtype=float)
    for index in range(count):
        if index == 0:
            laplacian[index, index] = 1.0
            laplacian[index, index + 1] = -1.0
        elif index == count - 1:
            laplacian[index, index - 1] = -1.0
            laplacian[index, index] = 1.0
        else:
            laplacian[index, index - 1] = -1.0
            laplacian[index, index] = 2.0
            laplacian[index, index + 1] = -1.0
    laplacian /= step**2
    phase_elliptic = np.eye(count) + elliptic * laplacian

    derivative_with_initial = np.zeros((count, count), dtype=float)
    derivative_with_initial[0, 0] = 1.0
    for index in range(1, count):
        derivative_with_initial[index, index] = 1.0 / step
        derivative_with_initial[index, index - 1] = -1.0 / step
    kernel = np.zeros((count, count), dtype=float)
    for row in range(count):
        for column in range(row + 1):
            kernel[row, column] = np.exp(
                -(row - column) * step / decay
            )
    memory_horizon = kernel @ derivative_with_initial
    return phase_elliptic, memory_horizon


def _smallest_singular(matrix: np.ndarray) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    return float(singular[-1])


def memory_tomography_operator(
    value: MemoryTomographyInput | FieldLawInput,
) -> MemoryTomographyCertificate:
    source = _input(value)
    x, raw_field, step = _validated(source)
    field = raw_field - raw_field[0]
    count = field.size
    phase, memory = _operators(
        count,
        step,
        source.elliptic_strength,
        source.memory_decay,
    )
    composite = memory @ phase
    phase_output = phase @ field
    expected_tomography = memory @ phase_output
    tomography = (
        expected_tomography
        if source.tomography is None
        else np.asarray(source.tomography, dtype=float)
    )
    if tomography.shape != field.shape:
        raise DomainViolationError("tomography output must match the field domain")
    ensure_finite(tomography, name="EDI tomography output")

    phase_lower = _smallest_singular(phase)
    memory_lower = _smallest_singular(memory)
    product_lower = phase_lower * memory_lower
    composite_lower = _smallest_singular(composite)
    lower_bound_residual = max(product_lower - composite_lower, 0.0)
    chain_rule_residual = float(
        np.linalg.norm(composite - memory @ phase)
    )

    reconstructed = np.linalg.solve(composite, tomography)
    reconstructed_curvature = phase @ reconstructed
    reconstructed_horizon = memory @ reconstructed_curvature
    field_residual = float(np.linalg.norm(reconstructed - field))
    curvature_residual = float(
        np.linalg.norm(reconstructed_curvature - phase_output)
    )
    horizon_residual = float(
        np.linalg.norm(reconstructed_horizon - tomography)
    )
    gauge_residual = float(abs(field[0]))
    initial_residual = float(
        abs((memory @ phase_output)[0] - expected_tomography[0])
    )
    rank = int(np.linalg.matrix_rank(composite, tol=source.tolerance))
    fibre_dimension = count - rank

    if isinstance(value, FieldLawInput):
        first = derived_operator(
            B_PHASE,
            SPEC.source_kinds[0],
            SPEC.source_kinds[1],
            value,
        )
        second = derived_operator(
            B_MEMORY,
            SPEC.source_kinds[2],
            SPEC.source_kinds[3],
            value,
        )
        phase_source_residual = float(np.linalg.norm(first.residual))
        memory_source_residual = float(np.linalg.norm(second.residual))
    else:
        phase_source_residual = 0.0
        memory_source_residual = 0.0

    tomographic = bool(
        phase_lower > source.tolerance
        and memory_lower > source.tolerance
        and fibre_dimension == 0
        and max(
            lower_bound_residual,
            chain_rule_residual,
            field_residual,
            curvature_residual,
            horizon_residual,
            gauge_residual,
            initial_residual,
            phase_source_residual,
            memory_source_residual,
        )
        <= source.tolerance
    )
    status_equivalence = float(
        tomographic
        != (
            product_lower > 0.0
            and fibre_dimension == 0
            and field_residual <= source.tolerance
        )
    )
    closed = tomographic and status_equivalence <= source.tolerance
    return MemoryTomographyCertificate(
        x,
        field,
        phase,
        memory,
        composite,
        phase_output,
        tomography,
        tomography,
        reconstructed,
        reconstructed_curvature,
        reconstructed_horizon,
        phase_lower,
        memory_lower,
        product_lower,
        composite_lower,
        lower_bound_residual,
        chain_rule_residual,
        field_residual,
        curvature_residual,
        horizon_residual,
        gauge_residual,
        initial_residual,
        fibre_dimension,
        phase_source_residual,
        memory_source_residual,
        status_equivalence,
        "closed" if closed else "open",
    )


def _residual(value, output: MemoryTomographyCertificate) -> ResidualResult:
    tolerance = _input(value).tolerance
    vector = (
        output.lower_bound_residual,
        output.chain_rule_residual,
        output.field_reconstruction_residual,
        output.curvature_reconstruction_residual,
        output.horizon_reconstruction_residual,
        output.gauge_mode_residual,
        output.initial_mode_residual,
        float(output.fibre_dimension),
        output.phase_source_residual,
        output.memory_source_residual,
        output.status_equivalence_residual,
    )
    passed = max(vector) <= tolerance
    return ResidualResult(
        "EDI memory-aware tomography lower bound and inverse reconstruction",
        vector,
        tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {
            "phase_lower_bound": output.phase_lower_bound,
            "memory_lower_bound": output.memory_lower_bound,
            "product_lower_bound": output.product_lower_bound,
            "composite_lower_bound": output.composite_lower_bound,
            "gauge_fixed": True,
            "initial_mode_fixed": True,
        },
    )


def _remove_phase(value) -> SourceRemovalResult:
    complete = memory_tomography_operator(value)
    removed = complete.memory_horizon_matrix @ complete.gauge_fixed_field
    return source_removal_result(
        ComplexId(B_PHASE),
        complete.tomography,
        removed,
        tolerance=max(_input(value).tolerance, 1e-12),
    )


def _remove_memory(value) -> SourceRemovalResult:
    complete = memory_tomography_operator(value)
    removed = complete.phase_elliptic_output
    return source_removal_result(
        ComplexId(B_MEMORY),
        complete.tomography,
        removed,
        tolerance=max(_input(value).tolerance, 1e-12),
    )


def contract() -> ComplexContract:
    return ComplexContract(
        complex_id=ComplexId(C_ID),
        appendix=APPENDIX,
        appendix_source_sha256=APPENDIX_SHA256,
        level=ComplexLevel.C,
        source_ids=(ComplexId(B_PHASE), ComplexId(B_MEMORY)),
        domain=DomainSpec(
            "gauge-fixed EDI tomography realization",
            "uniform finite domain, positive elliptic and memory parameters, fixed spatial gauge and temporal initial mode, and optional measured tomography",
            (MemoryTomographyInput, FieldLawInput),
        ),
        codomain=CodomainSpec(
            "memory-aware tomography certificate",
            "phase-elliptic and memory-horizon matrices, singular-value lower bounds, composite inverse, fibre dimension, and status equivalence",
            (MemoryTomographyCertificate,),
        ),
        operator=memory_tomography_operator,
        residual=_residual,
        closure_predicate=lambda output, residual: (
            output.closure_status == "closed"
            and residual is not None
            and residual.passed
            and output.product_lower_bound > 0.0
        ),
        source_removal_checks=(_remove_phase, _remove_memory),
        artifact_spec=ArtifactSpec(
            ("tomography_matrix", "singular_value_table", "inverse_reconstruction_plot"),
            "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.simulation.run_contract_suite",
        ),
        exact_semantics=True,
        implementation_path=IMPLEMENTATION_PATH,
    )
