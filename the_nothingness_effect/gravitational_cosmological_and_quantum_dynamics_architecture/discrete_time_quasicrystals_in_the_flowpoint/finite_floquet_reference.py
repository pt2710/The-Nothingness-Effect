"""Finite spin-chain Floquet reference for DTQC diagnostics.

This module supplies a bounded many-body numerical comparison.  It does not
promote a finite matrix simulation to a thermodynamic-limit existence theorem,
material realization, or formal validation of the TNE DTQC construction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch


CLAIM_BOUNDARY = (
    "finite spin-chain Floquet reference only; not a thermodynamic-limit "
    "existence proof, material validation, or formal physical attainment claim"
)


@dataclass(frozen=True)
class FiniteFloquetResult:
    signal: torch.Tensor
    frequencies: torch.Tensor
    temporal_power: torch.Tensor
    unitarity_residual: torch.Tensor
    period_two_correlation: torch.Tensor
    one_period_anticorrelation: torch.Tensor
    subharmonic_fraction: torch.Tensor
    spin_count: int
    periods: int
    pulse_angle: float
    disorder_strength: float
    closure_status: str
    claim_boundary: str = CLAIM_BOUNDARY


def _kron_all(operators: tuple[torch.Tensor, ...]) -> torch.Tensor:
    result = operators[0]
    for operator in operators[1:]:
        result = torch.kron(result, operator)
    return result


def _local_operator(
    operator: torch.Tensor, site: int, spin_count: int, identity: torch.Tensor
) -> torch.Tensor:
    factors = tuple(
        operator if index == site else identity for index in range(spin_count)
    )
    return _kron_all(factors)


def _correlation(left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
    left = left - left.mean()
    right = right - right.mean()
    denominator = (
        torch.linalg.vector_norm(left) * torch.linalg.vector_norm(right)
    ).clamp_min(torch.finfo(left.dtype).eps)
    return torch.dot(left, right) / denominator


def simulate_finite_floquet(
    *,
    spin_count: int = 4,
    periods: int = 32,
    interaction_strength: float = 0.35,
    disorder_strength: float = 0.18,
    pulse_error: float = 0.03,
    seed: int = 0,
    flowpoint_enabled: bool = True,
) -> FiniteFloquetResult:
    """Evolve a finite disordered Ising chain under a two-step Floquet unitary."""

    if not 2 <= spin_count <= 8:
        raise ValueError("finite Floquet reference supports two to eight spins")
    if periods < 8 or periods % 2:
        raise ValueError("finite Floquet reference requires an even period count >= 8")
    for name, value in (
        ("interaction_strength", interaction_strength),
        ("disorder_strength", disorder_strength),
        ("pulse_error", pulse_error),
    ):
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"{name} must be finite and non-negative")

    real_dtype = torch.float64
    complex_dtype = torch.complex128
    identity = torch.eye(2, dtype=complex_dtype)
    pauli_x = torch.tensor(((0.0, 1.0), (1.0, 0.0)), dtype=complex_dtype)
    pauli_z = torch.tensor(((1.0, 0.0), (0.0, -1.0)), dtype=complex_dtype)
    dimension = 2**spin_count
    zero = torch.zeros((dimension, dimension), dtype=complex_dtype)
    x_ops = tuple(
        _local_operator(pauli_x, site, spin_count, identity)
        for site in range(spin_count)
    )
    z_ops = tuple(
        _local_operator(pauli_z, site, spin_count, identity)
        for site in range(spin_count)
    )

    generator = torch.Generator().manual_seed(seed)
    fields = disorder_strength * (
        2.0 * torch.rand(spin_count, generator=generator, dtype=real_dtype) - 1.0
    )
    interaction_hamiltonian = zero.clone()
    for site in range(spin_count):
        interaction_hamiltonian = interaction_hamiltonian + fields[site] * z_ops[site]
        neighbor = (site + 1) % spin_count
        interaction_hamiltonian = (
            interaction_hamiltonian
            + interaction_strength * (z_ops[site] @ z_ops[neighbor])
        )

    pulse_angle = (
        math.pi * (1.0 - pulse_error) if flowpoint_enabled else 0.0
    )
    pulse_hamiltonian = zero.clone()
    for operator in x_ops:
        pulse_hamiltonian = pulse_hamiltonian + 0.5 * pulse_angle * operator
    interaction_unitary = torch.matrix_exp(-1j * interaction_hamiltonian)
    pulse_unitary = torch.matrix_exp(-1j * pulse_hamiltonian)
    floquet = interaction_unitary @ pulse_unitary
    unitarity_residual = torch.linalg.matrix_norm(
        floquet.conj().T @ floquet - torch.eye(dimension, dtype=complex_dtype)
    ).real

    state = torch.zeros(dimension, dtype=complex_dtype)
    state[0] = 1.0
    magnetization = sum(z_ops) / float(spin_count)
    signal = []
    for _ in range(periods):
        state = floquet @ state
        observed = torch.vdot(state, magnetization @ state).real
        signal.append(observed)
    signal_tensor = torch.stack(signal).to(dtype=real_dtype)
    centered = signal_tensor - signal_tensor.mean()
    spectrum = torch.fft.rfft(centered, norm="ortho")
    power = spectrum.abs().square()
    frequencies = torch.fft.rfftfreq(periods, d=1.0, dtype=real_dtype)
    target_index = int(torch.argmin(torch.abs(frequencies - 0.5)))
    non_dc = power[1:].sum().clamp_min(torch.finfo(real_dtype).eps)
    subharmonic_fraction = power[target_index] / non_dc
    period_two = _correlation(signal_tensor[:-2], signal_tensor[2:])
    one_period_anticorrelation = -_correlation(
        signal_tensor[:-1], signal_tensor[1:]
    )
    closed = bool(
        unitarity_residual <= 1e-9
        and period_two >= 0.5
        and subharmonic_fraction >= 0.25
    )
    return FiniteFloquetResult(
        signal=signal_tensor,
        frequencies=frequencies,
        temporal_power=power,
        unitarity_residual=unitarity_residual,
        period_two_correlation=period_two,
        one_period_anticorrelation=one_period_anticorrelation,
        subharmonic_fraction=subharmonic_fraction,
        spin_count=spin_count,
        periods=periods,
        pulse_angle=pulse_angle,
        disorder_strength=disorder_strength,
        closure_status="numerical_candidate" if closed else "open",
    )


def finite_floquet_benchmark(
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    spin_count: int = 4,
    periods: int = 32,
) -> tuple[dict[str, float | int | str], ...]:
    if len(seeds) < 2:
        raise ValueError("finite Floquet benchmark requires at least two seeds")
    rows = []
    for seed in seeds:
        canonical = simulate_finite_floquet(
            spin_count=spin_count,
            periods=periods,
            seed=seed,
            flowpoint_enabled=True,
        )
        ablation = simulate_finite_floquet(
            spin_count=spin_count,
            periods=periods,
            seed=seed,
            flowpoint_enabled=False,
        )
        rows.append(
            {
                "seed": seed,
                "spin_count": spin_count,
                "periods": periods,
                "unitarity_residual": float(canonical.unitarity_residual),
                "period_two_correlation": float(canonical.period_two_correlation),
                "one_period_anticorrelation": float(
                    canonical.one_period_anticorrelation
                ),
                "subharmonic_fraction": float(canonical.subharmonic_fraction),
                "flowpoint_ablation_subharmonic_fraction": float(
                    ablation.subharmonic_fraction
                ),
                "subharmonic_source_removal_delta": float(
                    canonical.subharmonic_fraction - ablation.subharmonic_fraction
                ),
                "closure_status": canonical.closure_status,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return tuple(rows)
