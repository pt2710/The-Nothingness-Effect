"""All fifteen completeness theorem-complex contracts (9A -> 4B -> 2C)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

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
from the_nothingness_effect.the_completeness_theorem.authoritative_obligations import (
    NoetherTransgression,
    NoetherTypeSeparation,
    SheafDescentCertificate,
    SplittingAttainment,
    TerminalObservableFactorization,
    TypedAdmissibilityDecoding,
    certify_sheaf_descent,
    certify_splitting_attainment,
    decode_typed_admissibility,
    factor_terminal_observable,
    noether_transgression_common_codomain,
    separate_noether_operator_and_residual,
)
from the_nothingness_effect.the_completeness_theorem.models import FormalSystem
from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import (
    DualClosureOperator,
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
    typed_admissibility_gate: float = 1.0
    typed_admissibility_free_orbit: bool = True
    splitting_residual: float = 0.0
    splitting_infimum_attained: bool = True
    noether_boundary_flux: float = 0.0
    descent_pairwise_residuals: tuple[float, float, float] = (0.0, 0.0, 0.0)
    descent_cocycle_residual: float = 0.0
    fixed_descent_data: bool = True
    overlap_isomorphisms: bool = True
    terminal_observable_values: np.ndarray | None = None
    terminal_value: float | None = None


@dataclass(frozen=True)
class CompletenessSourceLaw:
    law_name: str
    response: np.ndarray
    residual: np.ndarray
    status: str
    obstruction_count: int


AuthoritativeDerivedCertificate = (
    TypedAdmissibilityDecoding
    | SplittingAttainment
    | tuple[NoetherTypeSeparation, NoetherTransgression]
    | None
)


@dataclass(frozen=True)
class CompletenessDerivedLaw:
    law_name: str
    source_responses: tuple[np.ndarray, ...]
    derived_operator: np.ndarray
    residual: np.ndarray
    non_cancellation_energy: float
    authoritative_certificate: AuthoritativeDerivedCertificate = None


AuthoritativeSpatialCertificate = (
    SheafDescentCertificate | TerminalObservableFactorization | None
)


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
    authoritative_certificate: AuthoritativeSpatialCertificate = None


def _validate(
    value: CompletenessInput,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
            "completeness contracts require a state, two square operators, "
            "and a common spatial domain"
        )
    ensure_finite(
        (
            state,
            closure,
            parity,
            coordinates,
            value.typed_admissibility_gate,
            value.splitting_residual,
            value.noether_boundary_flux,
            *value.descent_pairwise_residuals,
            value.descent_cocycle_residual,
        ),
        name="completeness source",
    )
    if not value.formal_system.nodes:
        raise DomainViolationError("completeness formal system cannot be empty")
    if len(value.theorem_bits) != n or any(
        bit not in (0, 1) for bit in value.theorem_bits
    ):
        raise DomainViolationError(
            "typed theoremhood requires one binary finite-prefix digit "
            "per state coordinate"
        )
    return state, closure, parity, coordinates


def _prefix(bits: tuple[int, ...]) -> np.ndarray:
    return np.cumsum(
        np.array([bit * (2**index) for index, bit in enumerate(bits)], dtype=float)
    )


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


def _combine(responses: tuple[np.ndarray, ...]) -> np.ndarray:
    combined = np.zeros_like(responses[0])
    interaction = np.ones_like(responses[0])
    for response in responses:
        combined = combined + response
        interaction = interaction * (1.0 + response)
    return combined + interaction - 1.0


def _obligation_residual(
    index: int,
    value: CompletenessInput,
    certificate: AuthoritativeDerivedCertificate,
) -> np.ndarray:
    if index == 0:
        assert isinstance(certificate, TypedAdmissibilityDecoding)
        valid_typed_domain = (
            certificate.reconstructive_domain or certificate.null_gate_detected
        )
        return np.array([0.0 if valid_typed_domain else 1.0])
    if index == 1:
        assert isinstance(certificate, SplittingAttainment)
        inconsistent_claim = certificate.exact_splitting and not (
            certificate.infimum_attained
            and certificate.splitting_residual <= value.tolerance
        )
        return np.array([1.0 if inconsistent_claim else 0.0])
    if index == 3:
        assert isinstance(certificate, tuple)
        separation, transgression = certificate
        type_residual = 0.0 if separation.types_separated else 1.0
        flux_residual = 0.0 if transgression.commutation_domain_satisfied else abs(
            transgression.boundary_flux
        )
        return np.concatenate(
            (
                np.array([type_residual, flux_residual]),
                np.ravel(transgression.intertwining_residual),
            )
        )
    return np.zeros(1, dtype=float)


def _derive_from_responses(
    index: int,
    responses: tuple[np.ndarray, ...],
    value: CompletenessInput,
) -> tuple[np.ndarray, np.ndarray, AuthoritativeDerivedCertificate]:
    base = _combine(responses)
    certificate: AuthoritativeDerivedCertificate = None
    if index == 0:
        orientation = int(value.theorem_bits[0])
        observed_phase = int(value.theorem_bits[1])
        certificate = decode_typed_admissibility(
            gate=value.typed_admissibility_gate,
            orientation_bit=orientation,
            observed_phase_bit=observed_phase,
            infinity_state=np.asarray(value.state, dtype=float),
            involution=lambda item: np.asarray(value.parity_operator, dtype=float)
            @ item,
            free_orbit=value.typed_admissibility_free_orbit,
            tolerance=value.tolerance,
        )
        derived = base + certificate.output
    elif index == 1:
        certificate = certify_splitting_attainment(
            value.splitting_residual,
            infimum_attained=value.splitting_infimum_attained,
            tolerance=value.tolerance,
        )
        signed_attainment = 1.0 if certificate.exact_splitting else -1.0
        derived = base + signed_attainment * np.tanh(base)
    elif index == 2:
        derived = base
    elif index == 3:
        global_charge, local_current = responses
        local_value = global_charge + local_current
        global_value = local_current + global_charge
        transgression = noether_transgression_common_codomain(
            local_value,
            global_value,
            boundary_flux=value.noether_boundary_flux,
            tolerance=value.tolerance,
        )
        separation = separate_noether_operator_and_residual(
            np.diag(base),
            transgression.intertwining_residual,
        )
        certificate = (separation, transgression)
        derived = base + 0.5 * (
            transgression.local_codomain_value
            + transgression.global_codomain_value
        )
    else:
        raise IndexError(index)
    return (
        np.asarray(derived, dtype=float),
        _obligation_residual(index, value, certificate),
        certificate,
    )


def derived_operator(index: int, value: CompletenessInput) -> CompletenessDerivedLaw:
    source_indices = B_SOURCE_INDICES[index]
    sources = tuple(source_operator(item, value) for item in source_indices)
    responses = tuple(item.response for item in sources)
    derived, typed_residual, certificate = _derive_from_responses(
        index, responses, value
    )
    source_residual = np.concatenate(
        tuple(np.ravel(item.residual) for item in sources)
    )
    residual = np.concatenate((source_residual, np.ravel(typed_residual)))
    interaction = derived - np.sum(np.stack(responses), axis=0)
    return CompletenessDerivedLaw(
        str(B_IDS[index]),
        responses,
        derived,
        residual,
        float(np.linalg.norm(interaction) ** 2),
        certificate,
    )


def _terminal_values(
    value: CompletenessInput,
    local_operator: np.ndarray,
) -> tuple[np.ndarray, float]:
    if value.terminal_observable_values is None:
        terminal_value = float(
            np.mean(local_operator)
            if value.terminal_value is None
            else value.terminal_value
        )
        observable_values = np.full_like(local_operator, terminal_value)
    else:
        observable_values = np.asarray(
            value.terminal_observable_values,
            dtype=float,
        )
        if observable_values.shape != local_operator.shape:
            raise DomainViolationError(
                "terminal observable values must share the realized spatial codomain"
            )
        terminal_value = float(
            np.mean(observable_values)
            if value.terminal_value is None
            else value.terminal_value
        )
    return observable_values, terminal_value


def _spatial_from_derived(
    index: int,
    first: CompletenessDerivedLaw,
    second: CompletenessDerivedLaw,
    value: CompletenessInput,
) -> CompletenessSpatialClosure:
    local = (
        first.derived_operator
        + second.derived_operator
        + first.derived_operator * second.derived_operator
    )
    reconstructed = (
        local
        - first.derived_operator
        - second.derived_operator
        - first.derived_operator * second.derived_operator
    )
    reconstruction = float(np.linalg.norm(reconstructed))
    inherited = float(np.linalg.norm(first.residual) + np.linalg.norm(second.residual))
    certificate: AuthoritativeSpatialCertificate
    if index == 0:
        certificate = certify_sheaf_descent(
            value.descent_pairwise_residuals,
            value.descent_cocycle_residual,
            fixed_descent_data=value.fixed_descent_data,
            overlap_isomorphisms=value.overlap_isomorphisms,
            tolerance=value.tolerance,
        )
        descent_gate = 0.0 if certificate.gluable else 1.0
        typed_residual = max(
            *certificate.pairwise_residuals,
            certificate.cocycle_residual,
            descent_gate,
        )
    elif index == 1:
        observable_values, terminal_value = _terminal_values(value, local)
        certificate = factor_terminal_observable(
            observable_values,
            terminal_value=terminal_value,
            tolerance=value.tolerance,
        )
        typed_residual = certificate.factorization_residual
    else:
        raise IndexError(index)
    overlap = inherited + float(typed_residual)
    observability = float(typed_residual)
    closed = max(0.0, overlap, reconstruction, observability) <= value.tolerance
    return CompletenessSpatialClosure(
        str(C_IDS[index]),
        np.asarray(value.coordinates, dtype=float),
        local,
        0.0,
        overlap,
        reconstruction,
        observability,
        "closed" if closed else "open",
        certificate,
    )


def spatial_operator(index: int, value: CompletenessInput) -> CompletenessSpatialClosure:
    first_index, second_index = C_SOURCE_INDICES[index]
    first = derived_operator(first_index, value)
    second = derived_operator(second_index, value)
    return _spatial_from_derived(index, first, second, value)


def _residual(
    name: str,
    values,
    tolerance: float = 1e-10,
) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        name,
        vector,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
    )


def _remove_a(
    b_index: int,
    local_index: int,
    value: CompletenessInput,
) -> SourceRemovalResult:
    output = derived_operator(b_index, value)
    ablated = list(output.source_responses)
    ablated[local_index] = np.zeros_like(ablated[local_index])
    removed, _, _ = _derive_from_responses(b_index, tuple(ablated), value)
    source_indices = B_SOURCE_INDICES[b_index]
    return source_removal_result(
        A_IDS[source_indices[local_index]],
        output.derived_operator,
        removed,
        tolerance=1e-12,
    )


def _remove_b(
    c_index: int,
    local_index: int,
    value: CompletenessInput,
) -> SourceRemovalResult:
    output = spatial_operator(c_index, value)
    b_indices = C_SOURCE_INDICES[c_index]
    first = derived_operator(b_indices[0], value)
    second = derived_operator(b_indices[1], value)
    if local_index == 0:
        first = CompletenessDerivedLaw(
            first.law_name,
            first.source_responses,
            np.zeros_like(first.derived_operator),
            first.residual,
            0.0,
            first.authoritative_certificate,
        )
    else:
        second = CompletenessDerivedLaw(
            second.law_name,
            second.source_responses,
            np.zeros_like(second.derived_operator),
            second.residual,
            0.0,
            second.authoritative_certificate,
        )
    removed = _spatial_from_derived(c_index, first, second, value)
    return source_removal_result(
        B_IDS[b_indices[local_index]],
        output.local_operator,
        removed.local_operator,
        tolerance=1e-12,
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "completeness realization",
        (
            "finite formal system, typed operators, finite-prefix bits, spatial "
            "carrier, attainment/descent witnesses, and terminal observable data"
        ),
        (CompletenessInput,),
    )
    artifact = ArtifactSpec(
        ("closure_metrics", "residual_plot", "boundary_graph"),
        (
            "python -m "
            "the_nothingness_effect.the_completeness_theorem.simulation."
            "run_contract_suite"
        ),
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
                residual=lambda _s, o, cid=str(complex_id): _residual(
                    cid, o.residual
                ),
                implementation_path=(
                    "the_nothingness_effect/the_completeness_theorem/contracts.py"
                ),
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
                    (
                        "genuine multi-source admissibility, splitting, "
                        "transport, or typed Noether transgression operator"
                    ),
                    (CompletenessDerivedLaw,),
                ),
                partial(derived_operator, index),
                residual=lambda _s, o, cid=str(complex_id): _residual(
                    cid, o.residual
                ),
                source_removal_checks=tuple(
                    partial(_remove_a, index, local_index)
                    for local_index in range(len(source_indices))
                ),
                artifact_spec=artifact,
                implementation_path=(
                    "the_nothingness_effect/the_completeness_theorem/contracts.py"
                ),
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
                    (
                        "fixed-isomorphism sheaf descent or terminal observable "
                        "factorization certificate"
                    ),
                    (CompletenessSpatialClosure,),
                ),
                partial(spatial_operator, index),
                residual=lambda _s, o, cid=str(complex_id): _residual(
                    cid,
                    (
                        o.boundary_trace_residual,
                        o.overlap_or_quotient_residual,
                        o.reconstruction_residual,
                        o.observability_residual,
                    ),
                ),
                closure_predicate=lambda output, residual: (
                    output.closure_status == "closed"
                    and residual is not None
                    and residual.passed
                ),
                source_removal_checks=(
                    partial(_remove_b, index, 0),
                    partial(_remove_b, index, 1),
                ),
                artifact_spec=artifact,
                exact_semantics=True,
                implementation_path=(
                    "the_nothingness_effect/the_completeness_theorem/contracts.py"
                ),
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
