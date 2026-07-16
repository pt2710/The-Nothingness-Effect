"""Executable QENN A05--A12 source contracts.

These laws complete the native 12A QENN registry.  The finite operators preserve
the appendix distinction between exact identities and numerical witnesses:
a residual measures the named failure dual and never upgrades a finite sample to
an asymptotic theorem.
"""

from __future__ import annotations

from functools import partial

import torch

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    NonFiniteValueError,
)

from .contracts import (
    APPENDIX,
    APPENDIX_SHA256,
    QENNContractInput,
    QENNSourceLaw,
    _as_float,
    _validate,
)


SOURCE_IDS = tuple(
    ComplexId(identifier)
    for identifier in (
        "autocorrelation_completeness_of_weight_trajectories_continuous_mixing_component",
        "flowpoint_flip_parity_constraint_parity_broken_bias_spurious_lines",
        "qenn::dual_support_equivalence_support_mismatch_leakage",
        "bounded_remainder_drift_in_updates_long_memory_heavy_tail_drift",
        "inflation_collapse_support_invariance_nonlinear_sideband_mixing",
        "epoch_operator_closure_backprop_optimiser_induced_resonance",
        "entropy_balanced_landscape_no_sharp_minima_sharp_minima_trap",
        "hyper_parameter_stability_wedge_instability_lobe",
    )
)
IMPLEMENTATION = "the_nothingness_effect/artificial_intelligence/qenn/source_contracts.py"


def _expand_scalar(value: torch.Tensor, signal: torch.Tensor) -> torch.Tensor:
    return value.reshape(1, 1).expand_as(signal)


def _spectral_support(spectrum: torch.Tensor) -> torch.Tensor:
    magnitude = spectrum.abs()
    maximum = magnitude.amax(dim=-1, keepdim=True).clamp_min(
        torch.finfo(magnitude.dtype).eps
    )
    return magnitude >= 0.25 * maximum


def _autocorrelation(signal: torch.Tensor) -> torch.Tensor:
    centered = signal - signal.mean(dim=0, keepdim=True)
    denominator = centered.square().sum().clamp_min(torch.finfo(signal.dtype).eps)
    values = [torch.ones((), dtype=signal.dtype, device=signal.device)]
    for lag in range(1, signal.shape[0]):
        values.append((centered[:-lag] * centered[lag:]).sum() / denominator)
    return torch.stack(values)


def source_operator(index: int, value: QENNContractInput) -> QENNSourceLaw:
    signal = _validate(value)
    eps = torch.finfo(signal.dtype).eps

    if index == 0:
        autocorrelation = _autocorrelation(signal)
        measure = torch.fft.rfft(autocorrelation, norm="ortho").abs().square()
        support = _spectral_support(measure.unsqueeze(0)).squeeze(0)
        continuous_mass = measure.masked_fill(support, 0.0).sum() / measure.sum().clamp_min(eps)
        response = _expand_scalar(1.0 - continuous_mass, signal)
        residual = _expand_scalar(continuous_mass, signal)
        failure = "continuous autocorrelation mass or unresolved structural mixing"
    elif index == 1:
        spectrum = torch.fft.rfft(signal, dim=-1, norm="ortho")
        signs = torch.where(
            torch.arange(spectrum.shape[-1], device=signal.device) % 2 == 0,
            torch.ones((), dtype=signal.dtype, device=signal.device),
            -torch.ones((), dtype=signal.dtype, device=signal.device),
        )
        locked = spectrum * signs
        mirror = torch.flip(locked.abs(), dims=(-1,))
        asymmetry = (locked.abs() - mirror).abs()
        response = torch.fft.irfft(locked, n=signal.shape[-1], dim=-1, norm="ortho")
        residual = torch.fft.irfft(
            asymmetry.to(spectrum.dtype), n=signal.shape[-1], dim=-1, norm="ortho"
        ).abs()
        failure = "parity-broken mirror bias or asymmetric spurious spectral lines"
    elif index == 2:
        spectrum = torch.fft.rfft(signal, dim=-1, norm="ortho")
        dual_spectrum = torch.fft.rfft(torch.flip(signal, dims=(-1,)), dim=-1, norm="ortho")
        first_support = _spectral_support(spectrum)
        second_support = _spectral_support(dual_spectrum)
        mismatch = torch.logical_xor(first_support, second_support)
        leakage = spectrum.masked_fill(first_support & second_support, 0.0)
        response = torch.fft.irfft(
            spectrum.masked_fill(mismatch, 0.0), n=signal.shape[-1], dim=-1, norm="ortho"
        )
        residual = torch.fft.irfft(leakage, n=signal.shape[-1], dim=-1, norm="ortho").abs()
        failure = "dual support mismatch or spectral leakage outside the common support"
    elif index == 3:
        increments = signal[1:] - signal[:-1]
        cumulative = torch.cumsum(increments, dim=0)
        drift_budget = increments.abs().sum(dim=0, keepdim=True).clamp_min(eps)
        bounded_remainder = cumulative.abs() / drift_budget
        tail = increments - increments.mean(dim=0, keepdim=True)
        if tail.shape[0] > 1:
            memory = (tail[:-1] * tail[1:]).abs().mean(dim=0, keepdim=True)
        else:
            memory = torch.zeros_like(drift_budget)
        residual_core = torch.relu(bounded_remainder - 1.0) + memory / drift_budget
        residual = torch.nn.functional.pad(residual_core, (0, 0, 1, 0))
        response = signal - residual
        failure = "unbounded update remainder, long-memory covariance, or heavy-tail drift"
    elif index == 4:
        spectrum = torch.fft.rfft(signal, dim=-1, norm="ortho")
        support = _spectral_support(spectrum)
        inflated = spectrum * ((1.0 + 5.0**0.5) / 2.0)
        collapsed = inflated.masked_fill(~support, 0.0)
        nonlinear = torch.fft.rfft(signal.square(), dim=-1, norm="ortho")
        sideband = nonlinear.masked_fill(support, 0.0)
        response = torch.fft.irfft(collapsed, n=signal.shape[-1], dim=-1, norm="ortho")
        residual = torch.fft.irfft(sideband, n=signal.shape[-1], dim=-1, norm="ortho").abs()
        failure = "nonlinear sideband energy outside the inflation-collapse support"
    elif index == 5:
        if signal.shape[0] < 2:
            operator = torch.eye(signal.shape[-1], dtype=signal.dtype, device=signal.device)
        else:
            left = signal[:-1]
            right = signal[1:]
            operator = torch.linalg.pinv(left) @ right
        eigenvalues = torch.linalg.eigvals(operator)
        spectral_radius = eigenvalues.abs().amax().real
        contraction_defect = torch.relu(spectral_radius - (1.0 - value.tolerance))
        response = signal @ operator.real.to(signal.dtype)
        residual = _expand_scalar(contraction_defect, signal)
        failure = "epoch operator loses contractivity or optimizer-induced resonance appears"
    elif index == 6:
        centered = signal - signal.mean(dim=0, keepdim=True)
        covariance = centered.T @ centered / max(signal.shape[0] - 1, 1)
        curvature = torch.linalg.eigvalsh(covariance).clamp_min(0.0)
        mean_curvature = curvature.mean().clamp_min(eps)
        sharpness = curvature.amax() / mean_curvature
        probabilities = curvature / curvature.sum().clamp_min(eps)
        entropy = -(probabilities * torch.log(probabilities.clamp_min(eps))).sum()
        maximum_entropy = torch.log(
            torch.as_tensor(curvature.numel(), dtype=signal.dtype, device=signal.device)
        ).clamp_min(eps)
        defect = torch.relu(sharpness - 4.0) + torch.relu(0.5 - entropy / maximum_entropy)
        response = signal / (1.0 + sharpness)
        residual = _expand_scalar(defect, signal)
        failure = "sharp-minimum curvature trap or entropy-imbalanced landscape"
    elif index == 7:
        centered = signal - signal.mean(dim=0, keepdim=True)
        covariance = centered.T @ centered / max(signal.shape[0] - 1, 1)
        radius = torch.linalg.eigvalsh(covariance).abs().amax()
        learning_scale = torch.as_tensor(
            value.interaction_weight, dtype=signal.dtype, device=signal.device
        )
        regularization = torch.as_tensor(
            value.spatial_weight, dtype=signal.dtype, device=signal.device
        )
        stability_margin = 1.0 - learning_scale * radius / (1.0 + regularization)
        defect = torch.relu(-stability_margin)
        response = _expand_scalar(stability_margin, signal)
        residual = _expand_scalar(defect, signal)
        failure = "hyper-parameter point lies outside the contraction stability wedge"
    else:
        raise IndexError(index)

    if not bool(torch.isfinite(response).all()) or not bool(torch.isfinite(residual).all()):
        raise NonFiniteValueError("QENN source-law result contains NaN or infinity")
    return QENNSourceLaw(
        str(SOURCE_IDS[index]),
        response,
        residual,
        _as_float(torch.linalg.vector_norm(residual)),
        failure,
    )


def _residual(
    source: QENNContractInput,
    output: QENNSourceLaw,
) -> ResidualResult:
    value = output.invariant_residual
    passed = value <= source.tolerance
    return ResidualResult(
        output.law_name,
        (value,),
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {"failure_condition": output.failure_condition},
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "QENN extended source field",
        "finite rank-two epoch/weight trajectory and positive diagnostic weights",
        (QENNContractInput,),
    )
    return tuple(
        ComplexContract(
            complex_id,
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.A,
            (),
            domain,
            CodomainSpec(
                str(complex_id),
                "typed QENN source response with explicit failure-dual residual",
                (QENNSourceLaw,),
            ),
            partial(source_operator, index),
            residual=_residual,
            exact_semantics=False,
            implementation_path=IMPLEMENTATION,
        )
        for index, complex_id in enumerate(SOURCE_IDS)
    )
