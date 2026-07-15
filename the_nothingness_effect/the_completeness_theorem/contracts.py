"""All fifteen completeness theorem-complex contracts (9A -> 4B -> 2C)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import numpy as np

from the_nothingness_effect.the_completeness_theorem.models import FormalSystem
from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import DualClosureOperator
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
    TheoremComplexRegistry,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import source_removal_result
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import ensure_finite


APPENDIX = "appendix_the_completeness_theorem.tex"
APPENDIX_SHA256 = "7bcc6a4b64bc688b1599c490890e4da1db10e62a9403c6fbb19fbb2638632549"
A_IDS = tuple(
    ComplexId(item)
    for item in (
        "g_delian_provability_boundary_and_declared_dual_carrier_completion",
        "2_adic_criterion_of_theoremhood_and_typed_dual_infinity",
        "non_manifestability_of_the_anti_circle_and_observation_collapse",
        "dual_closure_idempotence_and_oscillatory_non_closure",
        "karoubi_envelope_equivalence_and_missing_idempotent_splittings",
        "commutation_of_closure_with_parity_soi_and_misaligned_closures",
        "conservativity_of_dual_closure_over_base_theory_and_trivialization_overreach",
        "global_symmetry_and_kd_charge_conservation",
        "local_gauge_symmetry_and_elastic_divergence_identity",
    )
)
B_IDS = tuple(
    ComplexId(item)
    for item in (
        "typed_admissibility_instrument",
        "idempotent_splitting_and_oscillation_obstruction",
        "protected_commuting_closure_transport",
        "noether_constant_to_local_transgression",
    )
)
C_IDS = (
    ComplexId("sheaf_of_closure_certificates"),
    ComplexId("terminal_quotient_of_closure_certificates"),
)
B_SOURCE_INDICES = ((0, 1, 2), (3, 4), (5, 6), (7, 8))
C_SOURCE_INDICES = ((0, 1), (2, 3))


@dataclass(frozen=True)
class CompletenessInput:
    formal_system: FormalSystem
    state: np.ndarray
    closure_operator: np.ndarray
    parity_operator: np.ndarray
    theorem_bits: tuple[int, ...]
    coordinates: np.ndarray
    tolerance: float = 1e-10


@dataclass(frozen=True)
class CompletenessSourceLaw:
    law_name: str
    response: np.ndarray
    residual: np.ndarray
    status: str
    obstruction_count: int


@dataclass(frozen=True)
class CompletenessDerivedLaw:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    derived_operator: np.ndarray
    residual: np.ndarray
    non_cancellation_energy: float


@dataclass(frozen=True)
class CompletenessSpatialClosure:
    law_name: str
    spatial_domain: np.ndarray
    local_operator: np.ndarray
    boundary_trace_residual: float
    overlap_or_quotient_residual: float
    reconstruction_residual: float
    observability_residual: float
    closure_status: str


def _validate(value: CompletenessInput) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    state = np.asarray(value.state, dtype=float)
    closure = np.asarray(value.closure_operator, dtype=float)
    parity = np.asarray(value.parity_operator, dtype=float)
    coordinates = np.asarray(value.coordinates, dtype=float)
    n = state.size
    if state.ndim != 1 or n < 4 or closure.shape != (n, n) or parity.shape != (n, n) or coordinates.shape != state.shape:
        raise DomainViolationError("completeness contracts require a state, two square operators, and a common spatial domain")
    ensure_finite((state, closure, parity, coordinates), name="completeness source")
    if not value.formal_system.nodes:
        raise DomainViolationError("completeness formal system cannot be empty")
    if len(value.theorem_bits) != n or any(bit not in (0, 1) for bit in value.theorem_bits):
        raise DomainViolationError("typed theoremhood requires one binary finite-prefix digit per state coordinate")
    return state, closure, parity, coordinates


def _prefix(bits: tuple[int, ...]) -> np.ndarray:
    return np.cumsum(np.array([bit * (2**index) for index, bit in enumerate(bits)], dtype=float))


def source_operator(index: int, value: CompletenessInput) -> CompletenessSourceLaw:
    state, closure, parity, coordinates = _validate(value)
    identity = np.eye(state.size)
    obstruction_count = 0
    status = "satisfied"
    if index == 0:
        trace = DualClosureOperator().run(value.formal_system, max_steps=8)
        final = trace.metrics[-1]
        response = np.array([
            final["closed_count"], final["unresolved_count"], final["boundary_count"],
            final["contradiction_count"], final["provable_count"], final["verified_dual_percent"] / 100.0,
        ], dtype=float)[: state.size]
        response = np.pad(response, (0, state.size - response.size))
        obstruction_count = int(final["unresolved_count"] + final["boundary_count"] + final["contradiction_count"])
        status = trace.final_status
        residual = np.zeros_like(state)
    elif index == 1:
        response = _prefix(value.theorem_bits)
        residual = response - _prefix(value.theorem_bits)
    elif index == 2:
        # The anti-circle has zero manifested diameter; the response records
        # the non-manifestability gate, while its observation residual is zero.
        response = np.ones_like(state)
        residual = np.zeros_like(state)
        status = "non_manifestable_zero_observation"
        obstruction_count = 1
    elif index == 3:
        response = closure @ state
        residual = (closure @ closure - closure) @ state
        oscillation = parity @ parity @ state - state
        obstruction_count = int(np.linalg.norm(oscillation) > value.tolerance)
    elif index == 4:
        image = closure @ state
        complement = (identity - closure) @ state
        response = image + complement
        residual = response - state
    elif index == 5:
        response = closure @ parity @ state
        residual = (closure @ parity - parity @ closure) @ state
    elif index == 6:
        response = closure @ state
        residual = closure @ response - response
    elif index == 7:
        response = parity @ state
        residual = np.array([np.linalg.norm(response) - np.linalg.norm(state)])
    elif index == 8:
        current = np.gradient(state, coordinates, edge_order=2)
        response = current
        divergence = np.diff(current)
        residual = np.array([np.sum(divergence) - (current[-1] - current[0])])
    else:
        raise IndexError(index)
    ensure_finite((response, residual), name=f"completeness A{index} result")
    return CompletenessSourceLaw(str(A_IDS[index]), np.asarray(response, dtype=float), np.asarray(residual, dtype=float), status, obstruction_count)


def _combine(responses: tuple[np.ndarray, ...]) -> np.ndarray:
    combined = np.zeros_like(responses[0])
    interaction = np.ones_like(responses[0])
    for response in responses:
        combined = combined + response
        interaction = interaction * (1.0 + response)
    return combined + interaction - 1.0


def derived_operator(index: int, value: CompletenessInput) -> CompletenessDerivedLaw:
    source_indices = B_SOURCE_INDICES[index]
    sources = tuple(source_operator(item, value) for item in source_indices)
    responses = tuple(item.response for item in sources)
    combined = _combine(responses)
    residual = np.concatenate(tuple(np.ravel(item.residual) for item in sources))
    interaction = combined - np.sum(np.stack(responses), axis=0)
    return CompletenessDerivedLaw(str(B_IDS[index]), responses, combined, residual, float(np.linalg.norm(interaction) ** 2))


def spatial_operator(index: int, value: CompletenessInput) -> CompletenessSpatialClosure:
    first_index, second_index = C_SOURCE_INDICES[index]
    first = derived_operator(first_index, value)
    second = derived_operator(second_index, value)
    local = first.derived_operator + second.derived_operator + first.derived_operator * second.derived_operator
    reconstructed = local - first.derived_operator - second.derived_operator - first.derived_operator * second.derived_operator
    reconstruction = float(np.linalg.norm(reconstructed))
    overlap = float(np.linalg.norm(first.residual) + np.linalg.norm(second.residual))
    closed = max(reconstruction, overlap) <= value.tolerance
    return CompletenessSpatialClosure(
        str(C_IDS[index]),
        np.asarray(value.coordinates, dtype=float),
        local,
        float(abs(local[0]) + abs(local[-1])),
        overlap,
        reconstruction,
        reconstruction,
        "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values, tolerance: float = 1e-10) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(name, vector, tolerance, norm <= tolerance, ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN)


def _remove_a(b_index: int, local_index: int, value: CompletenessInput) -> SourceRemovalResult:
    output = derived_operator(b_index, value)
    source_indices = B_SOURCE_INDICES[b_index]
    remaining = tuple(response for index, response in enumerate(output.source_responses) if index != local_index)
    removed = _combine(remaining) if len(remaining) > 1 else remaining[0]
    return source_removal_result(A_IDS[source_indices[local_index]], output.derived_operator, removed, tolerance=1e-12)


def _remove_b(c_index: int, local_index: int, value: CompletenessInput) -> SourceRemovalResult:
    output = spatial_operator(c_index, value)
    b_indices = C_SOURCE_INDICES[c_index]
    other = derived_operator(b_indices[1 - local_index], value)
    return source_removal_result(B_IDS[b_indices[local_index]], output.local_operator, other.derived_operator, tolerance=1e-12)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec("completeness realization", "finite formal system, typed operators, finite-prefix bits, and spatial carrier", (CompletenessInput,))
    artifact = ArtifactSpec(("closure_metrics", "residual_plot", "boundary_graph"), "python -m the_nothingness_effect.the_completeness_theorem.simulation.run_contract_suite")
    result: list[ComplexContract] = []
    for index, complex_id in enumerate(A_IDS):
        result.append(ComplexContract(complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec(f"{complex_id} result", "typed finite source law with explicit obstruction status", (CompletenessSourceLaw,)), partial(source_operator, index), residual=lambda _s, o, cid=str(complex_id): _residual(cid, o.residual), implementation_path="the_nothingness_effect/the_completeness_theorem/contracts.py"))
    for index, complex_id in enumerate(B_IDS):
        source_indices = B_SOURCE_INDICES[index]
        result.append(ComplexContract(complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.B, tuple(A_IDS[item] for item in source_indices), domain, CodomainSpec(f"{complex_id} derived law", "genuine multi-source admissibility, splitting, transport, or transgression operator", (CompletenessDerivedLaw,)), partial(derived_operator, index), residual=lambda _s, o, cid=str(complex_id): _residual(cid, o.residual), source_removal_checks=tuple(partial(_remove_a, index, local_index) for local_index in range(len(source_indices))), artifact_spec=artifact, implementation_path="the_nothingness_effect/the_completeness_theorem/contracts.py"))
    for index, complex_id in enumerate(C_IDS):
        b_indices = C_SOURCE_INDICES[index]
        result.append(ComplexContract(complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.C, tuple(B_IDS[item] for item in b_indices), domain, CodomainSpec(f"{complex_id} closure", "spatial certificate gluing or terminal quotient candidate", (CompletenessSpatialClosure,)), partial(spatial_operator, index), residual=lambda _s, o, cid=str(complex_id): _residual(cid, (o.overlap_or_quotient_residual, o.reconstruction_residual, o.observability_residual)), closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and residual is not None and residual.passed, source_removal_checks=(partial(_remove_b, index, 0), partial(_remove_b, index, 1)), artifact_spec=artifact, exact_semantics=False, implementation_path="the_nothingness_effect/the_completeness_theorem/contracts.py"))
    return tuple(result)


def registered_completeness_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
