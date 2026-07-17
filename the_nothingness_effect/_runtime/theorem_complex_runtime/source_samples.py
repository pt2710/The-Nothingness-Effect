"""Deterministic provenance witnesses with Spectrum, Elastic-Dubler, and Locality extensions."""

from __future__ import annotations

import numpy as np

from ._source_samples_uncountable_impl import *  # noqa: F401,F403
from ._source_samples_uncountable_impl import sample_inputs as _base_sample_inputs
from ._source_samples_elastic_dubler import sample_inputs as _elastic_dubler_samples
from ._source_samples_locality_gravity import sample_inputs as _locality_gravity_samples

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
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.canonical_contracts import (
    A1 as SOI_A1,
    A2 as SOI_A2,
    A3 as SOI_A3,
    A4 as SOI_A4,
    A5 as SOI_A5,
    A6 as SOI_A6,
    A7 as SOI_A7,
    A8 as SOI_A8,
    A9 as SOI_A9,
    A10 as SOI_A10,
    B1 as SOI_B1,
    B2 as SOI_B2,
    B3 as SOI_B3,
    C1 as SOI_C1,
    C2 as SOI_C2,
    C3 as SOI_C3,
    AddressInput,
    CosmicLedgerInput,
    DFIInput,
    DecompositionInput,
    DualRealizabilityInput,
    ElasticProbeInput,
    EntropyInput,
    FactorMapInput,
    FinitizationInput,
    HistoryAccessibilityInput,
    LpInput,
    MeasurableScopeInput,
    MeasureTransferInput,
    MetricDeformationInput,
    NormalizationInput,
    ObservableLocalityInput,
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
    horizon_temporal = np.asarray(
        ((1.0, 0.5, 0.0, 0.0), (0.5, 0.25, 0.0, 0.0))
    )
    horizon_spectral = np.asarray(
        ((0.5, 0.25, 0.0, 0.0), (0.25, 0.125, 0.0, 0.0))
    )
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


def _spectrum_samples() -> dict[str, object]:
    identity_2 = np.eye(2)
    identity_3 = np.eye(3)
    histories = np.asarray(((0, 0), (0, 1), (1, 0), (1, 1)), dtype=int)
    addresses = np.asarray((0.0, 0.25, 0.5, 0.75))
    schedules = histories.copy()
    initial_bits = np.zeros(4, dtype=int)
    expected_histories = np.asarray(
        tuple(
            tuple(
                [0]
                + [
                    int(np.bitwise_xor.reduce(schedule[: index + 1]))
                    for index in range(schedule.size)
                ]
            )
            for schedule in schedules
        ),
        dtype=int,
    )
    projector_middle = np.diag((0.0, 1.0, 0.0))
    return {
        str(SOI_A1): NormalizationInput(np.asarray((1.0, 1.0)), 2.0),
        str(SOI_A2): DFIInput(np.asarray((1.0, 2.0, 4.0)), 3.0),
        str(SOI_A3): DecompositionInput(np.asarray((1.0, 2.0)), np.eye(2)),
        str(SOI_A4): LpInput(np.asarray((3.0, 4.0)), 4.0, 2.0),
        str(SOI_A5): EntropyInput(np.asarray((0.5, 0.5)), 2.0),
        str(SOI_A6): FinitizationInput(
            np.asarray((1.0, 2.0)),
            np.asarray(((0.0, 0.0), (0.5, 1.0), (1.0, 2.0))),
        ),
        str(SOI_A7): DualRealizabilityInput(identity_2, np.asarray((1.0, 2.0))),
        str(SOI_A8): MeasureTransferInput(
            np.asarray((0.5, 0.5)),
            np.asarray((0, 1)),
            np.asarray((0.5, 0.5)),
            2.0,
        ),
        str(SOI_A9): MeasurableScopeInput(
            np.asarray((1.0, 2.0)),
            np.asarray((True, True)),
            np.asarray((True, True)),
        ),
        str(SOI_A10): FactorMapInput(
            identity_2,
            identity_2,
            identity_2,
            np.asarray((1.0, 2.0)),
        ),
        str(SOI_B1): AddressInput(
            histories,
            addresses,
            np.full(4, 0.25),
            4.0,
        ),
        str(SOI_B2): MetricDeformationInput(
            np.asarray(((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),
            identity_2,
            np.full(3, 1.0 / 3.0),
            np.asarray((1.0, 2.0, 3.0)),
            identity_3,
        ),
        str(SOI_B3): HistoryAccessibilityInput(
            initial_bits,
            schedules,
            expected_histories,
            4.0,
        ),
        str(SOI_C1): CosmicLedgerInput(
            addresses,
            histories,
            np.zeros((4, 1)),
        ),
        str(SOI_C2): ObservableLocalityInput(
            np.asarray((0.0, 1.0, 0.0)),
            np.asarray((0.0, 1.0, 0.0)),
            identity_3,
        ),
        str(SOI_C3): ElasticProbeInput(
            np.zeros(3),
            projector_middle,
            projector_middle,
            1.0,
        ),
    }


def sample_inputs() -> dict[str, object]:
    result = {
        **_base_sample_inputs(),
        **_observation_samples(),
        **_spectrum_samples(),
        **_elastic_dubler_samples(),
        **_locality_gravity_samples(),
    }
    if len(result) != 134:
        raise RuntimeError(f"expected 134 recertified samples, found {len(result)}")
    return result
