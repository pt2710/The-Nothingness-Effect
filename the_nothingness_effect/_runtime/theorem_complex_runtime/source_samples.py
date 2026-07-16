"""Deterministic provenance witnesses with Observation-and-Collapse extension."""

from __future__ import annotations

import numpy as np

from ._source_samples_uncountable_impl import *  # noqa: F401,F403
from ._source_samples_uncountable_impl import sample_inputs as _base_sample_inputs

from the_nothingness_effect.foundational_architecture.observation_and_collapse.canonical_contracts import (
    A1 as OBS_A1,
    A2 as OBS_A2,
    A3 as OBS_A3,
    A4 as OBS_A4,
    A5 as OBS_A5,
    A6 as OBS_A6,
    A7 as OBS_A7,
    A8 as OBS_A8,
    B1 as OBS_B1,
    B2 as OBS_B2,
    B3 as OBS_B3,
    B4 as OBS_B4,
    C1 as OBS_C1,
    C2 as OBS_C2,
    C3 as OBS_C3,
    C4 as OBS_C4,
    AttractorInput,
    ClosureInput,
    DimensionalBindingInput,
    HorizonInput,
    InstrumentInput,
    LocalityInput,
    MeanErgodicInput,
    OutcomeClosureInput,
    OutcomeFieldInput,
    SpectralCollapseInput,
    StabilizationInput,
    TemporalCompressionInput,
    UniquenessInput,
)


def _observation_samples() -> dict[str, object]:
    identity = np.eye(2)
    involution = np.diag((1.0, -1.0))
    fixed_state = np.asarray((1.0, 0.0))
    mixed_state = np.asarray((1.0, 1.0)) / np.sqrt(2.0)
    p0 = np.diag((1.0, 0.0))
    p1 = np.diag((0.0, 1.0))
    projectors = (p0, p1)
    relation = np.asarray(((1, 1), (0, 1)), dtype=int)
    constant_history = np.asarray(
        (
            ((1.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)),
            ((1.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)),
        ),
        dtype=float,
    )
    horizon_temporal = np.asarray(((1.0, 0.5, 0.0, 0.0), (0.5, 0.25, 0.0, 0.0)))
    horizon_spectral = np.asarray(((0.5, 0.25, 0.0, 0.0), (0.25, 0.125, 0.0, 0.0)))
    return {
        str(OBS_A1): MeanErgodicInput(identity, fixed_state, 8),
        str(OBS_A2): AttractorInput(
            fixed_state,
            np.asarray(((0.25, -0.25), (-0.25, 0.25))),
        ),
        str(OBS_A3): UniquenessInput(constant_history),
        str(OBS_A4): MeanErgodicInput(involution, mixed_state, 8),
        str(OBS_A5): ClosureInput(
            relation,
            np.asarray((1, 0)),
            np.asarray((1, 1)),
        ),
        str(OBS_A6): StabilizationInput((0, 0, 2), (0, 1, 2)),
        str(OBS_A7): InstrumentInput(projectors, mixed_state),
        str(OBS_A8): MeanErgodicInput(involution, mixed_state, 8),
        str(OBS_B1): OutcomeClosureInput(
            relation,
            np.asarray((0, 0)),
            projectors,
            mixed_state,
            0,
        ),
        str(OBS_B2): SpectralCollapseInput(involution, mixed_state, 8),
        str(OBS_B3): TemporalCompressionInput(constant_history),
        str(OBS_B4): SpectralCollapseInput(involution, mixed_state, 8),
        str(OBS_C1): DimensionalBindingInput(p0, p0, mixed_state),
        str(OBS_C2): LocalityInput(fixed_state, fixed_state, p0),
        str(OBS_C3): HorizonInput(horizon_temporal, horizon_spectral, 0.0),
        str(OBS_C4): OutcomeFieldInput(
            relation,
            np.asarray((0, 0)),
            projectors,
            p0,
            fixed_state,
        ),
    }


def sample_inputs() -> dict[str, object]:
    result = {**_base_sample_inputs(), **_observation_samples()}
    if len(result) != 80:
        raise RuntimeError(f"expected 80 recertified samples, found {len(result)}")
    return result
