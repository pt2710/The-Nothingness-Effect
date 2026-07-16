"""All seven Elastic-pi theorem-complex contracts (4A -> 2B -> 1C)."""

from __future__ import annotations

from dataclasses import dataclass
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
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import source_removal_result

from .elastic_pi import ElasticPiEvaluation, evaluate_elastic_pi, require_elastic_pi_value


APPENDIX = "appendix_tne_fluctuation_and_elastic_dynamics.tex"
APPENDIX_SHA256 = "63e5684e4c4bb016a2cc62d46574c2174fbe14eb5f50c16db825ca33b0836389"

A1 = ComplexId("dfi_elastic_equivalence_and_breakdown")
A2 = ComplexId("elastic_e_curvature_encoding_and_curvature_ambiguity_divergence")
A3 = ComplexId("elastic_curvature_entropy_duality_and_decoupling")
A4 = ComplexId("elastic_simulation_consistency_and_simulation_breakdown_non_equivalence")
B1 = ComplexId("dfi_log_curvature_reciprocity_law")
B2 = ComplexId("curvature_certified_simulation_residual")
C1 = ComplexId("spatial_reciprocal_curvature_validation_closure")


@dataclass(frozen=True)
class ElasticPiInput:
    entropy: np.ndarray
    K_D: float
    coordinates: np.ndarray | None = None
    tolerance: float = 1e-10


@dataclass(frozen=True)
class ElasticPiReciprocity:
    evaluation: ElasticPiEvaluation
    dfi_response: np.ndarray
    reciprocal_residual: np.ndarray
    cayley_variable: np.ndarray


@dataclass(frozen=True)
class CurvatureEncoding:
    evaluation: ElasticPiEvaluation
    curvature_proxy: np.ndarray
    entropy_curvature: np.ndarray
    curvature_identity_residual: np.ndarray


@dataclass(frozen=True)
class CurvatureEntropyDuality:
    forward_curvature: np.ndarray
    reconstructed_entropy: np.ndarray
    reconstruction_residual: np.ndarray
    boundary_anchor: tuple[float, float]


@dataclass(frozen=True)
class ElasticSimulationCertification:
    evaluation: ElasticPiEvaluation
    independent_value: np.ndarray
    value_residual: np.ndarray
    log_residual: np.ndarray


@dataclass(frozen=True)
class DfiCurvatureReciprocity:
    dfi_log_response: np.ndarray
    curvature_proxy: np.ndarray
    coupled_operator: np.ndarray
    reciprocity_residual: np.ndarray
    interaction_energy: float


@dataclass(frozen=True)
class CurvatureCertifiedSimulation:
    reconstructed_entropy: np.ndarray
    curvature_proxy: np.ndarray
    simulation_response: np.ndarray
    certification_operator: np.ndarray
    reconstruction_residual: np.ndarray
    simulation_residual: np.ndarray


@dataclass(frozen=True)
class SpatialElasticClosure:
    spatial_domain: np.ndarray
    local_operator: np.ndarray
    boundary_trace_residual: float
    reciprocity_residual: float
    certification_residual: float
    closure_status: str


def _laplacian(values: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    result = np.zeros_like(values)
    if values.size > 2:
        spacing = float(np.mean(np.diff(coordinates)))
        result[1:-1] = (values[2:] - 2.0 * values[1:-1] + values[:-2]) / spacing**2
    return result


def reciprocity_operator(value: ElasticPiInput) -> ElasticPiReciprocity:
    evaluation = evaluate_elastic_pi(value.entropy, K_D=value.K_D, x=value.coordinates)
    elastic = require_elastic_pi_value(evaluation)
    dfi_response = np.exp(np.asarray(value.entropy, dtype=float) / value.K_D)
    residual = elastic * dfi_response - np.pi
    cayley = np.tanh(np.asarray(value.entropy, dtype=float) / (2.0 * value.K_D))
    return ElasticPiReciprocity(evaluation, dfi_response, residual, cayley)


def curvature_operator(value: ElasticPiInput) -> CurvatureEncoding:
    evaluation = evaluate_elastic_pi(value.entropy, K_D=value.K_D, x=value.coordinates)
    coordinates = evaluation.coordinates
    entropy_curvature = -_laplacian(np.asarray(value.entropy, dtype=float) / value.K_D, coordinates)
    residual = evaluation.log_laplacian - entropy_curvature
    return CurvatureEncoding(evaluation, evaluation.log_laplacian, entropy_curvature, residual)


def duality_operator(value: ElasticPiInput) -> CurvatureEntropyDuality:
    evaluation = evaluate_elastic_pi(value.entropy, K_D=value.K_D, x=value.coordinates)
    elastic = require_elastic_pi_value(evaluation)
    reconstructed = -value.K_D * np.log(elastic / np.pi)
    residual = reconstructed - np.asarray(value.entropy, dtype=float)
    return CurvatureEntropyDuality(
        evaluation.log_laplacian,
        reconstructed,
        residual,
        (float(reconstructed[0]), float(reconstructed[-1])),
    )


def simulation_operator(value: ElasticPiInput) -> ElasticSimulationCertification:
    evaluation = evaluate_elastic_pi(value.entropy, K_D=value.K_D, x=value.coordinates)
    elastic = require_elastic_pi_value(evaluation)
    independent = np.pi / np.exp(np.asarray(value.entropy, dtype=float) / value.K_D)
    value_residual = elastic - independent
    log_residual = np.log(elastic) - evaluation.analytic_log_value
    return ElasticSimulationCertification(evaluation, independent, value_residual, log_residual)


def dfi_curvature_operator(value: ElasticPiInput) -> DfiCurvatureReciprocity:
    reciprocal = reciprocity_operator(value)
    curvature = curvature_operator(value)
    dfi_log = np.log(reciprocal.dfi_response)
    # The derivative coupling is a new two-source operator, not a carrier.
    coupled = curvature.curvature_proxy + dfi_log + curvature.curvature_proxy * dfi_log
    energy = float(np.linalg.norm(curvature.curvature_proxy * dfi_log) ** 2)
    return DfiCurvatureReciprocity(
        dfi_log,
        curvature.curvature_proxy,
        coupled,
        reciprocal.reciprocal_residual,
        energy,
    )


def certified_simulation_operator(value: ElasticPiInput) -> CurvatureCertifiedSimulation:
    duality = duality_operator(value)
    simulation = simulation_operator(value)
    simulation_residual = simulation.value_residual + simulation.log_residual
    simulation_response = simulation.independent_value / np.pi
    certification = (
        duality.forward_curvature
        + simulation_response
        + duality.forward_curvature * simulation_response
    )
    return CurvatureCertifiedSimulation(
        duality.reconstructed_entropy,
        duality.forward_curvature,
        simulation_response,
        certification,
        duality.reconstruction_residual,
        simulation_residual,
    )


def spatial_operator(value: ElasticPiInput) -> SpatialElasticClosure:
    reciprocity = dfi_curvature_operator(value)
    certification = certified_simulation_operator(value)
    coordinates = reciprocity.dfi_log_response * 0.0 + np.arange(reciprocity.dfi_log_response.size)
    local = reciprocity.coupled_operator + certification.certification_operator
    boundary = float(abs(local[0]) + abs(local[-1]))
    reciprocity_residual = float(np.linalg.norm(reciprocity.reciprocity_residual))
    certification_residual = float(
        np.linalg.norm(certification.reconstruction_residual)
        + np.linalg.norm(certification.simulation_residual)
    )
    closed = max(reciprocity_residual, certification_residual) <= value.tolerance
    return SpatialElasticClosure(
        coordinates,
        local,
        boundary,
        reciprocity_residual,
        certification_residual,
        "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values: np.ndarray | tuple[float, ...], tolerance: float = 1e-10) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        name,
        vector,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
    )


def _removal(source: ComplexId, complete: np.ndarray, removed: np.ndarray) -> SourceRemovalResult:
    return source_removal_result(source, complete, removed, tolerance=1e-12)


def remove_dfi(value: ElasticPiInput) -> SourceRemovalResult:
    output = dfi_curvature_operator(value)
    return _removal(A1, output.coupled_operator, output.curvature_proxy)


def remove_curvature(value: ElasticPiInput) -> SourceRemovalResult:
    output = dfi_curvature_operator(value)
    return _removal(A2, output.coupled_operator, output.dfi_log_response)


def remove_duality(value: ElasticPiInput) -> SourceRemovalResult:
    output = certified_simulation_operator(value)
    return _removal(A3, output.certification_operator, output.simulation_response)


def remove_simulation(value: ElasticPiInput) -> SourceRemovalResult:
    output = certified_simulation_operator(value)
    return _removal(A4, output.certification_operator, output.curvature_proxy)


def remove_reciprocity_law(value: ElasticPiInput) -> SourceRemovalResult:
    output = spatial_operator(value)
    certification = certified_simulation_operator(value)
    return _removal(B1, output.local_operator, certification.certification_operator)


def remove_certification_law(value: ElasticPiInput) -> SourceRemovalResult:
    output = spatial_operator(value)
    reciprocity = dfi_curvature_operator(value)
    return _removal(B2, output.local_operator, reciprocity.coupled_operator)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "Elastic-pi source",
        "finite one-dimensional entropy field, K_D > 0, and declared coordinates",
        (ElasticPiInput,),
    )
    artifact = ArtifactSpec(
        ("field_csv", "residual_plot", "source_removal_table"),
        "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.simulation.run_contract_suite",
    )
    contracts_: list[ComplexContract] = [
        ComplexContract(A1, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("reciprocal Elastic-pi field", "positive field with DFI reciprocity residual", (ElasticPiReciprocity,)), reciprocity_operator, residual=lambda _s, o: _residual("Elastic-pi reciprocal identity", o.reciprocal_residual), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
        ComplexContract(A2, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("curvature encoding", "log-Laplacian proxy and entropy identity", (CurvatureEncoding,)), curvature_operator, residual=lambda _s, o: _residual("log-curvature identity", o.curvature_identity_residual), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
        ComplexContract(A3, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("curvature-entropy duality", "forward proxy and entropy reconstruction", (CurvatureEntropyDuality,)), duality_operator, residual=lambda _s, o: _residual("entropy reconstruction", o.reconstruction_residual), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
        ComplexContract(A4, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("simulation certification", "independent evaluation and diagnostics", (ElasticSimulationCertification,)), simulation_operator, residual=lambda _s, o: _residual("Elastic-pi simulation", np.concatenate((o.value_residual, o.log_residual))), artifact_spec=artifact, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
        ComplexContract(B1, APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A1, A2), domain, CodomainSpec("DFI-log-curvature reciprocity", "coupled two-source operator", (DfiCurvatureReciprocity,)), dfi_curvature_operator, residual=lambda _s, o: _residual("DFI reciprocal residual", o.reciprocity_residual), source_removal_checks=(remove_dfi, remove_curvature), artifact_spec=artifact, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
        ComplexContract(B2, APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A3, A4), domain, CodomainSpec("curvature-certified simulation", "reconstruction and simulation coupling", (CurvatureCertifiedSimulation,)), certified_simulation_operator, residual=lambda _s, o: _residual("curvature certification", np.concatenate((o.reconstruction_residual, o.simulation_residual))), source_removal_checks=(remove_duality, remove_simulation), artifact_spec=artifact, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
        ComplexContract(C1, APPENDIX, APPENDIX_SHA256, ComplexLevel.C, (B1, B2), domain, CodomainSpec("spatial reciprocal curvature closure", "local operator, boundary trace, and explicit candidate status", (SpatialElasticClosure,)), spatial_operator, residual=lambda _s, o: _residual("spatial reciprocal closure", (o.reciprocity_residual, o.certification_residual)), closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and residual is not None and residual.passed, source_removal_checks=(remove_reciprocity_law, remove_certification_law), artifact_spec=artifact, exact_semantics=False, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi/contracts.py"),
    ]
    return tuple(contracts_)


def registered_elastic_pi_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
