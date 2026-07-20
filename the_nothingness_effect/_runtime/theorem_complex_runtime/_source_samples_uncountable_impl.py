"""Deterministic provenance witnesses with modular Foundational extensions."""

from __future__ import annotations

from ._source_samples_impl import *  # noqa: F401,F403
from ._source_samples_impl import sample_inputs as _base_sample_inputs

from the_nothingness_effect.foundational_architecture.uncountable_infinity.canonical_contracts import (
    A1 as UNCOUNTABLE_A1,
    A2 as UNCOUNTABLE_A2,
    A3 as UNCOUNTABLE_A3,
    A4 as UNCOUNTABLE_A4,
    A5 as UNCOUNTABLE_A5,
    A6 as UNCOUNTABLE_A6,
    A7 as UNCOUNTABLE_A7,
    A8 as UNCOUNTABLE_A8,
    A9 as UNCOUNTABLE_A9,
    A10 as UNCOUNTABLE_A10,
    B1 as UNCOUNTABLE_B1,
    B2 as UNCOUNTABLE_B2,
    B3 as UNCOUNTABLE_B3,
    B4 as UNCOUNTABLE_B4,
    B5 as UNCOUNTABLE_B5,
    C1 as UNCOUNTABLE_C1,
    C2 as UNCOUNTABLE_C2,
    AdicRepairInput,
    BooleanInput,
    CoverageFieldInput,
    CoverageInput,
    DenseTraceInput,
    DualRepairInput,
    OperationalInput,
    PowerSetInput,
    PrefixInput,
    SuperpositionInput,
    TrajectoryInput,
)


_UNCOUNTABLE_AXES = ((1, 0, 1), (0, 1, 0), (1, 1, 0))
_UNCOUNTABLE_PREFIX = PrefixInput((1, 0, 1, 1, 0, 1), 4)


def _uncountable_samples() -> dict[str, object]:
    return {
        str(UNCOUNTABLE_A1): TrajectoryInput((1, 0, 1, 1, 0, 1, 0, 1, 1)),
        str(UNCOUNTABLE_A2): PowerSetInput((0, 1, 0, 1, 1, 0)),
        str(UNCOUNTABLE_A3): DenseTraceInput(
            (1.25, -0.5, 2.0), (1, 0, 1, 0, 1)
        ),
        str(UNCOUNTABLE_A4): _UNCOUNTABLE_PREFIX,
        str(UNCOUNTABLE_A5): _UNCOUNTABLE_PREFIX,
        str(UNCOUNTABLE_A6): _UNCOUNTABLE_PREFIX,
        str(UNCOUNTABLE_A7): BooleanInput((1, 0, 1, 0), (0, 1, 1, 0)),
        str(UNCOUNTABLE_A8): OperationalInput(
            (1, 0, 1, 1), 2, ((1, 0),), (1,)
        ),
        str(UNCOUNTABLE_A9): CoverageInput(
            (1, -2, 0), _UNCOUNTABLE_AXES, (0.0, 0.0, 0.0)
        ),
        str(UNCOUNTABLE_A10): DualRepairInput((0, 1, 3, -1)),
        str(UNCOUNTABLE_B1): SuperpositionInput(
            (1, 0, 1, 1, 0), (0, 1, 1, 0, 1)
        ),
        str(UNCOUNTABLE_B2): _UNCOUNTABLE_PREFIX,
        str(UNCOUNTABLE_B3): _UNCOUNTABLE_PREFIX,
        str(UNCOUNTABLE_B4): OperationalInput(
            (1, 1, 0, 1), 2, ((0, 0),), (1,)
        ),
        str(UNCOUNTABLE_B5): AdicRepairInput(
            (1, -2, 0),
            ((1, 0, 1), (0, 1, 0), (1, 1, 1)),
            (0, 1, 3, -1),
        ),
        str(UNCOUNTABLE_C1): PrefixInput((1, 0, 1, 1, 0, 1, 1, 0), 5),
        str(UNCOUNTABLE_C2): CoverageFieldInput(
            (1, -2, 0),
            _UNCOUNTABLE_AXES,
            3,
            ((0, 0, 0),),
            (1,),
        ),
    }


def sample_inputs() -> dict[str, object]:
    result = {**_base_sample_inputs(), **_uncountable_samples()}
    if len(result) != 64:
        raise RuntimeError(f"expected 64 recertified samples, found {len(result)}")
    return result
