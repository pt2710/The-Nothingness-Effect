"""Two genuine additive B-level Flowpoint derivations."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from tne_runtime.theorem_complex_runtime import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    InvariantResult,
    ResidualResult,
    SourceRemovalResult,
)
from tne_runtime.theorem_complex_runtime.invariants import source_removal_result

from .a_level import APPENDIX, APPENDIX_SHA256
from .flowpoint import (
    BalanceFiber,
    PhaseClock,
    PhaseTransportResult,
    ScheduledSpectralHistory,
    canonical_involution,
    compose_phase_transports,
    phase_indexed_kernel_transport,
    scheduled_spectral_history,
)


@dataclass(frozen=True)
class ScheduledHistoryInput:
    bits: tuple[int, ...]
    anti_invariant_state: float


@dataclass(frozen=True)
class PhaseTransportInput:
    fiber: BalanceFiber
    source_phase: PhaseClock
    target_phase: PhaseClock
    amplitude: float


def scheduled_history_operator(value: ScheduledHistoryInput) -> ScheduledSpectralHistory:
    return scheduled_spectral_history(value.bits, anti_invariant_state=value.anti_invariant_state)


def scheduled_history_residual(_source, output: ScheduledSpectralHistory) -> ResidualResult:
    residual = output.reconstruction_residual
    return ResidualResult(
        "scheduled history decoder residual",
        (residual,),
        0.0,
        residual == 0.0,
        ClosureStatus.SATISFIED if residual == 0.0 else ClosureStatus.OPEN,
    )


def remove_involution_source(value: ScheduledHistoryInput) -> SourceRemovalResult:
    complete = np.asarray(scheduled_history_operator(value).samples, dtype=float)
    removed = np.full_like(complete, value.anti_invariant_state)
    return source_removal_result(
        ComplexId("self_negating_oscillation_and_eigenstructure"),
        complete,
        removed,
        tolerance=1e-12,
    )


def remove_schedule_source(value: ScheduledHistoryInput) -> SourceRemovalResult:
    complete = np.asarray(scheduled_history_operator(value).samples, dtype=float)
    removed = np.asarray(
        [value.anti_invariant_state if index % 2 == 0 else canonical_involution(value.anti_invariant_state) for index in range(len(value.bits))],
        dtype=float,
    )
    return source_removal_result(
        ComplexId("parity_to_bit_equivalence_and_2_adic_coding"),
        complete,
        removed,
        tolerance=1e-12,
    )


def phase_transport_operator(value: PhaseTransportInput) -> PhaseTransportResult:
    return phase_indexed_kernel_transport(
        value.fiber,
        value.source_phase,
        value.target_phase,
        amplitude=value.amplitude,
    )


def phase_transport_invariant(source: PhaseTransportInput, output: PhaseTransportResult) -> InvariantResult:
    composed, direct = compose_phase_transports(
        source.fiber,
        source.source_phase,
        source.target_phase,
        source.source_phase,
        amplitude=source.amplitude,
    )
    residual = float(
        np.linalg.norm(np.asarray(composed.first) - np.asarray(direct.first))
        + np.linalg.norm(np.asarray(composed.second) - np.asarray(direct.second))
    )
    return InvariantResult("pair-groupoid composition", residual <= 1e-12, residual, 1e-12)


def phase_transport_residual(_source, output: PhaseTransportResult) -> ResidualResult:
    residual = output.balance_residual
    return ResidualResult(
        "balance-fiber transport residual",
        (residual,),
        1e-12,
        residual <= 1e-12,
        ClosureStatus.SATISFIED if residual <= 1e-12 else ClosureStatus.OPEN,
    )


def remove_balance_fiber_source(value: PhaseTransportInput) -> SourceRemovalResult:
    complete = phase_transport_operator(value).transported
    removed_input = PhaseTransportInput(
        BalanceFiber(0.0, 0.0), value.source_phase, value.target_phase, value.amplitude
    )
    removed = phase_transport_operator(removed_input).transported
    return source_removal_result(
        ComplexId("kernel_fiber_integrability"),
        np.asarray((complete.first, complete.second), dtype=float),
        np.asarray((removed.first, removed.second), dtype=float),
        tolerance=1e-12,
    )


def remove_phase_clock_source(value: PhaseTransportInput) -> SourceRemovalResult:
    complete = phase_transport_operator(value).transported
    removed_input = PhaseTransportInput(
        value.fiber, value.source_phase, value.source_phase, value.amplitude
    )
    removed = phase_transport_operator(removed_input).transported
    return source_removal_result(
        ComplexId("phase_clock"),
        np.asarray((complete.first, complete.second), dtype=float),
        np.asarray((removed.first, removed.second), dtype=float),
        tolerance=1e-12,
    )


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            complex_id=ComplexId("scheduled_spectral_history"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.B,
            source_ids=(
                ComplexId("self_negating_oscillation_and_eigenstructure"),
                ComplexId("parity_to_bit_equivalence_and_2_adic_coding"),
            ),
            domain=DomainSpec(
                "scheduled history input",
                "complete binary schedule and nonzero anti-invariant state",
                (ScheduledHistoryInput,),
            ),
            codomain=CodomainSpec(
                "scheduled spectral history",
                "decoded anti-invariant samples",
                (ScheduledSpectralHistory,),
            ),
            operator=scheduled_history_operator,
            residual=scheduled_history_residual,
            source_removal_checks=(remove_involution_source, remove_schedule_source),
            artifact_spec=ArtifactSpec(
                ("metrics_csv", "residual_plot", "source_removal_plot", "operator_diagram"),
                "python -m equations.flowpoint.simulation",
            ),
            implementation_path="equations/flowpoint/b_level.py",
        ),
        ComplexContract(
            complex_id=ComplexId("phase_indexed_kernel_transport"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.B,
            source_ids=(ComplexId("kernel_fiber_integrability"), ComplexId("phase_clock")),
            domain=DomainSpec(
                "phase transport input",
                "balance fiber, two C2 phases, and finite amplitude",
                (PhaseTransportInput,),
            ),
            codomain=CodomainSpec(
                "balance-preserving transport",
                "translated point in the same balance fiber",
                (PhaseTransportResult,),
            ),
            operator=phase_transport_operator,
            invariant=phase_transport_invariant,
            residual=phase_transport_residual,
            source_removal_checks=(remove_balance_fiber_source, remove_phase_clock_source),
            artifact_spec=ArtifactSpec(
                ("metrics_csv", "residual_plot", "source_removal_plot", "operator_diagram"),
                "python -m equations.flowpoint.simulation",
            ),
            implementation_path="equations/flowpoint/b_level.py",
        ),
    )
