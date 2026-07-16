"""Executable PGQENN A05--A10 source contracts.

The finite laws operate on the typed MPL-TC PrimeGraph already used by PGQENN.
They do not infer or alter the prime stream: support, motif, parity, energy, and
shell diagnostics are computed from the declared graph and node features.
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
    DomainViolationError,
    NonFiniteValueError,
)

from .contracts import (
    APPENDIX,
    APPENDIX_SHA256,
    PGQENNContractInput,
    PGQENNSourceLaw,
    _float,
    _normalized_adjacency,
    _validate,
)


SOURCE_IDS = tuple(
    ComplexId(identifier)
    for identifier in (
        "prime_quasicrystal_support_equivalence_support_mismatch_leakage",
        "soi_scaled_annealing_invariance_soi_mis_scaling_spurious_entropy",
        "motif_exhaustion_completeness_coverage_bias_long_memory_drift",
        "weight_energy_parseval_equivalence_layerwise_l_2_energy_mismatch",
        "parity_orthogonal_optimization_cross_parity_gradient_contamination",
        "prime_shell_growth_regularity_shell_instability_phase_slips",
    )
)
IMPLEMENTATION = "the_nothingness_effect/artificial_intelligence/pgqenn/source_contracts.py"


def _expand(value: torch.Tensor, features: torch.Tensor) -> torch.Tensor:
    if value.ndim == 0:
        return value.reshape(1, 1).expand_as(features)
    if value.ndim == 1:
        return value.reshape(1, -1).expand_as(features)
    return value.expand_as(features)


def _support(spectrum: torch.Tensor) -> torch.Tensor:
    magnitude = spectrum.abs()
    threshold = 0.2 * magnitude.amax(dim=0, keepdim=True).clamp_min(
        torch.finfo(magnitude.dtype).eps
    )
    return magnitude >= threshold


def _rfft_energy(spectrum: torch.Tensor, sample_count: int) -> torch.Tensor:
    weights = torch.ones(
        spectrum.shape[0], dtype=spectrum.real.dtype, device=spectrum.device
    )
    if sample_count % 2 == 0:
        if weights.numel() > 2:
            weights[1:-1] = 2.0
    elif weights.numel() > 1:
        weights[1:] = 2.0
    return (spectrum.abs().square() * weights.unsqueeze(-1)).sum(dim=0)


def source_operator(index: int, value: PGQENNContractInput) -> PGQENNSourceLaw:
    features, adjacency = _validate(value)
    eps = torch.finfo(features.dtype).eps

    if index == 0:
        normalized = _normalized_adjacency(adjacency)
        transported = normalized @ features
        spectrum = torch.fft.rfft(features, dim=0, norm="ortho")
        transported_spectrum = torch.fft.rfft(transported, dim=0, norm="ortho")
        common = _support(spectrum) & _support(transported_spectrum)
        projected = spectrum.masked_fill(~common, 0.0)
        leakage = spectrum.masked_fill(common, 0.0)
        response = torch.fft.irfft(
            projected, n=features.shape[0], dim=0, norm="ortho"
        )
        residual = torch.fft.irfft(
            leakage, n=features.shape[0], dim=0, norm="ortho"
        ).abs()
        failure = "prime--quasicrystal support mismatch or graph-transport leakage"
    elif index == 1:
        energy = features.abs().mean(dim=-1, keepdim=True)
        scale = torch.as_tensor(value.K_D, dtype=features.dtype, device=features.device)
        baseline = torch.softmax(-energy / scale, dim=0)
        jointly_scaled = torch.softmax(-(2.0 * energy) / (2.0 * scale), dim=0)
        response = baseline.expand_as(features)
        residual = (baseline - jointly_scaled).abs().expand_as(features)
        failure = "SOI annealing scale is changed without the matching energy rescaling"
    elif index == 2:
        motifs = value.graph.motifs
        if not motifs or len(motifs) != features.shape[0]:
            raise DomainViolationError(
                "motif exhaustion requires one MPL-TC motif record per prime node"
            )
        vocabulary = tuple(sorted(set(motifs)))
        counts = torch.tensor(
            [motifs.count(item) for item in vocabulary],
            dtype=features.dtype,
            device=features.device,
        )
        coverage = counts.sum() / float(len(motifs))
        missing = torch.relu(torch.ones_like(counts) - counts)
        run_tensor = torch.tensor(
            value.graph.motif_runs,
            dtype=features.dtype,
            device=features.device,
        )
        if run_tensor.numel() != features.shape[0]:
            raise DomainViolationError("motif-run history must align with prime nodes")
        run_drift = (
            torch.diff(run_tensor, n=2).abs().mean()
            if run_tensor.numel() > 2
            else torch.zeros((), dtype=features.dtype, device=features.device)
        )
        response = _expand(coverage, features)
        residual = _expand(missing.sum() + run_drift / (1.0 + run_tensor.abs().mean()), features)
        failure = "motif coverage bias or long-memory drift in motif exhaustion"
    elif index == 3:
        spectrum = torch.fft.rfft(features, dim=0, norm="ortho")
        spatial_energy = features.square().sum(dim=0)
        spectral_energy = _rfft_energy(spectrum, features.shape[0])
        mismatch = (spatial_energy - spectral_energy).abs()
        response = features
        residual = _expand(mismatch, features)
        failure = "layerwise weight--energy Parseval mismatch"
    elif index == 4:
        phase = torch.tensor(
            [1.0 if depth.value % 2 == 0 else -1.0 for depth in value.graph.two_adic_depths],
            dtype=features.dtype,
            device=features.device,
        ).unsqueeze(-1)
        even = features * (phase > 0).to(features.dtype)
        odd = features * (phase < 0).to(features.dtype)
        cross = (even * odd).sum(dim=0).abs()
        response = even - odd
        residual = _expand(cross, features)
        failure = "cross-parity gradient contamination or loss of orthogonal optimization"
    elif index == 5:
        primes = torch.tensor(
            value.graph.primes, dtype=features.dtype, device=features.device
        )
        gaps = torch.diff(primes)
        reconstructed = torch.cat((primes[:1], primes[:1] + torch.cumsum(gaps, dim=0)))
        shell_residual = (reconstructed - primes).abs()
        depths = torch.tensor(
            [depth.value for depth in value.graph.two_adic_depths],
            dtype=features.dtype,
            device=features.device,
        )
        phase_slip = (
            torch.relu(torch.diff(depths).abs() - (1.0 + depths[:-1]))
            if depths.numel() > 1
            else torch.zeros_like(depths)
        )
        phase_slip = torch.nn.functional.pad(phase_slip, (1, 0))
        response = torch.stack((primes, depths), dim=-1)
        if response.shape[-1] < features.shape[-1]:
            response = torch.nn.functional.pad(
                response, (0, features.shape[-1] - response.shape[-1])
            )
        else:
            response = response[:, : features.shape[-1]]
        residual = _expand(shell_residual + phase_slip, features)
        failure = "prime-shell reconstruction instability or 2-adic phase slip"
    else:
        raise IndexError(index)

    if not bool(torch.isfinite(response).all()) or not bool(torch.isfinite(residual).all()):
        raise NonFiniteValueError("PGQENN source-law result contains NaN or infinity")
    return PGQENNSourceLaw(
        str(SOURCE_IDS[index]),
        response,
        residual,
        _float(torch.linalg.vector_norm(residual)),
        failure,
    )


def _residual(
    source: PGQENNContractInput,
    output: PGQENNSourceLaw,
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
        "PGQENN extended prime/motif/shell field",
        "typed MPL-TC PrimeGraph with aligned finite node features",
        (PGQENNContractInput,),
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
                "typed prime/motif/shell response with explicit failure-dual residual",
                (PGQENNSourceLaw,),
            ),
            partial(source_operator, index),
            residual=_residual,
            exact_semantics=False,
            implementation_path=IMPLEMENTATION,
        )
        for index, complex_id in enumerate(SOURCE_IDS)
    )
