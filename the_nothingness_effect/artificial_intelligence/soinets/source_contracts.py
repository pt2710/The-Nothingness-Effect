"""Executable SOInet A05--A18 source contracts.

The operators use the native typed modality field ``[modality, space, feature]``.
Each finite result retains the named complementary failure as an explicit
residual field; no finite diagnostic is promoted to a universal theorem.
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
    SOInetContractInput,
    SOInetSourceLaw,
    _float,
    _validate,
)


SOURCE_IDS = tuple(
    ComplexId(identifier)
    for identifier in (
        "hierarchical_soi_stack_transfer_cross_regime_collapse_duality",
        "soi_cross_domain_generalization_and_collapse",
        "soi_entropy_minimization_and_entropic_catastrophe",
        "soi_spectrum_learning_and_classification_soi_spectrum_degeneracy_dual_instability",
        "soinet_cross_modal_compositionality_modality_invariant_collapse_principle",
        "soinet_cross_modal_transfer_generalization_and_dual_stability",
        "soinet_error_contraction_and_dual_error_orthogonality",
        "soinet_meta_learnability_dual_closure",
        "soinet_modality_invariant_learning_and_universal_adaptation",
        "soinet_universal_cloning_principle_cloning_failure_duality",
        "soinet_universal_expressivity_bound_entropy_minimal_generalization_principle",
        "soinet_universal_generalization_principle_failure_brittleness_duality",
        "spectral_phase_locking_and_collapse_in_soinet",
        "universal_entropy_minimization_and_collapse_degeneracy_duality_in_soinet",
    )
)
IMPLEMENTATION = "the_nothingness_effect/artificial_intelligence/soinets/source_contracts.py"


def _expand(value: torch.Tensor, modalities: torch.Tensor) -> torch.Tensor:
    if value.ndim == 0:
        return value.reshape(1, 1, 1).expand_as(modalities)
    if value.ndim == 1 and value.numel() == modalities.shape[0]:
        return value.reshape(-1, 1, 1).expand_as(modalities)
    if value.ndim == 1 and value.numel() == modalities.shape[-1]:
        return value.reshape(1, 1, -1).expand_as(modalities)
    if value.ndim == 2 and value.shape == modalities.shape[:2]:
        return value.unsqueeze(-1).expand_as(modalities)
    if value.ndim == 2 and value.shape == (
        modalities.shape[0],
        modalities.shape[-1],
    ):
        return value.unsqueeze(1).expand_as(modalities)
    return value.expand_as(modalities)


def _probabilities(modalities: torch.Tensor) -> torch.Tensor:
    magnitude = modalities.abs()
    return magnitude / magnitude.sum(dim=-1, keepdim=True).clamp_min(
        torch.finfo(modalities.dtype).eps
    )


def _entropy(modalities: torch.Tensor) -> torch.Tensor:
    probabilities = _probabilities(modalities)
    eps = torch.finfo(modalities.dtype).tiny
    return -(probabilities * torch.log(probabilities.clamp_min(eps))).sum(dim=-1)


def _normalized(value: torch.Tensor, *, dim: int) -> torch.Tensor:
    return value / torch.linalg.vector_norm(value, dim=dim, keepdim=True).clamp_min(
        torch.finfo(value.dtype).eps
    )


def source_operator(index: int, value: SOInetContractInput) -> SOInetSourceLaw:
    modalities = _validate(value)
    eps = torch.finfo(modalities.dtype).eps

    if index == 0:
        summaries = modalities.mean(dim=1)
        normalized = _normalized(summaries, dim=-1)
        transfer = torch.roll(normalized, shifts=-1, dims=0)
        mismatch = torch.linalg.vector_norm(normalized - transfer, dim=-1)
        response = _expand(normalized.mean(dim=0), modalities)
        residual = _expand(mismatch, modalities)
        failure = "cross-regime hierarchy transfer mismatch or stack collapse"
    elif index == 1:
        modality_count = modalities.shape[0]
        total = modalities.sum(dim=0, keepdim=True)
        leave_one_out = (total - modalities) / float(modality_count - 1)
        response = leave_one_out
        residual = (modalities - leave_one_out).abs()
        failure = "cross-domain generalization failure or collapse outside the source domain"
    elif index == 2:
        entropy = _entropy(modalities)
        minimum = entropy.amin(dim=1, keepdim=True)
        catastrophe = torch.relu(entropy - minimum) + torch.relu(eps - entropy)
        response = _expand(entropy, modalities)
        residual = _expand(catastrophe, modalities)
        failure = "entropic catastrophe, undefined probability mass, or failed entropy minimization"
    elif index == 3:
        spectrum = torch.fft.rfft(modalities, dim=1, norm="ortho")
        power = spectrum.abs().square()
        bins = torch.arange(
            power.shape[1], dtype=modalities.dtype, device=modalities.device
        ).reshape(1, -1, 1)
        centroid = (power * bins).sum(dim=1) / power.sum(dim=1).clamp_min(eps)
        normalized_centroid = _normalized(centroid, dim=-1)
        degeneracy = torch.linalg.vector_norm(
            normalized_centroid - normalized_centroid.mean(dim=0, keepdim=True),
            dim=-1,
        )
        response = _expand(normalized_centroid, modalities)
        residual = _expand(degeneracy, modalities)
        failure = "SOI spectral-class degeneracy or dual spectral instability"
    elif index == 4:
        if modalities.shape[0] < 3:
            left = modalities.sum(dim=0)
            right = left
        else:
            first, second, third = modalities[:3]
            left = (first + second) + third
            right = first + (second + third)
        associativity = (left - right).abs()
        collapse = modalities.mean(dim=0)
        response = collapse.unsqueeze(0).expand_as(modalities)
        residual = associativity.unsqueeze(0).expand_as(modalities)
        failure = "cross-modal composition loses associativity or collapses modality information"
    elif index == 5:
        summaries = _normalized(modalities.mean(dim=1), dim=-1)
        gram = summaries @ summaries.T
        identity = torch.eye(
            gram.shape[0], dtype=gram.dtype, device=gram.device
        )
        transfer_defect = (gram - identity).abs().mean(dim=-1)
        response = _expand(summaries, modalities)
        residual = _expand(transfer_defect, modalities)
        failure = "cross-modal transfer is non-generalizing or dual-stability is lost"
    elif index == 6:
        consensus = modalities.mean(dim=0, keepdim=True)
        error = modalities - consensus
        first = error[:-1].reshape(error.shape[0] - 1, -1)
        second = error[1:].reshape(error.shape[0] - 1, -1)
        contraction = torch.relu(
            torch.linalg.vector_norm(second, dim=-1)
            - torch.linalg.vector_norm(first, dim=-1)
        )
        orthogonality = (first * second).sum(dim=-1).abs() / (
            torch.linalg.vector_norm(first, dim=-1)
            * torch.linalg.vector_norm(second, dim=-1)
        ).clamp_min(eps)
        defect = torch.nn.functional.pad(contraction + orthogonality, (0, 1))
        response = consensus.expand_as(modalities)
        residual = _expand(defect, modalities)
        failure = "error fails to contract or adjacent modality errors lose orthogonality"
    elif index == 7:
        flattened = modalities.reshape(modalities.shape[0], -1)
        centered = flattened - flattened.mean(dim=0, keepdim=True)
        singular_values = torch.linalg.svdvals(centered)
        active_rank = (singular_values > value.tolerance).sum().to(modalities.dtype)
        required_rank = torch.as_tensor(
            min(centered.shape), dtype=modalities.dtype, device=modalities.device
        )
        rank_defect = torch.relu(required_rank - active_rank)
        condition = singular_values.amax() / singular_values.amin().clamp_min(eps)
        response = _expand(active_rank / required_rank.clamp_min(1.0), modalities)
        residual = _expand(
            rank_defect + torch.relu(condition - 1e6) / 1e6, modalities
        )
        failure = "meta-learning carrier is rank-deficient or dual closure is ill-conditioned"
    elif index == 8:
        normalized = _normalized(modalities, dim=-1)
        invariant = normalized.mean(dim=0, keepdim=True)
        response = invariant.expand_as(modalities)
        residual = (normalized - invariant).abs()
        failure = "modality-dependent representation blocks universal adaptation"
    elif index == 9:
        modality_count = modalities.shape[0]
        total = modalities.sum(dim=0, keepdim=True)
        clone = (total - modalities) / float(modality_count - 1)
        response = clone
        residual = (modalities - clone).abs()
        failure = "universal cloning reconstruction fails on a held-out modality"
    elif index == 10:
        flattened = modalities.reshape(-1, modalities.shape[-1])
        singular_values = torch.linalg.svdvals(flattened)
        rank = (singular_values > value.tolerance).sum().to(modalities.dtype)
        maximum_rank = torch.as_tensor(
            min(flattened.shape), dtype=modalities.dtype, device=modalities.device
        )
        entropy = _entropy(modalities).mean()
        maximum_entropy = torch.log(
            torch.as_tensor(
                modalities.shape[-1],
                dtype=modalities.dtype,
                device=modalities.device,
            )
        ).clamp_min(eps)
        rank_defect = torch.relu(maximum_rank - rank)
        entropy_defect = torch.relu(0.25 - entropy / maximum_entropy)
        response = _expand(rank / maximum_rank.clamp_min(1.0), modalities)
        residual = _expand(rank_defect + entropy_defect, modalities)
        failure = "expressivity rank bound fails or entropy-minimal generalization degenerates"
    elif index == 11:
        split = modalities.shape[1] // 2
        train = modalities[:, :split]
        test = modalities[:, split:]
        train_summary = train.mean(dim=1)
        test_summary = test.mean(dim=1)
        brittleness = torch.linalg.vector_norm(train_summary - test_summary, dim=-1)
        response = _expand(0.5 * (train_summary + test_summary), modalities)
        residual = _expand(brittleness, modalities)
        failure = "held-out spatial regime reveals universal-generalization brittleness"
    elif index == 12:
        spectrum = torch.fft.rfft(modalities, dim=1, norm="ortho")
        dominant = spectrum.abs().sum(dim=-1).argmax(dim=1)
        selected = torch.stack(
            [spectrum[item, dominant[item]] for item in range(modalities.shape[0])]
        )
        phase = torch.angle(selected)
        reference = phase.mean(dim=0, keepdim=True)
        phase_defect = torch.atan2(
            torch.sin(phase - reference), torch.cos(phase - reference)
        ).abs().mean(dim=-1)
        response = _expand(torch.cos(phase).mean(dim=0), modalities)
        residual = _expand(phase_defect, modalities)
        failure = "spectral phase unlock or phase-selected collapse failure"
    elif index == 13:
        entropy = _entropy(modalities)
        entropy_spread = entropy.std(dim=0, unbiased=False).mean()
        collapse_variance = modalities.var(dim=0, unbiased=False).mean()
        degeneracy = torch.relu(value.tolerance - collapse_variance)
        response = _expand(entropy.mean(), modalities)
        residual = _expand(entropy_spread + degeneracy, modalities)
        failure = "universal entropy minimum coincides with degenerate modality collapse"
    else:
        raise IndexError(index)

    if not bool(torch.isfinite(response).all()) or not bool(
        torch.isfinite(residual).all()
    ):
        raise NonFiniteValueError("SOInet source-law result contains NaN or infinity")
    return SOInetSourceLaw(
        str(SOURCE_IDS[index]),
        response,
        residual,
        _float(torch.linalg.vector_norm(residual)),
        failure,
    )


def _residual(
    source: SOInetContractInput,
    output: SOInetSourceLaw,
) -> ResidualResult:
    passed = output.invariant_residual <= source.tolerance
    return ResidualResult(
        output.law_name,
        (output.invariant_residual,),
        source.tolerance,
        passed,
        ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN,
        {"failure_condition": output.failure_condition},
    )


def contracts() -> tuple[ComplexContract, ...]:
    domain = DomainSpec(
        "SOInet extended modality field",
        "finite [modality, spatial sample, feature] field with positive residual weights",
        (SOInetContractInput,),
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
                "typed SOInet response with explicit complementary failure residual",
                (SOInetSourceLaw,),
            ),
            partial(source_operator, index),
            residual=_residual,
            exact_semantics=False,
            implementation_path=IMPLEMENTATION,
        )
        for index, complex_id in enumerate(SOURCE_IDS)
    )
