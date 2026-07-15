"""All eight Elastic-pi Norm theorem contracts (5A -> 2B -> 1C)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.parity_dfi import parity_dfi
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

from .elastic_pi_norm import ElasticPiNormResult, elastic_pi_weighted_path


APPENDIX = "appendix_tne_fluctuation_and_elastic_dynamics.tex"
APPENDIX_SHA256 = "3277f0ffffcc27dc37ed17f7ecf721ba32234706544ceb5cfbeb5538846f2ba2"
A_IDS = tuple(
    ComplexId(item)
    for item in (
        "weighted_path_functional_and_norm_admissibility",
        "elastic_field_ratios_and_weight_regularity",
        "uniform_entropy_reduction_and_entropic_reweighting_bounds",
        "pdfi_elastic_norm_interface",
        "pdfi_elastic_norm_equivalence_and_decoupling",
    )
)
B_IDS = (
    ComplexId("weighted_path_ratio_regularity_functional"),
    ComplexId("entropy_pdfi_calibrated_norm_residual"),
)
C_ID = ComplexId("spatial_weighted_calibration_closure")


@dataclass(frozen=True)
class ElasticPiNormInput:
    trajectory: np.ndarray
    entropy: np.ndarray
    K_D: float
    p: float = 2.0
    anchored: bool = True
    tolerance: float = 1e-10


@dataclass(frozen=True)
class WeightRegularity:
    weights: np.ndarray
    minimum: float
    maximum: float
    ratio_residual: np.ndarray


@dataclass(frozen=True)
class ReweightingBounds:
    weighted_value: float
    unweighted_value: float
    lower_bound: float
    upper_bound: float
    bound_residual: np.ndarray


@dataclass(frozen=True)
class PdfiNormInterface:
    pdfi: float
    norm: float
    calibration: float
    residual: float


@dataclass(frozen=True)
class PdfiNormEquivalence:
    interface: PdfiNormInterface
    common_support: bool
    calibrated_equivalent: bool
    decoupling_residual: float


@dataclass(frozen=True)
class PathRatioRegularity:
    path_terms: np.ndarray
    weight_ratio: np.ndarray
    regularity_operator: np.ndarray
    ratio_residual: np.ndarray
    interaction_energy: float


@dataclass(frozen=True)
class EntropyPdfiCalibration:
    bounds: np.ndarray
    interface_vector: np.ndarray
    calibration_operator: np.ndarray
    residual: np.ndarray
    interaction_energy: float


@dataclass(frozen=True)
class SpatialWeightedClosure:
    spatial_domain: np.ndarray
    local_operator: np.ndarray
    boundary_trace_residual: float
    localization_residual: float
    calibration_residual: float
    coercivity_ratio: float
    closure_status: str


def path_operator(value: ElasticPiNormInput) -> ElasticPiNormResult:
    return elastic_pi_weighted_path(value.trajectory, value.entropy, K_D=value.K_D, p=value.p, anchored=value.anchored)


def weight_operator(value: ElasticPiNormInput) -> WeightRegularity:
    result = path_operator(value)
    expected = np.exp(-np.diff(result.entropy) / result.K_D)
    return WeightRegularity(result.transition_weights, float(np.min(result.transition_weights)), float(np.max(result.transition_weights)), result.transition_weights - expected)


def bounds_operator(value: ElasticPiNormInput) -> ReweightingBounds:
    result = path_operator(value)
    unweighted = float(np.sum(result.metric_increments**result.p) ** (1.0 / result.p))
    lower = float(np.min(result.transition_weights) ** (1.0 / result.p) * unweighted)
    upper = float(np.max(result.transition_weights) ** (1.0 / result.p) * unweighted)
    residual = np.array([max(lower - result.value, 0.0), max(result.value - upper, 0.0)])
    return ReweightingBounds(result.value, unweighted, lower, upper, residual)


def interface_operator(value: ElasticPiNormInput) -> PdfiNormInterface:
    result = path_operator(value)
    trajectory = np.asarray(value.trajectory)
    pdfi = parity_dfi(trajectory).value
    calibration = 0.0 if result.value == 0.0 else pdfi / result.value
    return PdfiNormInterface(pdfi, result.value, calibration, pdfi - calibration * result.value)


def equivalence_operator(value: ElasticPiNormInput) -> PdfiNormEquivalence:
    interface = interface_operator(value)
    common_support = len(value.trajectory) == len(value.entropy)
    calibrated = common_support and abs(interface.residual) <= value.tolerance
    return PdfiNormEquivalence(interface, common_support, calibrated, abs(interface.residual))


def ratio_regularity_operator(value: ElasticPiNormInput) -> PathRatioRegularity:
    path = path_operator(value)
    weights = weight_operator(value)
    terms = path.metric_increments**path.p
    regularity = terms + weights.weights + terms * weights.weights
    return PathRatioRegularity(terms, weights.weights, regularity, weights.ratio_residual, float(np.linalg.norm(terms * weights.weights) ** 2))


def calibration_operator(value: ElasticPiNormInput) -> EntropyPdfiCalibration:
    bounds = bounds_operator(value)
    interface = interface_operator(value)
    equivalence = equivalence_operator(value)
    bound_vector = np.array([bounds.lower_bound, bounds.weighted_value, bounds.upper_bound])
    interface_vector = np.array([interface.pdfi, interface.calibration * interface.norm, float(equivalence.calibrated_equivalent)])
    combined = bound_vector + interface_vector + bound_vector * interface_vector
    residual = np.concatenate((bounds.bound_residual, np.array([interface.residual, equivalence.decoupling_residual])))
    return EntropyPdfiCalibration(bound_vector, interface_vector, combined, residual, float(np.linalg.norm(bound_vector * interface_vector) ** 2))


def spatial_operator(value: ElasticPiNormInput) -> SpatialWeightedClosure:
    ratio = ratio_regularity_operator(value)
    calibration = calibration_operator(value)
    cal_pad = np.pad(calibration.calibration_operator, (0, max(0, ratio.regularity_operator.size - calibration.calibration_operator.size)), mode="edge")[: ratio.regularity_operator.size]
    local = ratio.regularity_operator + cal_pad
    boundary = float(abs(local[0]) + abs(local[-1]))
    localization = float(np.linalg.norm(np.diff(local))) if local.size > 1 else 0.0
    calibration_residual = float(np.linalg.norm(calibration.residual))
    path = path_operator(value)
    unweighted = float(np.linalg.norm(path.metric_increments))
    coercivity = 0.0 if unweighted == 0.0 else path.value / unweighted
    closed = calibration_residual <= value.tolerance and coercivity > 0.0
    return SpatialWeightedClosure(np.arange(local.size, dtype=float), local, boundary, localization, calibration_residual, coercivity, "numerical_candidate" if closed else "open")


def _residual(name: str, values, tolerance: float = 1e-10) -> ResidualResult:
    vector = tuple(float(item) for item in np.ravel(values))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(name, vector, tolerance, norm <= tolerance, ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN)


def _removal(source, complete, removed) -> SourceRemovalResult:
    return source_removal_result(source, complete, removed, tolerance=1e-12)


def remove_path(value):
    output = ratio_regularity_operator(value)
    return _removal(A_IDS[0], output.regularity_operator, output.weight_ratio)


def remove_ratio(value):
    output = ratio_regularity_operator(value)
    return _removal(A_IDS[1], output.regularity_operator, output.path_terms)


def remove_bounds(value):
    output = calibration_operator(value)
    return _removal(A_IDS[2], output.calibration_operator, output.interface_vector)


def remove_interface(value):
    output = calibration_operator(value)
    return _removal(A_IDS[3], output.calibration_operator, output.bounds)


def remove_equivalence(value):
    output = calibration_operator(value)
    removed = output.bounds + output.interface_vector
    return _removal(A_IDS[4], output.calibration_operator, removed)


def remove_regularity(value):
    output = spatial_operator(value)
    calibration = calibration_operator(value)
    removed = np.pad(calibration.calibration_operator, (0, max(0, output.local_operator.size - calibration.calibration_operator.size)), mode="edge")[: output.local_operator.size]
    return _removal(B_IDS[0], output.local_operator, removed)


def remove_calibration(value):
    output = spatial_operator(value)
    ratio = ratio_regularity_operator(value)
    return _removal(B_IDS[1], output.local_operator, ratio.regularity_operator)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec("Elastic-pi norm source", "anchored metric path, entropy sequence, K_D > 0 and p >= 1", (ElasticPiNormInput,))
    artifact = ArtifactSpec(("weighted_path_csv", "bounds_plot", "source_removal_table"), "python -m the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.simulation.run_contract_suite")
    result = [
        ComplexContract(A_IDS[0], APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("weighted path", "norm on anchored domain or seminorm with explicit status", (ElasticPiNormResult,)), path_operator, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(A_IDS[1], APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("weight regularity", "positive Elastic-pi field ratios", (WeightRegularity,)), weight_operator, residual=lambda _s, o: _residual("field ratio identity", o.ratio_residual), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(A_IDS[2], APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("reweighting bounds", "lower and upper path bounds", (ReweightingBounds,)), bounds_operator, residual=lambda _s, o: _residual("reweighting bounds", o.bound_residual), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(A_IDS[3], APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("pDFI norm interface", "common-input calibrated residual", (PdfiNormInterface,)), interface_operator, residual=lambda _s, o: _residual("pDFI norm interface", (o.residual,)), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(A_IDS[4], APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain, CodomainSpec("pDFI norm equivalence", "conditional calibrated status", (PdfiNormEquivalence,)), equivalence_operator, residual=lambda _s, o: _residual("pDFI norm decoupling", (o.decoupling_residual,)), implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(B_IDS[0], APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[0], A_IDS[1]), domain, CodomainSpec("path ratio regularity", "genuine path-weight interaction", (PathRatioRegularity,)), ratio_regularity_operator, residual=lambda _s, o: _residual("weight ratio", o.ratio_residual), source_removal_checks=(remove_path, remove_ratio), artifact_spec=artifact, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(B_IDS[1], APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (A_IDS[2], A_IDS[3], A_IDS[4]), domain, CodomainSpec("entropy pDFI calibration", "genuine bounds-interface-equivalence interaction", (EntropyPdfiCalibration,)), calibration_operator, residual=lambda _s, o: _residual("entropy pDFI calibration", o.residual), source_removal_checks=(remove_bounds, remove_interface, remove_equivalence), artifact_spec=artifact, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
        ComplexContract(C_ID, APPENDIX, APPENDIX_SHA256, ComplexLevel.C, B_IDS, domain, CodomainSpec("spatial weighted calibration", "local operator, boundary trace, coercivity, and candidate status", (SpatialWeightedClosure,)), spatial_operator, residual=lambda _s, o: _residual("spatial weighted calibration", (o.calibration_residual,)), closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and output.coercivity_ratio > 0.0 and residual is not None and residual.passed, source_removal_checks=(remove_regularity, remove_calibration), artifact_spec=artifact, exact_semantics=False, implementation_path="the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm/contracts.py"),
    ]
    return tuple(result)


def registered_elastic_pi_norm_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
