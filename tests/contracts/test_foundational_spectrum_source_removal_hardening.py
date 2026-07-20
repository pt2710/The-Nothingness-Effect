"""Hardening checks for Spectrum source-removal certificate recomputation."""

from __future__ import annotations

import numpy as np

from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.canonical_contracts import (
    B1,
    B2,
    B3,
    C1,
    C2,
    C3,
    AddressInput,
    CosmicLedgerInput,
    ElasticProbeInput,
    HistoryAccessibilityInput,
    MetricDeformationInput,
    ObservableLocalityInput,
)
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.hardened_contracts import (
    contracts,
)


def _derived_samples() -> dict[str, object]:
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
        str(B1): AddressInput(
            histories,
            addresses,
            np.full(4, 0.25),
            4.0,
        ),
        str(B2): MetricDeformationInput(
            np.asarray(((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),
            identity_2,
            np.full(3, 1.0 / 3.0),
            np.asarray((1.0, 2.0, 3.0)),
            identity_3,
        ),
        str(B3): HistoryAccessibilityInput(
            initial_bits,
            schedules,
            expected_histories,
            4.0,
        ),
        str(C1): CosmicLedgerInput(
            addresses,
            histories,
            np.zeros((4, 1)),
        ),
        str(C2): ObservableLocalityInput(
            np.asarray((0.0, 1.0, 0.0)),
            np.asarray((0.0, 1.0, 0.0)),
            identity_3,
        ),
        str(C3): ElasticProbeInput(
            np.zeros(3),
            projector_middle,
            projector_middle,
            1.0,
        ),
    }


def test_hardened_ablation_recomputes_nonzero_surviving_certificates():
    samples = _derived_samples()
    for contract in contracts()[10:]:
        value = samples[str(contract.complex_id)]
        removals = tuple(check(value) for check in contract.source_removal_checks)
        assert len(removals) == len(contract.source_ids)
        assert {item.source_id for item in removals} == set(contract.source_ids)
        assert all(item.necessary for item in removals)
        assert all(item.necessity_residual > 0.0 for item in removals)
        assert all(item.removed_response > 0.0 for item in removals)
        assert all(item.removed_response < item.baseline_response for item in removals)
