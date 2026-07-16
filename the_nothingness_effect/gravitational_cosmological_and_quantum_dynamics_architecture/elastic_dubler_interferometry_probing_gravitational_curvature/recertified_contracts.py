"""Recertified Elastic Dubler Interferometry (EDI) source contracts."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import ContractResult, ContractStatus, scale_aware_tolerance


@dataclass(frozen=True)
class EDIBridgeInput:
    path: np.ndarray
    tension: np.ndarray
    regularity: np.ndarray
    isotopy_certified: bool


@dataclass(frozen=True)
class EDIBridgeResult:
    work_integral: float
    regularity_minimum: float
    path_length: float


def evaluate_bridge_duality_and_2_adic_criterion(value: EDIBridgeInput) -> ContractResult[EDIBridgeResult]:
    path = np.asarray(value.path, dtype=float); tension = np.asarray(value.tension, dtype=float); q = np.asarray(value.regularity, dtype=float)
    if path.ndim != 2 or path.shape[0] < 2 or tension.shape != (path.shape[0],) or q.shape != tension.shape or not all(np.all(np.isfinite(item)) for item in (path, tension, q)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_BRIDGE_DOMAIN")
    if np.any(q <= 0.0):
        return ContractResult(None, ContractStatus.FALSIFIED, "REGULARITY_BREAKDOWN", witnesses={"minimum_q": float(np.min(q))})
    increments = np.linalg.norm(np.diff(path, axis=0), axis=1); work = float(np.sum((tension[:-1] + tension[1:]) * increments / 2.0)); length = float(np.sum(increments))
    status = ContractStatus.NUMERICAL_CANDIDATE if value.isotopy_certified else ContractStatus.UNDECIDED
    return ContractResult(EDIBridgeResult(work, float(np.min(q)), length), status, "FINITE_WORK_WITH_CERTIFIED_ISOTOPY" if value.isotopy_certified else "FINITE_WORK_IS_NOT_TOPOLOGY", {"quadrature_scale": abs(work)}, {"quadrature_scale": scale_aware_tolerance(work)}, {"isotopy_certified": value.isotopy_certified}, {"source_contract": "bridge_duality_and_the_2_adic_criterion"})


@dataclass(frozen=True)
class CurvatureInput:
    potential: np.ndarray
    spacing: float
    regularity_certificate: bool = False
    atomic_mass: float = 0.0


@dataclass(frozen=True)
class CurvatureResult:
    curvature: np.ndarray
    hessian_bound: float
    flux_residual: float


def evaluate_elastic_curvature_smoothness(value: CurvatureInput) -> ContractResult[CurvatureResult]:
    phi = np.asarray(value.potential, dtype=float)
    if phi.ndim != 1 or phi.size < 5 or not np.all(np.isfinite(phi)) or not np.isfinite(value.spacing) or value.spacing <= 0.0 or value.atomic_mass < 0.0:
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_CURVATURE_DOMAIN")
    gradient = np.gradient(phi, value.spacing, edge_order=2); curvature = np.gradient(gradient, value.spacing, edge_order=2)
    bound = float(np.max(np.abs(curvature))); flux = float(abs(gradient[-1] - gradient[0] - np.sum(curvature) * value.spacing))
    if value.atomic_mass > 0.0:
        return ContractResult(CurvatureResult(curvature, bound, flux), ContractStatus.FALSIFIED, "ATOMIC_OR_SINGULAR_CURVATURE", {"flux": flux}, {"flux": scale_aware_tolerance(bound)}, {"atomic_mass": value.atomic_mass})
    status = ContractStatus.NUMERICAL_CANDIDATE if value.regularity_certificate else ContractStatus.UNDECIDED
    return ContractResult(CurvatureResult(curvature, bound, flux), status, "W2INF_REGULARITY_CERTIFIED" if value.regularity_certificate else "WEAK_INTERMEDIATE", {"flux": flux}, {"flux": scale_aware_tolerance(bound)}, provenance={"source_contract": "elastic_curvature_smoothness_curvature_singularity"})


@dataclass(frozen=True)
class EntropicStabilityInput:
    generator: np.ndarray
    observation: np.ndarray
    reconstruction: np.ndarray
    horizon: float


@dataclass(frozen=True)
class EntropicStabilityResult:
    spectral_abscissa: float
    observability_rank: int
    error_bound: float


def evaluate_elastic_entropic_stability(value: EntropicStabilityInput) -> ContractResult[EntropicStabilityResult]:
    g = np.asarray(value.generator, dtype=float); obs = np.asarray(value.observation, dtype=float); rec = np.asarray(value.reconstruction, dtype=float)
    if g.ndim != 2 or g.shape[0] != g.shape[1] or obs.ndim != 2 or obs.shape[1] != g.shape[0] or rec.shape != (g.shape[0], obs.shape[0]) or value.horizon <= 0.0 or not all(np.all(np.isfinite(item)) for item in (g, obs, rec)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_SEMIGROUP_DOMAIN")
    eigen = np.linalg.eigvals(g); abscissa = float(np.max(np.real(eigen))); rank = int(np.linalg.matrix_rank(obs)); reconstruction_residual = float(np.linalg.norm(rec @ obs - np.eye(g.shape[0]))); error = float(np.exp(max(0.0, abscissa) * value.horizon) * reconstruction_residual)
    tol = scale_aware_tolerance(*g.ravel()); observable = rank == g.shape[0]
    if not observable:
        status, reason = ContractStatus.UNDECIDED, "UNOBSERVABLE_MODE"
    elif abscissa > tol:
        status, reason = ContractStatus.FALSIFIED, "OBSERVABLE_POSITIVE_MODE"
    elif abs(abscissa) <= tol:
        status, reason = ContractStatus.UNDECIDED, "MARGINAL_LAMBDA_ZERO"
    else:
        status, reason = ContractStatus.NUMERICAL_CANDIDATE, "ENTROPIC_STABILITY_CANDIDATE"
    return ContractResult(EntropicStabilityResult(abscissa, rank, error), status, reason, {"reconstruction": reconstruction_residual, "spectral_abscissa": abscissa}, {"reconstruction": tol, "spectral_abscissa": tol}, {"observable": observable}, {"source_contract": "elastic_entropic_stability_entropic_instability"})


@dataclass(frozen=True)
class GeometryInput:
    jacobians: np.ndarray
    sampled_outputs: np.ndarray
    sample_pairs: np.ndarray
    global_injectivity_certificate: bool = False


@dataclass(frozen=True)
class GeometryResult:
    minimum_singular_value: float
    collision_distance: float
    local_rank: int


def evaluate_elastic_geometric_consistency(value: GeometryInput) -> ContractResult[GeometryResult]:
    jac = np.asarray(value.jacobians, dtype=float); outputs = np.asarray(value.sampled_outputs, dtype=float); pairs = np.asarray(value.sample_pairs, dtype=int)
    if jac.ndim != 3 or outputs.ndim != 2 or pairs.ndim != 2 or pairs.shape[1] != 2 or not all(np.all(np.isfinite(item)) for item in (jac, outputs)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_GEOMETRY_DOMAIN")
    minimum = float(min(np.min(np.linalg.svd(matrix, compute_uv=False)) for matrix in jac)); rank = int(min(np.linalg.matrix_rank(matrix) for matrix in jac)); distances = [float(np.linalg.norm(outputs[i] - outputs[j])) for i, j in pairs if 0 <= i < len(outputs) and 0 <= j < len(outputs) and i != j]
    collision = min(distances, default=float("inf")); tol = scale_aware_tolerance(*outputs.ravel())
    if rank < min(jac.shape[1:]): status, reason = ContractStatus.FALSIFIED, "FIRST_ORDER_DEGENERATE"
    elif collision <= tol: status, reason = ContractStatus.FALSIFIED, "EXACT_NONINJECTIVE"
    elif value.global_injectivity_certificate: status, reason = ContractStatus.EXACT, "GLOBAL_INJECTIVITY_CERTIFIED"
    else: status, reason = ContractStatus.UNDECIDED, "LOCAL_RANK_IS_NOT_GLOBAL_INJECTIVITY"
    finite_collision = collision if np.isfinite(collision) else 0.0
    return ContractResult(GeometryResult(minimum, finite_collision, rank), status, reason, {"minimum_singular_value": minimum, "collision_distance": finite_collision}, {"minimum_singular_value": tol, "collision_distance": tol}, provenance={"source_contract": "elastic_geometric_consistency_geometric_degeneracy"})


@dataclass(frozen=True)
class EDIMetaResult:
    component_residuals: tuple[float, ...]
    closure_norm: float
    source_necessity: tuple[bool, ...]


def evaluate_edi_cross_complex_closure(component_results: tuple[ContractResult[object], ...], *, weights: tuple[float, ...] | None = None) -> ContractResult[EDIMetaResult]:
    if len(component_results) != 4 or any(item.value is None for item in component_results):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "FOUR_EDI_SOURCES_REQUIRED")
    selected = tuple(float(max(item.residuals.values(), default=0.0)) for item in component_results); metric = np.ones(4) if weights is None else np.asarray(weights, dtype=float)
    if metric.shape != (4,) or np.any(metric <= 0.0) or not np.all(np.isfinite(metric)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "POSITIVE_DEFINITE_WEIGHTS_REQUIRED")
    norm = float(np.sqrt(np.dot(metric, np.square(selected)))); tol = max((max(item.tolerances.values(), default=0.0) for item in component_results), default=0.0)
    necessity = tuple(float(np.sqrt(np.dot(np.delete(metric, i), np.square(np.delete(selected, i))))) != norm for i in range(4))
    if any(item.status is ContractStatus.FALSIFIED for item in component_results): status, reason = ContractStatus.FALSIFIED, "EDI_SOURCE_FALSIFIED"
    elif any(item.status is ContractStatus.UNDECIDED for item in component_results): status, reason = ContractStatus.UNDECIDED, "EDI_SOURCE_UNDECIDED"
    else: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "EDI_POSITIVE_DEFINITE_CLOSURE"
    return ContractResult(EDIMetaResult(selected, norm, necessity), status, reason, {"closure_norm": norm}, {"closure_norm": tol}, {"source_removal": necessity}, {"source_contract": "appendix_wide_edi_cross_complex_closure_and_computational_falsification_interface"})

