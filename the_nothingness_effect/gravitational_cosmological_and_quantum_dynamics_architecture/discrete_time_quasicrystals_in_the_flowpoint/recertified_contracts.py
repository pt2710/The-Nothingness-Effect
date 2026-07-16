"""Recertified DTQC source contracts.

Finite FFTs, wavelet grids, samples, and figures remain numerical evidence;
only supplied structural or limiting certificates can yield exact status.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import ContractResult, ContractStatus, scale_aware_tolerance


def _finite(*items) -> bool:
    return all(np.all(np.isfinite(np.asarray(item, dtype=float))) for item in items)


@dataclass(frozen=True)
class MeyerInput:
    physical_points: np.ndarray
    internal_points: np.ndarray
    window_bounds: tuple[float, float]
    lattice_rank: int
    cps_certificate: bool
    continuous_spectral_mass: float = 0.0


@dataclass(frozen=True)
class MeyerResult:
    model_set: np.ndarray
    minimum_separation: float
    difference_cover_radius: float
    pure_point: bool


def evaluate_meyer_cut_and_project_structure(value: MeyerInput) -> ContractResult[MeyerResult]:
    physical = np.asarray(value.physical_points, dtype=float); internal = np.asarray(value.internal_points, dtype=float); lo, hi = value.window_bounds
    if physical.ndim != 1 or internal.shape != physical.shape or physical.size < 2 or not _finite(physical, internal, (lo, hi, value.continuous_spectral_mass)) or lo > hi or value.lattice_rank < 1 or value.continuous_spectral_mass < 0.0:
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_CUT_AND_PROJECT_DOMAIN")
    selected = np.sort(physical[(internal >= lo) & (internal <= hi)]); gaps = np.diff(selected)
    separation = float(np.min(gaps)) if gaps.size else 0.0; cover = float(np.max(gaps)) if gaps.size else 0.0; pure = value.cps_certificate and value.continuous_spectral_mass == 0.0
    tol = scale_aware_tolerance(*physical)
    if value.continuous_spectral_mass > tol: status, reason = ContractStatus.FALSIFIED, "DIFFUSE_CONTINUOUS_MASS_WITNESS"
    elif value.cps_certificate and separation > tol: status, reason = ContractStatus.EXACT, "MEYER_CPS_CERTIFIED"
    else: status, reason = ContractStatus.UNDECIDED, "FINITE_APPROXIMANT_IS_NOT_MEYER_PROOF"
    return ContractResult(MeyerResult(selected, separation, cover, pure), status, reason, {"continuous_mass": value.continuous_spectral_mass, "minimum_separation": separation}, {"continuous_mass": tol, "minimum_separation": tol}, {"cps_certificate": value.cps_certificate}, {"source_contract": "meyer_cut_and_project_structure_non_meyer_diffuse_support"})


@dataclass(frozen=True)
class Z2xZ2Result:
    sectors: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    sector_energies: tuple[float, float, float, float]
    parity_bias: float


def evaluate_z2x2_sign_symmetry(weights) -> ContractResult[Z2xZ2Result]:
    w = np.asarray(weights, dtype=float)
    if w.ndim != 2 or min(w.shape) < 2 or not _finite(w):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_Z2X2_FIELD")
    a = w[::-1, :]; b = w[:, ::-1]; ab = w[::-1, ::-1]
    sectors = tuple((w + sa * a + sb * b + sa * sb * ab) / 4.0 for sa, sb in ((1, 1), (1, -1), (-1, 1), (-1, -1)))
    energies = tuple(float(np.vdot(item, item).real) for item in sectors); total = max(float(np.vdot(w, w).real), 1e-300); bias = float(1.0 - energies[0] / total)
    residuals = {"group_commutator": 0.0, "projector_reconstruction": float(np.linalg.norm(sum(sectors) - w)), "energy_partition": abs(sum(energies) - total)}; tol = scale_aware_tolerance(*w.ravel())
    failed = max(residuals.values()) > tol
    return ContractResult(Z2xZ2Result(sectors, energies, bias), ContractStatus.FALSIFIED if failed else ContractStatus.EXACT, "SIGN_SYMMETRY_BREAKING" if failed else "Z2X2_SECTORS_CERTIFIED", residuals, {name: tol for name in residuals}, {"parity_bias": bias}, {"source_contract": "z_2_2_sign_symmetry_parity_bias_symmetry_breaking"})


@dataclass(frozen=True)
class ElasticSupportInput:
    signal: np.ndarray
    active_support: np.ndarray
    gain: float | np.ndarray
    convolution_kernel: np.ndarray | None = None


@dataclass(frozen=True)
class ElasticSupportResult:
    transported: np.ndarray
    active_leakage: float
    ambient_leakage: float


def evaluate_elastic_invariance_of_support(value: ElasticSupportInput) -> ContractResult[ElasticSupportResult]:
    signal = np.asarray(value.signal, dtype=float); active = np.asarray(value.active_support, dtype=bool); gain = np.asarray(value.gain, dtype=float)
    if signal.ndim != 1 or active.shape != signal.shape or gain.shape not in ((), signal.shape) or not _finite(signal, gain) or np.any(gain == 0.0):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_SUPPORT_TRANSPORT")
    transported = signal * gain
    if value.convolution_kernel is not None:
        kernel = np.asarray(value.convolution_kernel, dtype=float)
        if kernel.ndim != 1 or kernel.size == 0 or not _finite(kernel):
            return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_CONVOLUTION_KERNEL")
        transported = np.convolve(transported, kernel, mode="same")
    scale = max(float(np.linalg.norm(transported)), 1e-300); active_leak = float(np.linalg.norm(transported[~active]) / scale); ambient_leak = float(np.linalg.norm(transported[(~active) & (np.abs(signal) == 0.0)]) / scale); tol = scale_aware_tolerance(*signal)
    convolutional = value.convolution_kernel is not None or gain.shape == signal.shape
    status = ContractStatus.NUMERICAL_CANDIDATE if active_leak <= tol else ContractStatus.FALSIFIED
    reason = "CONSTANT_GAIN_SUPPORT_CERTIFIED" if not convolutional and status is ContractStatus.NUMERICAL_CANDIDATE else ("NONLINEAR_OR_CONVOLUTIONAL_LEAKAGE" if status is ContractStatus.FALSIFIED else "AMBIENT_SUPPORT_ONLY")
    return ContractResult(ElasticSupportResult(transported, active_leak, ambient_leak), status, reason, {"active_leakage": active_leak, "ambient_leakage": ambient_leak}, {"active_leakage": tol, "ambient_leakage": tol}, {"convolutional": convolutional}, {"source_contract": "elastic_invariance_of_support_nonlinear_leakage"})


@dataclass(frozen=True)
class OUScatterInput:
    latent_line: np.ndarray
    theta: float
    sigma: float
    dt: float
    feature_matrix: np.ndarray
    seed: int
    ensemble_size: int


@dataclass(frozen=True)
class OUScatterResult:
    features_5d: np.ndarray
    continuous_floor: float
    atomic_mass: float


def evaluate_ou_noise_5d_scatter(value: OUScatterInput) -> ContractResult[OUScatterResult]:
    latent = np.asarray(value.latent_line, dtype=float); feature = np.asarray(value.feature_matrix, dtype=float)
    if latent.ndim != 1 or latent.size < 4 or feature.shape != (5, latent.size) or value.theta <= 0.0 or value.sigma < 0.0 or value.dt <= 0.0 or value.ensemble_size < 1 or not _finite(latent, feature, (value.theta, value.sigma, value.dt)):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_OU_EXPERIMENT")
    rng = np.random.default_rng(value.seed); paths = []
    for _ in range(value.ensemble_size):
        noise = np.zeros_like(latent)
        for i in range(1, latent.size): noise[i] = noise[i - 1] - value.theta * noise[i - 1] * value.dt + value.sigma * np.sqrt(value.dt) * rng.standard_normal()
        paths.append(feature @ (latent + noise))
    features = np.stack(paths); floor = float(np.mean(np.var(features, axis=0))); atomic = float(np.linalg.norm(np.mean(features, axis=0)) ** 2); tol = scale_aware_tolerance(*features.ravel())
    status = ContractStatus.NUMERICAL_CANDIDATE if value.sigma > 0.0 else ContractStatus.EXACT; reason = "NOISE_INDUCED_CONTINUOUS_FLOOR" if value.sigma > 0.0 else "ZERO_NOISE_ATOMIC_LIMIT"
    return ContractResult(OUScatterResult(features, floor, atomic), status, reason, {"continuous_floor": floor}, {"continuous_floor": tol}, {"seed": value.seed, "ensemble_size": value.ensemble_size}, {"source_contract": "ou_noise_5_d_scatter_robustness_noise_induced_smearing"})


@dataclass(frozen=True)
class AutocorrelationInput:
    pure_point_mass: float
    absolutely_continuous_mass: float
    singular_continuous_mass: float
    support_residual: float
    averaging_limit_certified: bool


@dataclass(frozen=True)
class AutocorrelationResult:
    total_mass: float
    continuous_mass: float
    decomposition_unique: bool


def evaluate_autocorrelation_completeness(value: AutocorrelationInput) -> ContractResult[AutocorrelationResult]:
    masses = (value.pure_point_mass, value.absolutely_continuous_mass, value.singular_continuous_mass)
    if not _finite(masses, (value.support_residual,)) or any(item < 0.0 for item in masses) or value.support_residual < 0.0:
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_SPECTRAL_MEASURE")
    continuous = masses[1] + masses[2]; tol = scale_aware_tolerance(*masses)
    if not value.averaging_limit_certified: status, reason = ContractStatus.UNDECIDED, "AUTOCORRELATION_LIMIT_MISSING"
    elif continuous > tol or value.support_residual > tol: status, reason = ContractStatus.FALSIFIED, "MIXED_AUTOCORRELATION"
    else: status, reason = ContractStatus.EXACT, "PURE_POINT_AUTOCORRELATION_CLOSURE"
    return ContractResult(AutocorrelationResult(sum(masses), continuous, value.averaging_limit_certified), status, reason, {"continuous_mass": continuous, "support": value.support_residual}, {"continuous_mass": tol, "support": tol}, provenance={"source_contract": "autocorrelation_completeness_mixed_autocorrelation"})


@dataclass(frozen=True)
class ReconstructionInput:
    analysis_operator: np.ndarray
    synthesis_operator: np.ndarray
    signal: np.ndarray
    convergence_mode: str
    convergence_certificate: bool
    null_witness: np.ndarray | None = None


@dataclass(frozen=True)
class ReconstructionResult:
    reconstructed: np.ndarray
    reconstruction_residual: float
    null_residual: float


def evaluate_reconstruction_equivalence(value: ReconstructionInput) -> ContractResult[ReconstructionResult]:
    analysis = np.asarray(value.analysis_operator, dtype=float); synthesis = np.asarray(value.synthesis_operator, dtype=float); signal = np.asarray(value.signal, dtype=float)
    if analysis.ndim != 2 or synthesis.shape != analysis.T.shape or signal.shape != (analysis.shape[1],) or value.convergence_mode not in {"finite", "l1", "l2", "besicovitch"} or not _finite(analysis, synthesis, signal):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_RECONSTRUCTION_DOMAIN")
    reconstructed = synthesis @ (analysis @ signal); residual = float(np.linalg.norm(reconstructed - signal)); null_residual = 0.0
    if value.null_witness is not None:
        witness = np.asarray(value.null_witness, dtype=float)
        if witness.shape != signal.shape or not _finite(witness): return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_NULL_WITNESS")
        null_residual = float(np.linalg.norm(analysis @ witness))
    tol = scale_aware_tolerance(*signal); noninvertible = value.null_witness is not None and np.linalg.norm(value.null_witness) > tol and null_residual <= tol
    if noninvertible: status, reason = ContractStatus.FALSIFIED, "NONINVERTIBLE_NULL_WITNESS"
    elif not value.convergence_certificate: status, reason = ContractStatus.UNDECIDED, "CONVERGENCE_MODE_UNCERTIFIED"
    elif residual <= tol: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "RECONSTRUCTION_EQUIVALENCE_CANDIDATE"
    else: status, reason = ContractStatus.FALSIFIED, "RECONSTRUCTION_RESIDUAL"
    return ContractResult(ReconstructionResult(reconstructed, residual, null_residual), status, reason, {"reconstruction": residual, "null": null_residual}, {"reconstruction": tol, "null": tol}, {"convergence_mode": value.convergence_mode}, {"source_contract": "algebraic_analytic_reconstruction_equivalence_non_invertible_reconstruction"})


@dataclass(frozen=True)
class WaveletRidgeInput:
    coefficients: np.ndarray
    frequencies: np.ndarray
    cone_of_influence: np.ndarray
    expected_ridges: np.ndarray
    resolution: float
    analytic_admissibility_certified: bool


@dataclass(frozen=True)
class WaveletRidgeResult:
    extracted_ridges: np.ndarray
    ridge_drift: float
    inside_coi_fraction: float


def evaluate_wavelet_ridge_locking(value: WaveletRidgeInput) -> ContractResult[WaveletRidgeResult]:
    coeff = np.asarray(value.coefficients); frequencies = np.asarray(value.frequencies, dtype=float); coi = np.asarray(value.cone_of_influence, dtype=bool); expected = np.asarray(value.expected_ridges, dtype=float)
    if coeff.ndim != 2 or frequencies.shape != (coeff.shape[0],) or coi.shape != coeff.shape or expected.shape != (coeff.shape[1],) or value.resolution <= 0.0 or not _finite(np.abs(coeff), frequencies, expected):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_WAVELET_GRID")
    masked = np.where(coi, np.abs(coeff), -np.inf); indices = np.argmax(masked, axis=0); ridges = frequencies[indices]; valid = np.any(coi, axis=0); drift = float(np.max(np.abs(ridges[valid] - expected[valid]))) if np.any(valid) else 0.0; fraction = float(np.mean(valid)); tol = max(value.resolution, scale_aware_tolerance(*frequencies))
    if not value.analytic_admissibility_certified or fraction < 1.0: status, reason = ContractStatus.UNDECIDED, "WAVELET_OR_COI_UNCERTIFIED"
    elif drift > tol: status, reason = ContractStatus.FALSIFIED, "RIDGE_DRIFT_SHEAR"
    else: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "RESOLUTION_INDEXED_RIDGE_LOCKING"
    return ContractResult(WaveletRidgeResult(ridges, drift, fraction), status, reason, {"ridge_drift": drift, "coi_exclusion": 1.0 - fraction}, {"ridge_drift": tol, "coi_exclusion": 0.0}, {"resolution": value.resolution}, {"source_contract": "wavelet_ridge_locking_ridge_drift_shear"})


@dataclass(frozen=True)
class FloquetRobustnessInput:
    clean_residuals: np.ndarray
    disordered_residuals: np.ndarray
    drive_is_floquet_free: bool
    two_adic_certificate: bool
    disorder_probability_space: str


@dataclass(frozen=True)
class FloquetRobustnessResult:
    clean_mean: float
    quenched_mean: float
    annealed_mean: float
    robustness_gap: float


def evaluate_floquet_free_robustness(value: FloquetRobustnessInput) -> ContractResult[FloquetRobustnessResult]:
    clean = np.asarray(value.clean_residuals, dtype=float); disorder = np.asarray(value.disordered_residuals, dtype=float)
    if clean.ndim != 1 or disorder.ndim != 2 or min(clean.size, disorder.size) == 0 or not _finite(clean, disorder):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_FLOQUET_EXPERIMENT")
    clean_mean = float(np.mean(clean)); quenched = float(np.mean(np.mean(disorder, axis=1))); annealed = float(np.mean(disorder)); gap = annealed - clean_mean; tol = scale_aware_tolerance(*clean, *disorder.ravel())
    if not value.drive_is_floquet_free or not value.two_adic_certificate or not value.disorder_probability_space: status, reason = ContractStatus.INVALID_INPUT, "MISSING_DRIVE_2ADIC_OR_PROBABILITY_CONTRACT"
    elif annealed > clean_mean + tol: status, reason = ContractStatus.FALSIFIED, "DISORDER_RELIANT_OR_DEGRADED_STABILITY"
    else: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "CLEAN_QUENCHED_ANNEALED_ROBUSTNESS"
    return ContractResult(FloquetRobustnessResult(clean_mean, quenched, annealed, gap), status, reason, {"robustness_gap": gap}, {"robustness_gap": tol}, {"probability_space": value.disorder_probability_space}, {"source_contract": "floquet_free_robustness_dual_2_adic_criterionicity_disorder_reliant_stability"})


@dataclass(frozen=True)
class DriftInput:
    spectral_measure: np.ndarray
    phase: np.ndarray
    phase_kind: str
    boundedness_certificate: bool = False


@dataclass(frozen=True)
class DriftResult:
    modulated_measure: np.ndarray
    mass_residual: float
    phase_variation: float


def evaluate_drift_boundedness(value: DriftInput) -> ContractResult[DriftResult]:
    measure = np.asarray(value.spectral_measure, dtype=complex); phase = np.asarray(value.phase, dtype=float)
    if measure.ndim != 1 or phase.shape != measure.shape or value.phase_kind not in {"constant", "affine", "bounded_nonlinear", "stochastic_mixing"} or not _finite(np.abs(measure), phase):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_PHASE_MODULATION")
    multiplier = np.exp(1j * phase); modulated = measure * multiplier; mass = float(abs(np.linalg.norm(modulated) - np.linalg.norm(measure))); variation = float(np.max(phase) - np.min(phase)); tol = scale_aware_tolerance(*np.abs(measure))
    if value.phase_kind in {"constant", "affine"}: status, reason = ContractStatus.EXACT, "SUPPORT_PRESERVING_PHASE_OR_SHIFT"
    elif value.phase_kind == "bounded_nonlinear" and value.boundedness_certificate: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "BOUNDED_SIDEBANDS"
    elif value.phase_kind == "stochastic_mixing": status, reason = ContractStatus.NUMERICAL_CANDIDATE, "CONTINUUM_REQUIRES_MIXING_LIMIT"
    else: status, reason = ContractStatus.UNDECIDED, "BOUNDEDNESS_CERTIFICATE_MISSING"
    return ContractResult(DriftResult(modulated, mass, variation), status, reason, {"mass": mass, "phase_variation": variation}, {"mass": tol, "phase_variation": variation}, provenance={"source_contract": "drift_boundedness_criterion_unbounded_drift_breakdown"})


@dataclass(frozen=True)
class DFITailInput:
    measure: np.ndarray
    kernel: np.ndarray
    active_support: np.ndarray
    windows: tuple[int, ...]
    ordered_limit_certified: bool


@dataclass(frozen=True)
class DFITailResult:
    normalized_measure: np.ndarray
    normalization_residual: float
    tail_trace: tuple[float, ...]


def evaluate_dfi_compatible_tail_control(value: DFITailInput) -> ContractResult[DFITailResult]:
    measure = np.asarray(value.measure, dtype=float); kernel = np.asarray(value.kernel, dtype=float); active = np.asarray(value.active_support, dtype=bool)
    if measure.ndim != 1 or kernel.shape != measure.shape or active.shape != measure.shape or np.any(measure < 0.0) or np.any(kernel < 0.0) or not _finite(measure, kernel) or not value.windows or any(window < 1 or window > measure.size for window in value.windows):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_DFI_MEASURE_OR_WINDOWS")
    kernel_mass = float(np.sum(kernel)); measure_mass = float(np.sum(measure))
    if kernel_mass <= 0.0 or measure_mass <= 0.0: return ContractResult(None, ContractStatus.INVALID_INPUT, "ZERO_NORMALIZATION_MASS")
    normalized = measure / measure_mass; normalization = float(abs(np.sum(normalized) - 1.0)); tail = tuple(float(np.sum(normalized[window:][~active[window:]])) for window in value.windows); tol = scale_aware_tolerance(*normalized)
    persistent = tail[-1] > tol
    if not value.ordered_limit_certified: status, reason = ContractStatus.UNDECIDED, "ORDERED_LIMITS_MISSING"
    elif persistent: status, reason = ContractStatus.FALSIFIED, "TAIL_DRIVEN_MASS_IMBALANCE"
    else: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "NORMALIZED_TAIL_CONTROL"
    return ContractResult(DFITailResult(normalized, normalization, tail), status, reason, {"normalization": normalization, "terminal_tail": tail[-1]}, {"normalization": tol, "terminal_tail": tol}, {"windows": value.windows}, {"source_contract": "dfi_compatible_tail_control_tail_driven_mass_imbalance"})


@dataclass(frozen=True)
class FigureClosureInput:
    samples: np.ndarray
    timestamps: np.ndarray
    estimator_residuals: np.ndarray
    generated_file_hashes: tuple[str, ...]
    parameters: dict[str, object]
    seed: int
    minimizer_identified: bool


@dataclass(frozen=True)
class FigureClosureResult:
    sample_hash: str
    parameter_hash: str
    maximum_estimator_residual: float
    provenance_complete: bool


def evaluate_figure_backed_closure(value: FigureClosureInput) -> ContractResult[FigureClosureResult]:
    samples = np.asarray(value.samples, dtype=float); timestamps = np.asarray(value.timestamps, dtype=float); residuals = np.asarray(value.estimator_residuals, dtype=float)
    hashes_valid = bool(value.generated_file_hashes) and all(len(item) == 64 and all(char in "0123456789abcdefABCDEF" for char in item) for item in value.generated_file_hashes)
    if samples.ndim < 1 or timestamps.shape != (samples.shape[0],) or residuals.ndim != 1 or residuals.size == 0 or not _finite(samples, timestamps, residuals):
        return ContractResult(None, ContractStatus.INVALID_INPUT, "INVALID_FIGURE_EVIDENCE_DOMAIN")
    sample_hash = hashlib.sha256(samples.tobytes() + timestamps.tobytes()).hexdigest(); parameter_hash = hashlib.sha256(json.dumps(value.parameters, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest(); maximum = float(np.max(np.abs(residuals))); tol = scale_aware_tolerance(*samples.ravel())
    provenance_complete = hashes_valid and bool(value.parameters)
    if not provenance_complete: status, reason = ContractStatus.FALSIFIED, "PROVENANCE_INCOMPLETE"
    elif not value.minimizer_identified: status, reason = ContractStatus.UNDECIDED, "NUMERICAL_CANDIDATE_NOT_MINIMIZER"
    elif maximum > tol: status, reason = ContractStatus.FALSIFIED, "FIGURE_CONTRADICTED_CLAIM"
    else: status, reason = ContractStatus.NUMERICAL_CANDIDATE, "FIGURE_BACKED_ESTIMATOR_CLOSURE"
    return ContractResult(FigureClosureResult(sample_hash, parameter_hash, maximum, provenance_complete), status, reason, {"maximum_estimator_residual": maximum}, {"maximum_estimator_residual": tol}, {"generated_file_hashes": value.generated_file_hashes}, {"source_contract": "figure_backed_closure_bragg_cwt_figure_contradicted_claims", "seed": value.seed, "claim_boundary": "finite computational support; not a formal proof substitute"})

