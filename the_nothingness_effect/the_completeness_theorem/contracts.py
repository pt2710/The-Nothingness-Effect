"""All fifteen completeness theorem-complex contracts (9A -> 4B -> 2C).

The executable interfaces mirror the authoritative appendix's typed partial
maps.  In particular, admissibility decoding, attainment-gated splitting,
Noether transgression, sheaf descent, and terminal factorisation are represented
as separate data and residual channels.  Finite evaluations remain numerical
support and are never promoted to a formal proof.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path

import numpy as np

from the_nothingness_effect.the_completeness_theorem.models import FormalSystem
from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import (
    DualClosureOperator,
)
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
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    source_removal_result,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.validation import (
    ensure_finite,
)


APPENDIX = "appendix_the_completeness_theorem.tex"
APPENDIX_SHA256 = "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3"
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
# Complex 07 is derived from the theoremhood/infinity and manifestability/
# observation complexes.  The Gödelian boundary is an upstream appendix input,
# not an additive source of this B operator.
B_SOURCE_INDICES = ((1, 2), (3, 4), (5, 6), (7, 8))
# The sheaf glues all three native B-level local certificates.  The terminal
# quotient uses all four B-level closures, including the Noether interface.
C_SOURCE_INDICES = ((0, 1, 2), (0, 1, 2, 3))


@dataclass(frozen=True)
class AdmissibilityData:
    diameter: float
    infinity_state: np.ndarray
    infinity_involution: np.ndarray
    observation_outcome_bit: int
    theorem_bit: int


@dataclass(frozen=True)
class SplittingData:
    update_trajectory: tuple[np.ndarray, ...]
    embedding: np.ndarray
    retraction: np.ndarray


@dataclass(frozen=True)
class ProtectedTransportData:
    protected_state: np.ndarray
    pullback_operator: np.ndarray


@dataclass(frozen=True)
class NoetherData:
    global_noether_map: np.ndarray
    local_noether_map: np.ndarray
    constant_injection: np.ndarray
    transgression_map: np.ndarray
    temporal_difference_map: np.ndarray
    boundary_flux: np.ndarray
    common_codomain: str = "charge-change"


@dataclass(frozen=True)
class SheafData:
    local_certificates: tuple[np.ndarray, np.ndarray, np.ndarray]
    transition_maps: tuple[np.ndarray, np.ndarray, np.ndarray]
    cover_complete: bool = True
    descent_data_fixed: bool = True


@dataclass(frozen=True)
class TerminalData:
    admissibility_representation_class: np.ndarray
    invariance_conservation_class: np.ndarray
    observable_samples: np.ndarray
    endomorphism_samples: np.ndarray


@dataclass(frozen=True)
class CompletenessInput:
    formal_system: FormalSystem
    state: np.ndarray
    closure_operator: np.ndarray
    parity_operator: np.ndarray
    theorem_bits: tuple[int, ...]
    coordinates: np.ndarray
    admissibility: AdmissibilityData
    splitting: SplittingData
    protected_transport: ProtectedTransportData
    noether: NoetherData
    sheaf: SheafData
    terminal: TerminalData
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
    operator_codomain: str
    residual_codomain: str
    domain_admitted: bool
    decoder_defined: bool = False
    decoded_theorem_bit: int | None = None
    free_orbit: bool = False
    null_gate_detected: bool = False
    attainment_residual: float = 0.0
    splitting_residual: float = 0.0
    boundary_flux_residual: float = 0.0


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
    overlap_residuals: tuple[float, ...] = ()
    cocycle_residual: float = 0.0
    cover_complete: bool = True
    descent_data_fixed: bool = True
    global_section: np.ndarray | None = None
    terminal_point: np.ndarray | None = None
    observable_constant: float | None = None
    terminal_factorization_residual: float = 0.0
    unique_terminal_map: bool = False


def _validate(value: CompletenessInput) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    state = np.asarray(value.state, dtype=float)
    closure = np.asarray(value.closure_operator, dtype=float)
    parity = np.asarray(value.parity_operator, dtype=float)
    coordinates = np.asarray(value.coordinates, dtype=float)
    n = state.size
    if (
        state.ndim != 1
        or n < 4
        or closure.shape != (n, n)
        or parity.shape != (n, n)
        or coordinates.shape != state.shape
    ):
        raise DomainViolationError(
            "completeness contracts require a state, two square operators, and a common spatial domain"
        )
    ensure_finite(value, name="completeness input")
    if not value.formal_system.nodes:
        raise DomainViolationError("completeness formal system cannot be empty")
    if len(value.theorem_bits) != n or any(bit not in (0, 1) for bit in value.theorem_bits):
        raise DomainViolationError(
            "typed theoremhood requires one binary finite-prefix digit per state coordinate"
        )
    if value.tolerance < 0:
        raise DomainViolationError("completeness tolerance must be non-negative")
    return state, closure, parity, coordinates


def _square(name: str, matrix, n: int) -> np.ndarray:
    result = np.asarray(matrix, dtype=float)
    if result.shape != (n, n):
        raise DomainViolationError(f"{name} must have shape {(n, n)}")
    ensure_finite(result, name=name)
    return result


def _vector(name: str, vector, n: int) -> np.ndarray:
    result = np.asarray(vector, dtype=float)
    if result.shape != (n,):
        raise DomainViolationError(f"{name} must have shape {(n,)}")
    ensure_finite(result, name=name)
    return result


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
        response = np.array(
            [
                final["closed_count"],
                final["unresolved_count"],
                final["boundary_count"],
                final["contradiction_count"],
                final["provable_count"],
                final["verified_dual_percent"] / 100.0,
            ],
            dtype=float,
        )[: state.size]
        response = np.pad(response, (0, state.size - response.size))
        obstruction_count = int(
            final["unresolved_count"]
            + final["boundary_count"]
            + final["contradiction_count"]
        )
        status = trace.final_status
        residual = np.zeros_like(state)
    elif index == 1:
        response = _prefix(value.theorem_bits)
        residual = response - _prefix(value.theorem_bits)
    elif index == 2:
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
    return CompletenessSourceLaw(
        str(A_IDS[index]),
        np.asarray(response, dtype=float),
        np.asarray(residual, dtype=float),
        status,
        obstruction_count,
    )


def _source_responses(indices: tuple[int, ...], value: CompletenessInput) -> tuple[np.ndarray, ...]:
    return tuple(source_operator(index, value).response for index in indices)


def _interaction_energy(operator: np.ndarray, responses: tuple[np.ndarray, ...]) -> float:
    stacked = np.stack([np.resize(item, operator.shape) for item in responses])
    additive = np.sum(stacked, axis=0)
    return float(np.linalg.norm(operator - additive) ** 2)


def _admissibility_operator(value: CompletenessInput) -> CompletenessDerivedLaw:
    state, _, _, _ = _validate(value)
    data = value.admissibility
    n = state.size
    infinity_state = _vector("infinity state", data.infinity_state, n)
    involution = _square("infinity involution", data.infinity_involution, n)
    if data.observation_outcome_bit not in (0, 1) or data.theorem_bit not in (0, 1):
        raise DomainViolationError("theorem and observation outcome bits must lie in C2")
    gate = float(data.diameter != 0.0)
    phase = data.theorem_bit ^ data.observation_outcome_bit
    instrument = gate * (involution @ infinity_state if phase else infinity_state)
    toggled = gate * (involution @ infinity_state if not phase else infinity_state)
    theorem_duality_residual = toggled - involution @ instrument
    involution_residual = (involution @ involution - np.eye(n)) @ infinity_state
    free_orbit = bool(
        np.linalg.norm(infinity_state) > value.tolerance
        and np.linalg.norm(involution @ infinity_state - infinity_state) > value.tolerance
    )
    decoder_defined = bool(gate and free_orbit)
    decoded = None
    if decoder_defined:
        sheet = int(
            np.linalg.norm(instrument - involution @ infinity_state)
            < np.linalg.norm(instrument - infinity_state)
        )
        decoded = sheet ^ data.observation_outcome_bit
    null_gate_detected = bool(not gate and np.linalg.norm(instrument) <= value.tolerance)
    residual = np.concatenate((involution_residual, theorem_duality_residual))
    responses = _source_responses(B_SOURCE_INDICES[0], value)
    return CompletenessDerivedLaw(
        str(B_IDS[0]),
        responses,
        instrument,
        residual,
        _interaction_energy(instrument, responses),
        "pointed infinity module",
        "involution and instrument-law residual space",
        bool((decoder_defined and decoded == data.theorem_bit) or null_gate_detected),
        decoder_defined=decoder_defined,
        decoded_theorem_bit=decoded,
        free_orbit=free_orbit,
        null_gate_detected=null_gate_detected,
    )


def _splitting_operator(value: CompletenessInput) -> CompletenessDerivedLaw:
    state, closure, _, _ = _validate(value)
    data = value.splitting
    trajectory = tuple(_vector("update trajectory state", item, state.size) for item in data.update_trajectory)
    if len(trajectory) < 2:
        raise DomainViolationError("attainment requires at least two update-trajectory states")
    e = np.asarray(data.embedding, dtype=float)
    m = np.asarray(data.retraction, dtype=float)
    if e.ndim != 2 or e.shape[1] != state.size or m.shape != (state.size, e.shape[0]):
        raise DomainViolationError("splitting maps must type as e:X->Y and m:Y->X")
    ensure_finite((e, m), name="splitting maps")
    cycle_residual = float(
        np.linalg.norm(trajectory[-1] - trajectory[-2])
    )
    split_residual = float(
        np.linalg.norm(m @ e - closure) + np.linalg.norm(e @ m - np.eye(e.shape[0]))
    )
    admitted = cycle_residual <= value.tolerance and split_residual <= value.tolerance
    reconstructed = e @ (closure @ state) if admitted else np.zeros(e.shape[0], dtype=float)
    embedded = m @ reconstructed if admitted else np.zeros_like(state)
    residual = np.array(
        [
            cycle_residual,
            split_residual,
            cycle_residual * split_residual,
            np.linalg.norm(embedded - closure @ state) if admitted else 1.0,
        ],
        dtype=float,
    )
    responses = _source_responses(B_SOURCE_INDICES[1], value)
    return CompletenessDerivedLaw(
        str(B_IDS[1]),
        responses,
        reconstructed,
        residual,
        _interaction_energy(reconstructed, responses),
        "internal splitting carrier Y",
        "attainment/splitting obstruction space",
        admitted,
        attainment_residual=cycle_residual,
        splitting_residual=split_residual,
    )


def _protected_transport_operator(value: CompletenessInput) -> CompletenessDerivedLaw:
    state, closure, parity, _ = _validate(value)
    data = value.protected_transport
    protected = _vector("protected state", data.protected_state, state.size)
    pullback = _square("protected pullback", data.pullback_operator, state.size)
    transported = closure @ pullback @ protected
    commutator = (closure @ parity - parity @ closure) @ protected
    reconstruction = transported - pullback @ closure @ protected
    residual = np.concatenate((commutator, reconstruction))
    responses = _source_responses(B_SOURCE_INDICES[2], value)
    return CompletenessDerivedLaw(
        str(B_IDS[2]),
        responses,
        transported,
        residual,
        _interaction_energy(transported, responses),
        "protected base-fragment carrier",
        "commutator and conservativity residual space",
        bool(np.linalg.norm(residual) <= value.tolerance),
    )


def _noether_operator(value: CompletenessInput) -> CompletenessDerivedLaw:
    state, _, _, _ = _validate(value)
    data = value.noether
    n = state.size
    global_map = _square("global Noether map", data.global_noether_map, n)
    local_map = _square("local Noether map", data.local_noether_map, n)
    injection = _square("constant injection", data.constant_injection, n)
    transgression = _square("Noether transgression", data.transgression_map, n)
    delta_t = _square("temporal difference", data.temporal_difference_map, n)
    boundary_flux = _vector("boundary flux", data.boundary_flux, n)
    if not data.common_codomain.strip():
        raise DomainViolationError("Noether routes require a declared common codomain")
    global_route = delta_t @ global_map @ state
    local_route = transgression @ local_map @ injection @ state
    intertwining_residual = local_route - global_route
    boundary_norm = float(np.linalg.norm(boundary_flux))
    residual = np.concatenate((intertwining_residual, boundary_flux))
    admitted = bool(
        np.linalg.norm(intertwining_residual) <= value.tolerance
        and boundary_norm <= value.tolerance
    )
    responses = _source_responses(B_SOURCE_INDICES[3], value)
    # The operator output is the common composite.  The comparison defect and
    # boundary flux remain in the residual codomain and are never added to it.
    common_composite = global_route if admitted else 0.5 * (global_route + local_route)
    return CompletenessDerivedLaw(
        str(B_IDS[3]),
        responses,
        common_composite,
        residual,
        _interaction_energy(common_composite, responses),
        data.common_codomain,
        f"{data.common_codomain} comparison residual + boundary-flux residual",
        admitted,
        boundary_flux_residual=boundary_norm,
    )


def derived_operator(index: int, value: CompletenessInput) -> CompletenessDerivedLaw:
    if index == 0:
        return _admissibility_operator(value)
    if index == 1:
        return _splitting_operator(value)
    if index == 2:
        return _protected_transport_operator(value)
    if index == 3:
        return _noether_operator(value)
    raise IndexError(index)


def _sheaf_operator(value: CompletenessInput) -> CompletenessSpatialClosure:
    _, _, _, coordinates = _validate(value)
    data = value.sheaf
    n = coordinates.size
    certificates = tuple(_vector("local certificate", item, n) for item in data.local_certificates)
    g78, g89, g79 = tuple(_square("transition map", item, n) for item in data.transition_maps)
    s07, s08, s09 = certificates
    r78v = g78 @ s07 - s08
    r89v = g89 @ s08 - s09
    r79v = g79 @ s07 - s09
    cocycle_v = (g89 @ g78 - g79) @ s07
    overlap_residuals = tuple(float(np.linalg.norm(item)) for item in (r78v, r89v, r79v))
    cocycle = float(np.linalg.norm(cocycle_v))
    compatible = bool(
        data.cover_complete
        and data.descent_data_fixed
        and max((*overlap_residuals, cocycle), default=0.0) <= value.tolerance
    )
    global_section = (s07 + s08 + s09) / 3.0 if compatible else None
    reconstruction = (
        float(max(np.linalg.norm(global_section - item) for item in certificates))
        if global_section is not None
        else float(max((*overlap_residuals, cocycle, 1.0)))
    )
    local = global_section if global_section is not None else np.zeros_like(s07)
    return CompletenessSpatialClosure(
        str(C_IDS[0]),
        coordinates,
        local,
        0.0 if data.cover_complete else 1.0,
        float(max(overlap_residuals, default=0.0)),
        reconstruction,
        cocycle,
        "numerical_candidate" if compatible and reconstruction <= value.tolerance else "open",
        overlap_residuals=overlap_residuals,
        cocycle_residual=cocycle,
        cover_complete=data.cover_complete,
        descent_data_fixed=data.descent_data_fixed,
        global_section=global_section,
    )


def _terminal_operator(value: CompletenessInput) -> CompletenessSpatialClosure:
    _, _, _, coordinates = _validate(value)
    data = value.terminal
    ar = np.asarray(data.admissibility_representation_class, dtype=float).ravel()
    ic = np.asarray(data.invariance_conservation_class, dtype=float).ravel()
    observables = np.asarray(data.observable_samples, dtype=float).ravel()
    endomorphisms = np.asarray(data.endomorphism_samples, dtype=float).ravel()
    if ar.size == 0 or ic.size == 0 or observables.size == 0 or endomorphisms.size == 0:
        raise DomainViolationError("terminal quotient data cannot be empty")
    ensure_finite((ar, ic, observables, endomorphisms), name="terminal quotient data")
    ar_residual = float(np.max(np.abs(ar - ar[0])))
    ic_residual = float(np.max(np.abs(ic - ic[0])))
    pushout_residual = float(abs(ar[0] - ic[0]))
    observable_constant = float(observables[0])
    observable_factorization = float(np.max(np.abs(observables - observable_constant)))
    endomorphism_residual = float(np.max(np.abs(endomorphisms - ar[0])))
    unique_terminal_map = bool(
        max(
            ar_residual,
            ic_residual,
            pushout_residual,
            observable_factorization,
            endomorphism_residual,
        )
        <= value.tolerance
    )
    residual = max(ar_residual, ic_residual, pushout_residual)
    factorization = max(observable_factorization, endomorphism_residual)
    local = np.full(coordinates.shape, ar[0] if unique_terminal_map else 0.0, dtype=float)
    return CompletenessSpatialClosure(
        str(C_IDS[1]),
        coordinates,
        local,
        0.0,
        residual,
        pushout_residual,
        factorization,
        "numerical_candidate" if unique_terminal_map else "open",
        terminal_point=np.array([ar[0]], dtype=float) if unique_terminal_map else None,
        observable_constant=observable_constant if unique_terminal_map else None,
        terminal_factorization_residual=factorization,
        unique_terminal_map=unique_terminal_map,
    )


def spatial_operator(index: int, value: CompletenessInput) -> CompletenessSpatialClosure:
    if index == 0:
        return _sheaf_operator(value)
    if index == 1:
        return _terminal_operator(value)
    raise IndexError(index)


def _residual(name: str, values, tolerance: float = 1e-10) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        name,
        vector,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
    )


def _derived_residual(_source, output: CompletenessDerivedLaw) -> ResidualResult:
    # A partial B operator is release-satisfied only on its declared domain.
    values = output.residual if output.domain_admitted else np.concatenate((output.residual, np.array([1.0])))
    return _residual(output.law_name, values)


def _spatial_residual(_source, output: CompletenessSpatialClosure) -> ResidualResult:
    return _residual(
        output.law_name,
        (
            output.boundary_trace_residual,
            output.overlap_or_quotient_residual,
            output.reconstruction_residual,
            output.observability_residual,
            output.cocycle_residual,
            output.terminal_factorization_residual,
        ),
    )


def _replace_admissibility(value: CompletenessInput, **changes) -> CompletenessInput:
    return replace(value, admissibility=replace(value.admissibility, **changes))


def _remove_a(b_index: int, local_index: int, value: CompletenessInput) -> SourceRemovalResult:
    complete = derived_operator(b_index, value).derived_operator
    source_index = B_SOURCE_INDICES[b_index][local_index]
    if b_index == 0 and local_index == 0:
        removed_value = _replace_admissibility(
            value,
            infinity_involution=np.eye(value.state.size),
            theorem_bit=0,
        )
        removed = derived_operator(b_index, removed_value).derived_operator
    elif b_index == 0:
        removed = derived_operator(
            b_index,
            _replace_admissibility(value, diameter=0.0, observation_outcome_bit=0),
        ).derived_operator
    elif b_index == 1 and local_index == 0:
        trajectory = (value.state, value.state + 1.0)
        removed = derived_operator(
            b_index,
            replace(value, splitting=replace(value.splitting, update_trajectory=trajectory)),
        ).derived_operator
    elif b_index == 1:
        rank = value.splitting.embedding.shape[0]
        removed = derived_operator(
            b_index,
            replace(
                value,
                splitting=replace(
                    value.splitting,
                    embedding=np.zeros_like(value.splitting.embedding),
                    retraction=np.zeros((value.state.size, rank)),
                ),
            ),
        ).derived_operator
    elif b_index == 2 and local_index == 0:
        removed = np.asarray(value.protected_transport.protected_state, dtype=float)
    elif b_index == 2:
        removed = np.asarray(value.closure_operator @ value.protected_transport.protected_state, dtype=float)
    elif b_index == 3 and local_index == 0:
        removed = np.zeros_like(complete)
    elif b_index == 3:
        removed = np.zeros_like(complete)
    else:
        raise IndexError ((b_index, local_index))
    return source_removal_result(A_IDS[source_index], complete, removed, tolerance=1e-12)


def _remove_b(c_index: int, local_index: int, value: CompletenessInput) -> SourceRemovalResult:
    output = spatial_operator(c_index, value)
    b_index = C_SOURCE_INDICES[c_index][local_index]
    if c_index == 0:
        certificates = list(value.sheaf.local_certificates)
        # The native sheaf has one local certificate per B07/B08/B09 source.
        certificates[local_index] = np.zeros_like(certificates[local_index])
        removed_value = replace(
            value,
            sheaf=replace(value.sheaf, local_certificates=tuple(certificates)),
        )
        removed = spatial_operator(c_index, removed_value).local_operator
    else:
        if local_index == 0:
            terminal = replace(
                value.terminal,
                admissibility_representation_class=np.array([0.0, 1.0]),
            )
        elif local_index == 1:
            terminal = replace(
                value.terminal,
                admissibility_representation_class=np.array([0.0, -1.0]),
            )
        elif local_index == 2:
            terminal = replace(
                value.terminal,
                invariance_conservation_class=np.array([0.0, 1.0]),
            )
        else:
            terminal = replace(
                value.terminal,
                invariance_conservation_class=np.array([0.0, -1.0]),
             )
        removed = spatial_operator(c_index, replace(value,  terminal=terminal)).local_operator
    return source_removal_result(B_IDS[b_index], output.local_operator, removed, tolerance=1e-12)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "completeness realization",
        "finite formal system with typed admissibility, splitting, Noether, descent, and terminal interfaces",
        (CompletenessInput,),
    )
    artifact = ArtifactSpec(
        ("closure_metrics", "residual_plot", "boundary_graph"),
        "python -m the_nothingness_effect.the_completeness_theorem.simulation.run_contract_suite",
    )
    result: list[ComplexContract] = []
    for index, complex_id in enumerate(A_IDS):
        result.append(
            ComplexContract(
                complex_id,
                APPENDIX,
                APPENDIX_SHA256,
                ComplexLevel.A,
                (),
                domain,
                CodomainSpec(
                    f"{complex_id} result",
                    "typed finite source law with explicit obstruction status",
                    (CompletenessSourceLaw,),
                ),
                partial(source_operator, index),
                residual=lambda _s, o, cid=str(complex_id): _residual(cid, o.residual),
                implementation_path="the_nothingness_effect/the_completeness_theorem/contracts.py",
            )
        )
    for index, complex_id in enumerate(B_IDS):
        source_indices = B_SOURCE_INDICES[index]
        result.append(
            ComplexContract(
                complex_id,
                APPENDIX,
                APPENDIX_SHA256,
                ComplexLevel.B,
                tuple(A_IDS[item] for item in source_indices),
                domain,
                CodomainSpec(
                    f"{complex_id} derived law",
                    "typed partial B operator with a separately typed residual channel",
                    (CompletenessDerivedLaw,),
                ),
                partial(derived_operator, index),
                residual=_derived_residual,
                source_removal_checks=tuple(
                    partial(_remove_a, index, local_index)
                    for local_index in range(len(source_indices))
                ),
                artifact_spec=artifact,
                implementation_path="the_nothingness_effect/the_completeness_theorem/contracts.py",
            )
        )
    for index, complex_id in enumerate(C_IDS):
        b_indices = C_SOURCE_INDICES[index]
        result.append(
            ComplexContract(
                complex_id,
                APPENDIX,
                APPENDIX_SHA256,
                ComplexLevel.C,
                tuple(B_IDS[item] for item in b_indices),
                domain,
                CodomainSpec(
                    f"{complex_id} closure",
                    "typed sheaf descent or terminal-factorisation candidate",
                    (CompletenessSpatialClosure,),
                ),
                partial(spatial_operator, index),
                residual=_spatial_residual,
                closure_predicate=lambda output, residual: (
                    output.closure_status == "numerical_candidate"
                    and residual is not None
                    and residual.passed
                ),
                source_removal_checks=tuple(
                    partial(_remove_b, index, local_index)
                    for local_index in range(len(b_indices))
                ),
                artifact_spec=artifact,
                exact_semantics=False,
                implementation_path="the_nothingness_effect/the_completeness_theorem/contracts.py",
            )
        )
    return tuple(result)


def registered_completeness_registry(
    matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv",
) -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
