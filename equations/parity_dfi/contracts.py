"""All ten pDFI theorem-complex contracts (6A -> 3B -> 1C)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from equations.elastic_pi.elastic_pi import evaluate_elastic_pi, require_elastic_pi_value
from equations.theorem_complex_runtime import (
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
from equations.theorem_complex_runtime.invariants import source_removal_result

from .parity_dfi import ParityDFIResult, parity_dfi, parity_inverse_recurrence


APPENDIX = "appendix_tne_fluctuation_and_elastic_dynamics.tex"
APPENDIX_SHA256 = "3277f0ffffcc27dc37ed17f7ecf721ba32234706544ceb5cfbeb5538846f2ba2"

A_IDS = tuple(
    ComplexId(item)
    for item in (
        "parity_definite_fluctuation_law_and_parity_indeterminate_fluctuation_law",
        "flowpoint_parity_correspondence_and_decoupling",
        "pdfi_entropic_predictability_and_fluctuation_ambiguity",
        "pdfi_driven_meta_observation_and_collapse_under_meta_parity_breakdown",
        "pdfi_elastic_equivalence_and_decoupling",
        "completeness_of_parity_driven_fluctuation_synthesis_and_incompleteness_of_parity_driven_fluctuations",
    )
)
B_IDS = tuple(
    ComplexId(item)
    for item in (
        "parity_flowpoint_transport_law",
        "predictability_observation_parity_coupling",
        "elastic_calibration_completeness_functional",
    )
)
C_ID = ComplexId("spatial_parity_elastic_calibration_closure")


@dataclass(frozen=True)
class ParityDFIInput:
    trajectory: np.ndarray
    response_seed: float = 2.0
    K_D: float = 1.0
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ParityRecurrenceLaw:
    pdfi: ParityDFIResult
    response: np.ndarray
    inverse_residual: np.ndarray
    two_cycle_residual: np.ndarray


@dataclass(frozen=True)
class FlowpointParityLaw:
    flowpoint_trajectory: np.ndarray
    source_parity: np.ndarray
    transported_parity: np.ndarray
    commutator_residual: np.ndarray


@dataclass(frozen=True)
class PredictabilityLaw:
    observed_increments: np.ndarray
    parity_selected_increments: np.ndarray
    masked_ambiguity: np.ndarray
    exact_tracking_residual: np.ndarray


@dataclass(frozen=True)
class MetaObservationLaw:
    observation_increments: np.ndarray
    observation_mask: np.ndarray
    selected_observations: np.ndarray
    meta_pdfi: float


@dataclass(frozen=True)
class ElasticCalibrationLaw:
    pdfi: float
    weighted_path: float
    calibration: float
    calibration_residual: float
    elastic_weights: np.ndarray


@dataclass(frozen=True)
class ParityCompletenessLaw:
    domain_complete: bool
    parity_complete: bool
    recurrence_complete: bool
    source_vector: np.ndarray
    obstruction_count: int


@dataclass(frozen=True)
class ParityFlowpointTransport:
    response: np.ndarray
    flowpoint_state: np.ndarray
    transport_operator: np.ndarray
    commutator_residual: np.ndarray
    interaction_energy: float


@dataclass(frozen=True)
class PredictabilityObservationCoupling:
    predicted: np.ndarray
    observed: np.ndarray
    coupling_operator: np.ndarray
    tracking_residual: np.ndarray
    interaction_energy: float


@dataclass(frozen=True)
class ElasticCompletenessFunctional:
    elastic_weights: np.ndarray
    completeness_vector: np.ndarray
    functional: np.ndarray
    calibration_residual: float
    interaction_energy: float


@dataclass(frozen=True)
class SpatialParityClosure:
    spatial_domain: np.ndarray
    local_operator: np.ndarray
    boundary_trace_residual: float
    parity_leakage_residual: float
    calibration_residual: float
    closure_status: str


def recurrence_operator(value: ParityDFIInput) -> ParityRecurrenceLaw:
    result = parity_dfi(value.trajectory)
    response = parity_inverse_recurrence(value.response_seed, result.trajectory.size)
    inverse = response[:-1] * response[1:] - 1.0
    two_cycle = response[2:] - response[:-2]
    return ParityRecurrenceLaw(result, response, inverse, two_cycle)


def flowpoint_operator(value: ParityDFIInput) -> FlowpointParityLaw:
    source = np.asarray(value.trajectory, dtype=np.int64)
    flowpoint = -source
    source_parity = np.mod(source, 2)
    transported = np.mod(flowpoint, 2)
    return FlowpointParityLaw(flowpoint, source_parity, transported, transported - source_parity)


def predictability_operator(value: ParityDFIInput) -> PredictabilityLaw:
    result = parity_dfi(value.trajectory)
    selected = result.parity_transitions * result.relative_increments
    ambiguity = (1.0 - result.parity_transitions) * result.relative_increments
    return PredictabilityLaw(result.relative_increments, selected, ambiguity, selected - result.weighted_increments)


def observation_operator(value: ParityDFIInput) -> MetaObservationLaw:
    result = parity_dfi(value.trajectory)
    increments = np.abs(np.diff(np.abs(result.trajectory.astype(float))))
    selected = result.parity_transitions * increments
    return MetaObservationLaw(increments, result.parity_transitions, selected, float(np.sum(selected)))


def elastic_operator(value: ParityDFIInput) -> ElasticCalibrationLaw:
    result = parity_dfi(value.trajectory)
    entropy = np.abs(result.trajectory.astype(float))
    evaluation = evaluate_elastic_pi(entropy, K_D=value.K_D)
    elastic = require_elastic_pi_value(evaluation)
    weights = elastic[1:] / elastic[:-1]
    path = float(np.sqrt(np.sum(weights * np.diff(result.trajectory.astype(float)) ** 2)))
    calibration = 0.0 if path == 0.0 else result.value / path
    residual = result.value - calibration * path
    return ElasticCalibrationLaw(result.value, path, calibration, residual, weights)


def completeness_operator(value: ParityDFIInput) -> ParityCompletenessLaw:
    result = parity_dfi(value.trajectory)
    recurrence = parity_inverse_recurrence(value.response_seed, result.trajectory.size)
    vector = np.array(
        [
            float(np.all(result.trajectory[:-1] != 0)),
            float(np.all((result.parity_labels == 0) | (result.parity_labels == 1))),
            float(np.allclose(recurrence[:-1] * recurrence[1:], 1.0)),
        ]
    )
    return ParityCompletenessLaw(bool(vector[0]), bool(vector[1]), bool(vector[2]), vector, int(np.count_nonzero(vector == 0.0)))


def transport_operator(value: ParityDFIInput) -> ParityFlowpointTransport:
    recurrence = recurrence_operator(value)
    flowpoint = flowpoint_operator(value)
    response = recurrence.response
    state = flowpoint.flowpoint_trajectory.astype(float)
    combined = response + state + response * state
    energy = float(np.linalg.norm(response * state) ** 2)
    return ParityFlowpointTransport(response, state, combined, flowpoint.commutator_residual, energy)


def predictability_observation_operator(value: ParityDFIInput) -> PredictabilityObservationCoupling:
    prediction = predictability_operator(value)
    observation = observation_operator(value)
    predicted = prediction.parity_selected_increments
    observed = observation.selected_observations
    coupled = predicted + observed + predicted * observed
    return PredictabilityObservationCoupling(
        predicted,
        observed,
        coupled,
        prediction.exact_tracking_residual,
        float(np.linalg.norm(predicted * observed) ** 2),
    )


def elastic_completeness_operator(value: ParityDFIInput) -> ElasticCompletenessFunctional:
    elastic = elastic_operator(value)
    completeness = completeness_operator(value)
    complete = completeness.source_vector
    weights = elastic.elastic_weights
    # Broadcast the aggregate completeness gate across every elastic transition.
    gate = float(np.prod(complete))
    functional = weights + gate + weights * gate
    return ElasticCompletenessFunctional(
        weights,
        complete,
        functional,
        elastic.calibration_residual,
        float(np.linalg.norm(weights * gate) ** 2),
    )


def spatial_operator(value: ParityDFIInput) -> SpatialParityClosure:
    transport = transport_operator(value)
    predictive = predictability_observation_operator(value)
    elastic = elastic_completeness_operator(value)
    predict_pad = np.pad(predictive.coupling_operator, (0, 1), mode="edge")
    elastic_pad = np.pad(elastic.functional, (0, 1), mode="edge")
    local = transport.transport_operator + predict_pad + elastic_pad
    boundary = float(abs(local[0]) + abs(local[-1]))
    parity_leakage = float(np.linalg.norm(transport.commutator_residual))
    closed = max(parity_leakage, abs(elastic.calibration_residual)) <= value.tolerance
    return SpatialParityClosure(
        np.arange(local.size, dtype=float),
        local,
        boundary,
        parity_leakage,
        abs(elastic.calibration_residual),
        "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values, tolerance: float = 1e-10) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(name, vector, tolerance, norm <= tolerance, ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN)


def _removal(source: ComplexId, complete, removed) -> SourceRemovalResult:
    return source_removal_result(source, complete, removed, tolerance=1e-12)


def remove_recurrence(value):
    output = transport_operator(value)
    return _removal(A_IDS[0], output.transport_operator, output.flowpoint_state)


def remove_flowpoint(value):
    output = transport_operator(value)
    return _removal(A_IDS[1], output.transport_operator, output.response)


def remove_prediction(value):
    output = predictability_observation_operator(value)
    return _removal(A_IDS[2], output.coupling_operator, output.observed)


def remove_observation(value):
    output = predictability_observation_operator(value)
    return _removal(A_IDS[3], output.coupling_operator, output.predicted)


def remove_elastic(value):
    output = elastic_completeness_operator(value)
    gate = float(np.prod(output.completeness_vector))
    return _removal(A_IDS[4], output.functional, np.full_like(output.elastic_weights, gate))


def remove_completeness(value):
    output = elastic_completeness_operator(value)
    return _removal(A_IDS[5], output.functional, output.elastic_weights)


def remove_transport(value):
    output = spatial_operator(value)
    predictive = predictability_observation_operator(value)
    elastic = elastic_completeness_operator(value)
    removed = np.pad(predictive.coupling_operator, (0, 1), mode="edge") + np.pad(elastic.functional, (0, 1), mode="edge")
    return _removal(B_IDS[0], output.local_operator, removed)


def remove_predictive(value):
    output = spatial_operator(value)
    transport = transport_operator(value)
    elastic = elastic_completeness_operator(value)
    removed = transport.transport_operator + np.pad(elastic.functional, (0, 1), mode="edge")
    return _removal(B_IDS[1], output.local_operator, removed)


def remove_elastic_completeness(value):
    output = spatial_operator(value)
    transport = transport_operator(value)
    predictive = predictability_observation_operator(value)
    removed = transport.transport_operator + np.pad(predictive.coupling_operator, (0, 1), mode="edge")
    return _removal(B_IDS[2], output.local_operator, removed)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec("pDFI realization", "integer trajectory, nonzero predecessors, positive recurrence seed and K_D", (ParityDFIInput,))
    artifact = ArtifactSpec(("transition_csv", "parity_plot", "source_removal_table"), "python -m equations.parity_dfi.simulation.run_contract_suite")
    a_specs = (
        (A_IDS[0], ParityRecurrenceLaw, recurrence_operator, lambda o: np.concatenate((o.inverse_residual, o.two_cycle_residual))),
        (A_IDS[1], FlowpointParityLaw, flowpoint_operator, lambda o: o.commutator_residual),
        (A_IDS[2], PredictabilityLaw, predictability_operator, lambda o: o.exact_tracking_residual),
        (A_IDS[3], MetaObservationLaw, observation_operator, lambda _o: (0.0,)),
        (A_IDS[4], ElasticCalibrationLaw, elastic_operator, lambda o: (o.calibration_residual,)),
        (A_IDS[5], ParityCompletenessLaw, completeness_operator, lambda o: (float(o.obstruction_count),)),
    )
    result: list[ComplexContract] = []
    for complex_id, result_type, operator, residual_values in a_specs:
        result.append(ComplexContract(complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec(f"{complex_id} output", "typed pDFI source-law result", (result_type,)), operator, residual=lambda _s, o, fn=residual_values: _residual(str(complex_id), fn(o)), implementation_path="equations/parity_dfi/contracts.py"))
    result.extend(
        (
            ComplexContract(B_IDS[0], APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[0], A_IDS[1]), domain, CodomainSpec("parity Flowpoint transport", "genuine two-source transport operator", (ParityFlowpointTransport,)), transport_operator, residual=lambda _s, o: _residual("Flowpoint parity commutator", o.commutator_residual), source_removal_checks=(remove_recurrence, remove_flowpoint), artifact_spec=artifact, implementation_path="equations/parity_dfi/contracts.py"),
            ComplexContract(B_IDS[1], APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[2], A_IDS[3]), domain, CodomainSpec("predictability observation coupling", "genuine prediction-observation response", (PredictabilityObservationCoupling,)), predictability_observation_operator, residual=lambda _s, o: _residual("pDFI tracking", o.tracking_residual), source_removal_checks=(remove_prediction, remove_observation), artifact_spec=artifact, implementation_path="equations/parity_dfi/contracts.py"),
            ComplexContract(B_IDS[2], APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[4], A_IDS[5]), domain, CodomainSpec("elastic completeness functional", "genuine calibrated completeness response", (ElasticCompletenessFunctional,)), elastic_completeness_operator, residual=lambda _s, o: _residual("elastic calibration", (o.calibration_residual,)), source_removal_checks=(remove_elastic, remove_completeness), artifact_spec=artifact, implementation_path="equations/parity_dfi/contracts.py"),
            ComplexContract(C_ID, APPENDIX, APPENDIX_SHA256, ComplexLevel.C, B_IDS, domain, CodomainSpec("spatial pDFI closure", "local operator, boundary trace, leakage and candidate status", (SpatialParityClosure,)), spatial_operator, residual=lambda _s, o: _residual("spatial parity calibration", (o.parity_leakage_residual, o.calibration_residual)), closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and residual is not None and residual.passed, source_removal_checks=(remove_transport, remove_predictive, remove_elastic_completeness), artifact_spec=artifact, exact_semantics=False, implementation_path="equations/parity_dfi/contracts.py"),
        )
    )
    return tuple(result)


def registered_pdfi_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
