"""Four authoritative A-level Flowpoint source laws."""

from __future__ import annotations

import numpy as np

from equations.theorem_complex_runtime import (
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    InvariantResult,
    ResidualResult,
)

from .flowpoint import (
    BalanceFiber,
    FlowpointSchedule,
    PhaseClock,
    canonical_involution,
)


APPENDIX = "appendix_canonical_self_negating_involution_flowpoint.tex"
APPENDIX_SHA256 = "5c44d82b34cd4c5d05d01253a62987f2f6099d582bf954a4cbdbc13b52b52206"


def _norm(value) -> float:
    return float(np.linalg.norm(np.asarray(value)))


def _self_negating_invariant(source, output) -> InvariantResult:
    residual = _norm(canonical_involution(output) - source)
    return InvariantResult("F^2=I", residual == 0.0, residual, 0.0)


def _schedule_invariant(_source, output: FlowpointSchedule) -> InvariantResult:
    residual = float(sum(time % 2 != bit for time, bit in zip(output.times, output.bits, strict=True)))
    return InvariantResult("T_k congruent a_k mod 2", residual == 0.0, residual, 0.0)


def _swap_invariant(source: BalanceFiber, output: BalanceFiber) -> InvariantResult:
    reconstructed = output.swap()
    residual = _norm(reconstructed.first - source.first) + _norm(reconstructed.second - source.second)
    return InvariantResult("J^2=I", residual == 0.0, residual, 0.0)


def _balance_residual(source: BalanceFiber, output: BalanceFiber) -> ResidualResult:
    residual = _norm(output.balance - source.balance)
    return ResidualResult(
        "swap balance invariance",
        (residual,),
        1e-12,
        residual <= 1e-12,
        ClosureStatus.SATISFIED if residual <= 1e-12 else ClosureStatus.OPEN,
    )


def _phase_invariant(source: PhaseClock, output: PhaseClock) -> InvariantResult:
    residual = float(output.shift().phase != source.phase)
    return InvariantResult("theta^2=id", residual == 0.0, residual, 0.0)


def contracts() -> tuple[ComplexContract, ...]:
    return (
        ComplexContract(
            complex_id=ComplexId("self_negating_oscillation_and_eigenstructure"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.A,
            source_ids=(),
            domain=DomainSpec(
                "non-Boolean numeric vector space",
                "finite numeric scalar or array",
                (int, float, complex, np.ndarray),
                validator=lambda value: not isinstance(value, bool),
            ),
            codomain=CodomainSpec(
                "same numeric vector space",
                "finite value with source shape",
                (int, float, complex, np.ndarray),
            ),
            operator=canonical_involution,
            invariant=_self_negating_invariant,
            implementation_path="equations/flowpoint/a_level.py",
        ),
        ComplexContract(
            complex_id=ComplexId("parity_to_bit_equivalence_and_2_adic_coding"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.A,
            source_ids=(),
            domain=DomainSpec(
                "finite binary prefix",
                "nonempty sequence containing only 0 and 1",
                (tuple, list),
            ),
            codomain=CodomainSpec(
                "scheduled finite 2-adic prefix",
                "exact parity schedule with explicit prefix length",
                (FlowpointSchedule,),
            ),
            operator=FlowpointSchedule.from_bits,
            invariant=_schedule_invariant,
            implementation_path="equations/flowpoint/a_level.py",
        ),
        ComplexContract(
            complex_id=ComplexId("kernel_fiber_integrability"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.A,
            source_ids=(),
            domain=DomainSpec("balance fiber", "pair in V x V", (BalanceFiber,)),
            codomain=CodomainSpec("balance fiber", "swapped pair in V x V", (BalanceFiber,)),
            operator=lambda fiber: fiber.swap(),
            invariant=_swap_invariant,
            residual=_balance_residual,
            implementation_path="equations/flowpoint/a_level.py",
        ),
        ComplexContract(
            complex_id=ComplexId("phase_clock"),
            appendix=APPENDIX,
            appendix_source_sha256=APPENDIX_SHA256,
            level=ComplexLevel.A,
            source_ids=(),
            domain=DomainSpec("C2 phase torsor", "phase in {0,1}", (PhaseClock,)),
            codomain=CodomainSpec("C2 phase torsor", "shifted phase", (PhaseClock,)),
            operator=lambda phase: phase.shift(),
            invariant=_phase_invariant,
            implementation_path="equations/flowpoint/a_level.py",
        ),
    )
