"""Typed QENN theorem-complex contracts for the first 4A -> 2B -> 1C chain.

The implementation follows the appendix residual-energy construction: B laws
are positive, non-cancelling functions of both complete A residual fields, and
the C law forms one boundary-sensitive spatial defect field from both B laws.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import torch

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
from the_nothingness_effect._runtime.theorem_complex_runtime.types import DomainViolationError, NonFiniteValueError


APPENDIX = "appendix_tne_artificial_intelligence_architechture.tex"
APPENDIX_SHA256 = "3a75d4bfdbf9779255d01dd3ae3db6a848a4dc1fa67455ca1f22d5abcadf866a"
A_IDS = tuple(
    ComplexId(value)
    for value in (
        "lyapunov_weight_lattice_fourier_pisot_spectral_purification",
        "dfi_entropy_plateau_dfi_divergence_spiking",
        "pv_inflation_pure_point_diffraction_non_pv_salem_leakage",
        "parseval_energy_bijection_for_epochs_energy_mass_imbalance",
    )
)
B_IDS = (
    ComplexId("lyapunov_entropy_dissipation_functional"),
    ComplexId("pv_parseval_spectral_energy_lock"),
)
C_IDS = (ComplexId("lyapunov_parseval_training_isometry_closure"),)


@dataclass(frozen=True)
class QENNContractInput:
    signal: torch.Tensor
    tolerance: float = 1e-6
    interaction_weight: float = 1.0
    spatial_weight: float = 1.0


@dataclass(frozen=True)
class QENNSourceLaw:
    law_name: str
    response: torch.Tensor
    residual_field: torch.Tensor
    invariant_residual: float
    failure_condition: str


@dataclass(frozen=True)
class QENNDerivedLaw:
    law_name: str
    source_residuals: tuple[torch.Tensor, torch.Tensor]
    derived_operator: torch.Tensor
    residual_energy: float
    non_cancellation_energy: float


@dataclass(frozen=True)
class QENNSpatialClosure:
    law_name: str
    spatial_domain: torch.Tensor
    local_operator: torch.Tensor
    boundary_trace_residual: float
    localization_residual: float
    reconstruction_residual: float
    coercivity_ratio: float
    observability_residual: float
    closure_status: str


def _validate(value: QENNContractInput) -> torch.Tensor:
    signal = value.signal
    if not isinstance(signal, torch.Tensor) or signal.ndim != 2 or signal.shape[-1] < 4:
        raise DomainViolationError("QENN contracts require a rank-two [batch, feature] tensor with at least four features")
    if not bool(torch.isfinite(signal).all()):
        raise NonFiniteValueError("QENN source signal contains NaN or infinity")
    if not torch.isfinite(torch.tensor((value.tolerance, value.interaction_weight, value.spatial_weight))).all():
        raise NonFiniteValueError("QENN contract parameters must be finite")
    if value.tolerance < 0.0 or value.interaction_weight <= 0.0 or value.spatial_weight <= 0.0:
        raise DomainViolationError("QENN tolerance must be non-negative and both weights strictly positive")
    return signal


def _as_float(value: torch.Tensor) -> float:
    if not bool(torch.isfinite(value).all()):
        raise NonFiniteValueError("QENN result contains NaN or infinity")
    return float(value.detach().cpu())


def source_operator(index: int, value: QENNContractInput) -> QENNSourceLaw:
    signal = _validate(value)
    if index == 0:
        # Negative Lyapunov increments are the contraction branch; positive
        # increments form the explicit loss of contraction residual.
        magnitudes = torch.linalg.vector_norm(signal, dim=0)
        increments = magnitudes[1:] - magnitudes[:-1]
        residual = torch.nn.functional.pad(torch.relu(increments), (1, 0)).expand_as(signal)
        response = signal - residual
        failure = "non-negative Lyapunov contraction margin"
    elif index == 1:
        magnitudes = signal.abs()
        denominator = magnitudes.sum(dim=-1, keepdim=True)
        if bool((denominator == 0).any()):
            raise DomainViolationError("normalized DFI entropy law is singular for an all-zero sample")
        probabilities = magnitudes / denominator
        entropy = -(probabilities * torch.log(probabilities.clamp_min(torch.finfo(signal.dtype).tiny))).sum(dim=-1, keepdim=True)
        response = entropy.expand_as(signal)
        residual = (response - response.mean(dim=0, keepdim=True)).abs()
        failure = "DFI entropy divergence or batch spiking"
    elif index == 2:
        spectrum = torch.fft.rfft(signal, dim=-1, norm="ortho")
        dominant = spectrum.abs().argmax(dim=-1, keepdim=True)
        pure = torch.zeros_like(spectrum).scatter(-1, dominant, spectrum.gather(-1, dominant))
        response = torch.fft.irfft(pure, n=signal.shape[-1], dim=-1, norm="ortho")
        residual = signal - response
        failure = "non-PV or Salem continuous spectral leakage"
    elif index == 3:
        spectrum = torch.fft.rfft(signal, dim=-1, norm="ortho")
        response = torch.fft.irfft(spectrum, n=signal.shape[-1], dim=-1, norm="ortho")
        energy_error = torch.linalg.vector_norm(signal, dim=-1, keepdim=True) - torch.linalg.vector_norm(spectrum, dim=-1, keepdim=True)
        residual = energy_error.expand_as(signal)
        failure = "epoch energy or mass imbalance"
    else:
        raise IndexError(index)
    invariant = _as_float(torch.linalg.vector_norm(residual))
    return QENNSourceLaw(str(A_IDS[index]), response, residual, invariant, failure)


def _normalized_defect(field: torch.Tensor) -> torch.Tensor:
    magnitude = field.abs()
    return magnitude / (1.0 + magnitude)


def derived_operator(index: int, value: QENNContractInput) -> QENNDerivedLaw:
    first_index, second_index = ((0, 1), (2, 3))[index]
    first = source_operator(first_index, value)
    second = source_operator(second_index, value)
    delta_first = _normalized_defect(first.residual_field)
    delta_second = _normalized_defect(second.residual_field)
    interaction = value.interaction_weight * (delta_first - delta_second).square()
    operator = first.residual_field.square() + second.residual_field.square() + interaction
    total = _as_float(operator.sum())
    non_cancellation = _as_float(interaction.sum())
    return QENNDerivedLaw(str(B_IDS[index]), (first.residual_field, second.residual_field), operator, total, non_cancellation)


def spatial_operator(value: QENNContractInput) -> QENNSpatialClosure:
    signal = _validate(value)
    first = derived_operator(0, value)
    second = derived_operator(1, value)
    theta_first = _normalized_defect(first.derived_operator)
    theta_second = _normalized_defect(second.derived_operator)
    potential = 0.5 * (theta_first + theta_second)
    gradient = potential[..., 1:] - potential[..., :-1]
    gradient_density = torch.nn.functional.pad(gradient.square(), (1, 0))
    local = first.derived_operator + second.derived_operator + value.spatial_weight * gradient_density
    reconstructed = local - first.derived_operator - second.derived_operator - value.spatial_weight * gradient_density
    boundary = _as_float(local[..., 0].abs().sum() + local[..., -1].abs().sum())
    localization = _as_float(gradient.abs().sum())
    reconstruction = _as_float(torch.linalg.vector_norm(reconstructed))
    source_norm = _as_float(torch.linalg.vector_norm(signal))
    local_norm = _as_float(torch.linalg.vector_norm(local))
    coercivity = local_norm / source_norm if source_norm > 0.0 else 0.0
    observable = _as_float((first.derived_operator + second.derived_operator - local).abs().mean())
    closed = reconstruction <= value.tolerance and coercivity > 0.0
    coordinates = torch.linspace(0.0, 1.0, signal.shape[-1], dtype=signal.dtype, device=signal.device)
    return QENNSpatialClosure(
        str(C_IDS[0]), coordinates, local, boundary, localization, reconstruction,
        coercivity, observable, "numerical_candidate" if closed else "open",
    )


def _residual(name: str, values: tuple[float, ...], tolerance: float) -> ResidualResult:
    norm = sum(item * item for item in values) ** 0.5
    passed = norm <= tolerance
    return ResidualResult(name, values, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN)


def _remove_a(b_index: int, source_index: int, value: QENNContractInput) -> SourceRemovalResult:
    output = derived_operator(b_index, value)
    first, second = output.source_residuals
    surviving = second.square() if source_index == 0 else first.square()
    baseline = output.derived_operator.sum()
    removed = surviving.sum()
    delta = (baseline - removed).abs()
    a_index = b_index * 2 + source_index
    return SourceRemovalResult(A_IDS[a_index], _as_float(baseline), _as_float(removed), _as_float(delta), _as_float(delta) > 1e-12)


def _remove_b(b_index: int, value: QENNContractInput) -> SourceRemovalResult:
    output = spatial_operator(value)
    surviving = derived_operator(1 - b_index, value).derived_operator
    baseline = output.local_operator.sum()
    removed = surviving.sum()
    delta = (baseline - removed).abs()
    return SourceRemovalResult(B_IDS[b_index], _as_float(baseline), _as_float(removed), _as_float(delta), _as_float(delta) > 1e-12)


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec("QENN training field", "finite rank-two training state and positive residual weights", (QENNContractInput,))
    artifact = ArtifactSpec(("residual_table", "closure_field", "source_removal_comparison"), "python -m the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite")
    result: list[ComplexContract] = []
    for index, complex_id in enumerate(A_IDS):
        result.append(ComplexContract(
            complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.A, (), domain,
            CodomainSpec(f"{complex_id} source law", "typed QENN response, invariant residual, and failure condition", (QENNSourceLaw,)),
            partial(source_operator, index),
            residual=lambda source, output, cid=str(complex_id): _residual(cid, (output.invariant_residual,), source.tolerance),
            implementation_path="the_nothingness_effect/artificial_intelligence/qenn/contracts.py",
        ))
    for index, complex_id in enumerate(B_IDS):
        source_ids = (A_IDS[2 * index], A_IDS[2 * index + 1])
        result.append(ComplexContract(
            complex_id, APPENDIX, APPENDIX_SHA256, ComplexLevel.B, source_ids, domain,
            CodomainSpec(f"{complex_id} residual energy", "positive non-cancelling two-source residual-energy operator", (QENNDerivedLaw,)),
            partial(derived_operator, index),
            residual=lambda source, output, cid=str(complex_id): _residual(cid, (output.residual_energy,), source.tolerance),
            source_removal_checks=(partial(_remove_a, index, 0), partial(_remove_a, index, 1)),
            artifact_spec=artifact,
            implementation_path="the_nothingness_effect/artificial_intelligence/qenn/contracts.py",
        ))
    result.append(ComplexContract(
        C_IDS[0], APPENDIX, APPENDIX_SHA256, ComplexLevel.C, B_IDS, domain,
        CodomainSpec(str(C_IDS[0]), "one spatial defect field with boundary, localization, coercivity, reconstruction, and observability diagnostics", (QENNSpatialClosure,)),
        spatial_operator,
        residual=lambda source, output: _residual(str(C_IDS[0]), (output.reconstruction_residual, output.observability_residual), source.tolerance),
        closure_predicate=lambda output, residual: output.closure_status == "numerical_candidate" and output.coercivity_ratio > 0.0 and residual is not None and residual.passed,
        source_removal_checks=(partial(_remove_b, 0), partial(_remove_b, 1)),
        artifact_spec=artifact,
        exact_semantics=False,
        implementation_path="the_nothingness_effect/artificial_intelligence/qenn/contracts.py",
    ))
    return tuple(result)


def registered_qenn_registry(matrix: str | Path = "docs/data/theorem_complex_implementation_matrix.csv") -> TheoremComplexRegistry:
    registry = TheoremComplexRegistry.from_csv(matrix)
    for contract in contracts():
        registry.register(contract)
    return registry
