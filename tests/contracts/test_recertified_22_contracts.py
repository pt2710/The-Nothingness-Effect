"""Executable certification tests for the 22 corrected source contracts."""

from __future__ import annotations

import hashlib
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import ContractStatus
from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint import (
    TwoAdicUnificationInput,
    evaluate_2adic_dimensional_unification,
    evaluate_kernel_alternator,
)
from the_nothingness_effect.foundational_architecture.duality import KernelRecursionInput, evaluate_kernel_recursion
from the_nothingness_effect.foundational_architecture.symmetry import evaluate_order_two_symmetry_recursion
from the_nothingness_effect.foundational_architecture.spatiality import evaluate_affine_spatial_involution_orbit
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature import (
    CurvatureInput, EDIBridgeInput, EntropicStabilityInput, GeometryInput,
    evaluate_bridge_duality_and_2_adic_criterion, evaluate_edi_cross_complex_closure,
    evaluate_elastic_curvature_smoothness, evaluate_elastic_entropic_stability,
    evaluate_elastic_geometric_consistency,
)
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics import SymmetricCosmologyInput, evaluate_symmetric_cosmology_cross_complex_closure
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint import (
    AutocorrelationInput, DFITailInput, DriftInput, ElasticSupportInput,
    FigureClosureInput, FloquetRobustnessInput, MeyerInput, OUScatterInput,
    ReconstructionInput, WaveletRidgeInput,
    evaluate_autocorrelation_completeness, evaluate_dfi_compatible_tail_control,
    evaluate_drift_boundedness, evaluate_elastic_invariance_of_support,
    evaluate_figure_backed_closure, evaluate_floquet_free_robustness,
    evaluate_meyer_cut_and_project_structure, evaluate_ou_noise_5d_scatter,
    evaluate_reconstruction_equivalence, evaluate_wavelet_ridge_locking,
    evaluate_z2x2_sign_symmetry,
)


def test_foundational_contracts_and_boundaries():
    kernel = evaluate_kernel_alternator([1.0, 2.0], [3.0, 4.0])
    assert kernel.status is ContractStatus.EXACT
    assert np.allclose(kernel.value.diagonal_part[0] + kernel.value.kernel_part[0], [1.0, 2.0])
    assert evaluate_kernel_alternator([1.0], [2.0], characteristic=2).status is ContractStatus.INVALID_INPUT

    two_adic = evaluate_2adic_dimensional_unification(TwoAdicUnificationInput((0, 1), (1, 1), (0, 1), 2))
    assert two_adic.status is ContractStatus.EXACT and two_adic.value.commuting
    assert evaluate_2adic_dimensional_unification(TwoAdicUnificationInput((0,), (1,), (2,), 1)).status is ContractStatus.INVALID_INPUT

    recursion = evaluate_kernel_recursion(KernelRecursionInput(np.array([1.0, -1.0]), np.eye(2), 3, np.ones(2), 1e-12))
    assert recursion.status is ContractStatus.NUMERICAL_CANDIDATE
    broken = evaluate_kernel_recursion(KernelRecursionInput(np.array([1.0, 1.0]), np.diag([2.0, 1.0]), 2, np.ones(2), 1e-12))
    assert broken.status is ContractStatus.FALSIFIED

    symmetry = evaluate_order_two_symmetry_recursion([1.0, 2.0], [[0.0, 1.0], [1.0, 0.0]], np.eye(2))
    assert symmetry.status is ContractStatus.NUMERICAL_CANDIDATE
    affine = evaluate_affine_spatial_involution_orbit([2.0, 1.0], [0.0, 0.0], [[-1.0, 0.0], [0.0, 1.0]])
    assert affine.status is ContractStatus.EXACT and np.allclose(affine.value.return_image, [2.0, 1.0])


def _edi_sources():
    bridge = evaluate_bridge_duality_and_2_adic_criterion(EDIBridgeInput(np.array([[0.0], [1.0], [2.0]]), np.ones(3), np.ones(3), True))
    x = np.linspace(-1.0, 1.0, 9)
    curvature = evaluate_elastic_curvature_smoothness(CurvatureInput(x**2, x[1] - x[0], True))
    stability = evaluate_elastic_entropic_stability(EntropicStabilityInput(-np.eye(2), np.eye(2), np.eye(2), 1.0))
    geometry = evaluate_elastic_geometric_consistency(GeometryInput(np.stack([np.eye(2), np.eye(2)]), np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0, 1]]), True))
    return bridge, curvature, stability, geometry


def test_edi_sources_and_positive_definite_meta_closure():
    sources = _edi_sources()
    assert all(item.accepted_candidate for item in sources)
    meta = evaluate_edi_cross_complex_closure(sources)
    assert meta.status is ContractStatus.NUMERICAL_CANDIDATE
    assert len(meta.value.source_necessity) == 4
    assert evaluate_elastic_curvature_smoothness(CurvatureInput(np.arange(5.0), 1.0, atomic_mass=1.0)).status is ContractStatus.FALSIFIED
    unobservable = evaluate_elastic_entropic_stability(EntropicStabilityInput(np.eye(2), np.zeros((1, 2)), np.zeros((2, 1)), 1.0))
    assert unobservable.status is ContractStatus.UNDECIDED


def test_spatial_cosmology_requires_every_source_and_boundary_closure():
    x = np.linspace(-1.0, 1.0, 5); fields = (x, x**2 + 1.0)
    result = evaluate_symmetric_cosmology_cross_complex_closure(SymmetricCosmologyInput(x, fields, ("a", "b"), np.eye(5), np.zeros(5, dtype=bool), 3.0))
    assert result.status is ContractStatus.NUMERICAL_CANDIDATE
    assert all(item > 0.0 for item in result.value.source_removal_residuals)


def test_dtqc_structure_support_and_noise_contracts():
    meyer = evaluate_meyer_cut_and_project_structure(MeyerInput(np.arange(6.0), np.linspace(-1, 1, 6), (-1, 1), 2, True))
    assert meyer.status is ContractStatus.EXACT
    diffuse = evaluate_meyer_cut_and_project_structure(MeyerInput(np.arange(6.0), np.linspace(-1, 1, 6), (-1, 1), 2, True, 0.2))
    assert diffuse.status is ContractStatus.FALSIFIED
    sectors = evaluate_z2x2_sign_symmetry(np.arange(16.0).reshape(4, 4))
    assert sectors.status is ContractStatus.EXACT and np.allclose(sum(sectors.value.sectors), np.arange(16.0).reshape(4, 4))
    support = evaluate_elastic_invariance_of_support(ElasticSupportInput(np.array([1.0, 0.0, 2.0]), np.array([True, False, True]), 2.0))
    assert support.status is ContractStatus.NUMERICAL_CANDIDATE
    ou = evaluate_ou_noise_5d_scatter(OUScatterInput(np.linspace(0, 1, 8), 0.5, 0.1, 0.1, np.ones((5, 8)), 7, 4))
    assert ou.status is ContractStatus.NUMERICAL_CANDIDATE and ou.value.features_5d.shape == (4, 5)


def test_dtqc_limit_reconstruction_and_wavelet_contracts():
    auto = evaluate_autocorrelation_completeness(AutocorrelationInput(1.0, 0.0, 0.0, 0.0, True))
    assert auto.status is ContractStatus.EXACT
    mixed = evaluate_autocorrelation_completeness(AutocorrelationInput(1.0, 0.1, 0.0, 0.0, True))
    assert mixed.status is ContractStatus.FALSIFIED
    reconstruction = evaluate_reconstruction_equivalence(ReconstructionInput(np.eye(3), np.eye(3), np.arange(3.0), "l2", True))
    assert reconstruction.status is ContractStatus.NUMERICAL_CANDIDATE
    coeff = np.zeros((3, 4)); coeff[1, :] = 1.0
    ridge = evaluate_wavelet_ridge_locking(WaveletRidgeInput(coeff, np.array([1.0, 2.0, 3.0]), np.ones_like(coeff, dtype=bool), np.full(4, 2.0), 0.1, True))
    assert ridge.status is ContractStatus.NUMERICAL_CANDIDATE


def test_dtqc_robustness_drift_tail_and_figure_evidence():
    robustness = evaluate_floquet_free_robustness(FloquetRobustnessInput(np.array([0.2, 0.3]), np.array([[0.1, 0.2], [0.2, 0.2]]), True, True, "seeded Gaussian ensemble"))
    assert robustness.status is ContractStatus.NUMERICAL_CANDIDATE
    drift = evaluate_drift_boundedness(DriftInput(np.ones(6), np.arange(6.0), "affine"))
    assert drift.status is ContractStatus.EXACT
    tail = evaluate_dfi_compatible_tail_control(DFITailInput(np.array([1.0, 1.0, 0.0, 0.0]), np.ones(4), np.array([True, True, False, False]), (2, 4), True))
    assert tail.status is ContractStatus.NUMERICAL_CANDIDATE
    digest = hashlib.sha256(b"figure").hexdigest()
    figure = evaluate_figure_backed_closure(FigureClosureInput(np.zeros((4, 2)), np.arange(4.0), np.zeros(3), (digest,), {"window": 4}, 0, True))
    assert figure.status is ContractStatus.NUMERICAL_CANDIDATE
    assert figure.provenance["claim_boundary"].startswith("finite computational support")


def test_nonfinite_input_is_never_masked():
    assert evaluate_kernel_alternator([np.nan], [0.0]).status is ContractStatus.INVALID_INPUT
    invalid = evaluate_autocorrelation_completeness(AutocorrelationInput(np.inf, 0.0, 0.0, 0.0, True))
    assert invalid.status is ContractStatus.INVALID_INPUT

