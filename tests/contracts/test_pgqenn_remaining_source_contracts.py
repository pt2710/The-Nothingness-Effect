"""Executable source-law gates for PGQENN A05--A10."""

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
    SOURCE_IDS,
    contracts,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts


def _input() -> PGQENNContractInput:
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


def test_pgqenn_native_registry_is_complete_ten_a_sources():
    identifiers = {str(contract.complex_id) for contract in all_contracts()}

    assert len(SOURCE_IDS) == 6
    assert set(map(str, SOURCE_IDS)).issubset(identifiers)
    assert len(contracts()) == 6


def test_pgqenn_remaining_source_laws_return_finite_graph_aligned_fields():
    value = _input()

    for contract in contracts():
        evaluation = contract.evaluate(value)
        output = evaluation.output

        assert output.response.shape == value.node_features.shape
        assert output.residual_field.shape == value.node_features.shape
        assert torch.isfinite(output.response).all()
        assert torch.isfinite(output.residual_field).all()
        assert np.isfinite(output.invariant_residual)
        assert evaluation.residual is not None


def test_pgqenn_exact_finite_identities_close_at_machine_precision():
    value = _input()
    by_id = {str(contract.complex_id): contract for contract in contracts()}

    annealing = by_id[
        "soi_scaled_annealing_invariance_soi_mis_scaling_spurious_entropy"
    ].evaluate(value)
    parseval = by_id[
        "weight_energy_parseval_equivalence_layerwise_l_2_energy_mismatch"
    ].evaluate(value)
    parity = by_id[
        "parity_orthogonal_optimization_cross_parity_gradient_contamination"
    ].evaluate(value)
    shell = by_id[
        "prime_shell_growth_regularity_shell_instability_phase_slips"
    ].evaluate(value)

    assert annealing.output.invariant_residual <= 1e-6
    assert parseval.output.invariant_residual <= 1e-5
    assert parity.output.invariant_residual <= 1e-6
    assert shell.output.invariant_residual <= 1e-6


def test_pgqenn_support_and_motif_certificates_depend_on_declared_graph():
    value = _input()
    support = contracts()[0].evaluate(value)
    motif = contracts()[2].evaluate(value)

    assert support.output.response.shape[0] == len(value.graph.primes)
    assert motif.output.response.shape[0] == len(value.graph.motifs)
    assert value.graph.growth_mode == "mpl_tc_prime_motif"
    assert value.graph.dependency_sha256
    assert torch.isfinite(support.output.residual_field).all()
    assert torch.isfinite(motif.output.residual_field).all()
