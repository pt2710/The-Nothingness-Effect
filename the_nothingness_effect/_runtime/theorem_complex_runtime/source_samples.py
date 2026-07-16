"""Deterministic finite provenance witnesses for recertified source laws."""

from __future__ import annotations

import numpy as np
import torch

from the_nothingness_effect.artificial_intelligence.pgqenn.contracts import (
    PGQENNContractInput,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.growth_law import (
    CanonicalPrimeGrowth,
)
from the_nothingness_effect.artificial_intelligence.pgqenn.source_contracts import (
    SOURCE_IDS as PGQENN_SOURCE_IDS,
)
from the_nothingness_effect.artificial_intelligence.qenn.contracts import (
    QENNContractInput,
)
from the_nothingness_effect.artificial_intelligence.qenn.source_contracts import (
    SOURCE_IDS as QENN_SOURCE_IDS,
)
from the_nothingness_effect.artificial_intelligence.soinets.contracts import (
    SOInetContractInput,
)
from the_nothingness_effect.artificial_intelligence.soinets.source_contracts import (
    SOURCE_IDS as SOINET_SOURCE_IDS,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import (
    normalized_dfi,
)
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.extended_contracts import (
    DFIDecompositionInput,
    DFIFlowpointInterfaceInput,
    DFISimulationInput,
)
from the_nothingness_effect.foundational_architecture.spatiality.canonical_contracts import (
    A1 as SPATIALITY_A1,
    A2 as SPATIALITY_A2,
    B1 as SPATIALITY_B1,
    B2 as SPATIALITY_B2,
    C1 as SPATIALITY_C1,
    OrbitClassificationInput,
    OrbitHarmonicInput,
    PhaseSpatialityInput,
    SpectralReconstructionInput,
    SquareRootLiftInput,
)
from the_nothingness_effect.foundational_architecture.symmetry.canonical_contracts import (
    A1 as SYMMETRY_A1,
    A2 as SYMMETRY_A2,
    B1 as SYMMETRY_B1,
    B2 as SYMMETRY_B2,
    C1 as SYMMETRY_C1,
    GeneratorWordInput,
    OrbitActionInput,
    ScheduleParityInput,
    ScheduleTransportInput,
    ScheduleWordFieldInput,
)


def _qenn_sample() -> QENNContractInput:
    axis = torch.linspace(0.0, 2.0 * torch.pi, 12)
    signal = torch.stack(
        (
            torch.sin(axis),
            torch.cos(axis),
            torch.sin(2.0 * axis),
            torch.cos(2.0 * axis),
            0.5 * torch.sin(axis),
            0.5 * torch.cos(axis),
        ),
        dim=-1,
    )
    return QENNContractInput(signal, tolerance=1e-6)


def _pgqenn_sample() -> PGQENNContractInput:
    graph = CanonicalPrimeGrowth().build(9)
    node = torch.arange(1.0, 10.0).unsqueeze(-1)
    features = torch.cat(
        (
            node / 10.0,
            torch.sin(node),
            torch.cos(node),
            torch.log1p(node),
            (node % 3.0) / 3.0,
        ),
        dim=-1,
    )
    return PGQENNContractInput(graph, features, tolerance=1e-6)


def _soinet_sample() -> SOInetContractInput:
    axis = torch.linspace(0.0, 2.0 * torch.pi, 8)
    base = torch.stack(
        (
            1.2 + torch.sin(axis),
            1.2 + torch.cos(axis),
            1.2 + torch.sin(2.0 * axis),
            1.2 + torch.cos(2.0 * axis),
        ),
        dim=-1,
    )
    modalities = torch.stack((base, 1.05 * base, torch.roll(base, 1, 0)))
    return SOInetContractInput(modalities, tolerance=1e-6)


def _dfi_samples() -> dict[str, object]:
    values = np.asarray(
        (
            (1.0, 2.0, 4.0),
            (2.0, 3.0, 5.0),
            (3.0, 5.0, 8.0),
        ),
        dtype=float,
    )
    components = np.asarray(
        normalized_dfi(values, spectrum_scale=1.0).normalized_entropy,
        dtype=float,
    )
    return {
        "dfi_uniqueness_of_decomposition_and_mapping_ambiguity": (
            DFIDecompositionInput(
                data=values,
                spectrum_scale=1.0,
                feature_permutation=(0, 1, 2),
                tolerance=1e-10,
            )
        ),
        "dfi_flowpoint_consistency_and_interface_inconsistency": (
            DFIFlowpointInterfaceInput(
                data=values,
                spectrum_scale=1.0,
                feature_involution=np.eye(values.shape[1]),
                tolerance=1e-10,
            )
        ),
        "dfi_simulation_consistency_and_simulation_breakdown": (
            DFISimulationInput(
                data=values,
                spectrum_scale=1.0,
                simulated_normalized_entropy=components,
                tolerance=1e-10,
            )
        ),
    }


def _symmetry_samples() -> dict[str, object]:
    tape = (1, 0, 1, 1)
    state = np.asarray((1.0, -2.0, 0.5), dtype=float)
    identity = np.eye(state.size)
    return {
        str(SYMMETRY_A1): ScheduleParityInput(tape, state),
        str(SYMMETRY_A2): OrbitActionInput(state),
        str(SYMMETRY_B1): ScheduleTransportInput(tape, state, 0, 2),
        str(SYMMETRY_B2): GeneratorWordInput(state, (1, 0, 0), identity),
        str(SYMMETRY_C1): ScheduleWordFieldInput(tape, state, identity),
    }


def _spatiality_samples() -> dict[str, object]:
    point = 1.0 + 2.0j
    order = 5
    indices = np.arange(order)
    samples = (
        np.exp(2j * np.pi * indices / order)
        + 0.2 * np.exp(4j * np.pi * indices / order)
    )
    return {
        str(SPATIALITY_A1): OrbitClassificationInput(point, order),
        str(SPATIALITY_A2): PhaseSpatialityInput(point, 0.7),
        str(SPATIALITY_B1): SquareRootLiftInput(point, order),
        str(SPATIALITY_B2): OrbitHarmonicInput(samples),
        str(SPATIALITY_C1): SpectralReconstructionInput(samples),
    }


def sample_inputs() -> dict[str, object]:
    """Return one deterministic typed witness for every promoted contract."""

    qenn = _qenn_sample()
    pgqenn = _pgqenn_sample()
    soinets = _soinet_sample()
    result = {
        **{str(identifier): qenn for identifier in QENN_SOURCE_IDS},
        **{str(identifier): pgqenn for identifier in PGQENN_SOURCE_IDS},
        **{str(identifier): soinets for identifier in SOINET_SOURCE_IDS},
        **_dfi_samples(),
        **_symmetry_samples(),
        **_spatiality_samples(),
    }
    if len(result) != 41:
        raise RuntimeError(f"expected 41 recertified samples, found {len(result)}")
    return result
