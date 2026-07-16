"""Canonical registry adapters for the 22 recertified A source contracts."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
import hashlib
from pathlib import Path
from typing import Callable

import numpy as np

from .contract_protocol import ContractResult, ContractStatus
from .types import (
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)


FOUNDATIONAL = "appendix_tne_foundational_closure_architecture.tex"
FOUNDATIONAL_SHA256 = "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea"
GRAVITATIONAL = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
GRAVITATIONAL_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
FIGURE_FIXTURE = "docs/figures/figure_provenance_fixture.svg"


@dataclass(frozen=True)
class PositionalContractInput:
    args: tuple[object, ...]
    kwargs: dict[str, object] | None = None


def _call_positional(function: Callable, value: PositionalContractInput) -> ContractResult:
    return function(*value.args, **(value.kwargs or {}))


def _residual(identifier: str, _source, result: ContractResult) -> ResidualResult:
    vector = tuple(float(value) for value in result.residuals.values()) or (0.0,)
    tolerance = max(
        (float(value) for value in result.tolerances.values()),
        default=0.0,
    )
    passed = result.status in {
        ContractStatus.EXACT,
        ContractStatus.NUMERICAL_CANDIDATE,
    }
    status = (
        ClosureStatus.SATISFIED
        if passed
        else ClosureStatus.INVALID_DOMAIN
        if result.status is ContractStatus.INVALID_INPUT
        else ClosureStatus.OPEN
    )
    return ResidualResult(
        identifier,
        vector,
        tolerance,
        passed,
        status,
        {
            "contract_status": result.status.value,
            "reason_code": result.reason_code,
        },
    )


def contracts() -> tuple[ComplexContract, ...]:
    from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.recertified_contracts import (
        evaluate_2adic_dimensional_unification,
        evaluate_kernel_alternator,
    )
    from the_nothingness_effect.foundational_architecture.duality.recertified_contracts import (
        evaluate_kernel_recursion,
    )
    from the_nothingness_effect.foundational_architecture.symmetry.recertified_contracts import (
        evaluate_order_two_symmetry_recursion,
    )
    from the_nothingness_effect.foundational_architecture.spatiality.recertified_contracts import (
        evaluate_affine_spatial_involution_orbit,
    )
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.recertified_contracts import (
        evaluate_bridge_duality_and_2_adic_criterion,
        evaluate_edi_cross_complex_closure,
        evaluate_elastic_curvature_smoothness,
        evaluate_elastic_entropic_stability,
        evaluate_elastic_geometric_consistency,
    )
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics.recertified_contracts import (
        evaluate_symmetric_cosmology_cross_complex_closure,
    )
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.figure_provenance import (
        evaluate_figure_backed_closure,
    )
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.recertified_contracts import (
        evaluate_autocorrelation_completeness,
        evaluate_dfi_compatible_tail_control,
        evaluate_drift_boundedness,
        evaluate_elastic_invariance_of_support,
        evaluate_floquet_free_robustness,
        evaluate_meyer_cut_and_project_structure,
        evaluate_ou_noise_5d_scatter,
        evaluate_reconstruction_equivalence,
        evaluate_wavelet_ridge_locking,
        evaluate_z2x2_sign_symmetry,
    )

    definitions = (
        ("kernel_alternator", FOUNDATIONAL, FOUNDATIONAL_SHA256, evaluate_kernel_alternator, True, "canonical_self_negating_involution/the_flowpoint"),
        ("necessity_and_sufficiency_of_2_adic_mirror_history_coding_and_coordinatewise_reflection_closure_nece", FOUNDATIONAL, FOUNDATIONAL_SHA256, evaluate_2adic_dimensional_unification, False, "canonical_self_negating_involution/the_flowpoint"),
        ("kernel_recursion", FOUNDATIONAL, FOUNDATIONAL_SHA256, evaluate_kernel_recursion, False, "foundational_architecture/duality"),
        ("order_two_symmetry_recursion", FOUNDATIONAL, FOUNDATIONAL_SHA256, evaluate_order_two_symmetry_recursion, True, "foundational_architecture/symmetry"),
        ("affine_spatial_involution_orbit", FOUNDATIONAL, FOUNDATIONAL_SHA256, evaluate_affine_spatial_involution_orbit, True, "foundational_architecture/spatiality"),
        ("bridge_duality_and_the_2_adic_criterion", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_bridge_duality_and_2_adic_criterion, False, "gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature"),
        ("elastic_curvature_smoothness_curvature_singularity", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_elastic_curvature_smoothness, False, "gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature"),
        ("elastic_entropic_stability_entropic_instability", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_elastic_entropic_stability, False, "gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature"),
        ("elastic_geometric_consistency_geometric_degeneracy", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_elastic_geometric_consistency, False, "gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature"),
        ("appendix_wide_edi_cross_complex_closure_and_computational_falsification_interface", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_edi_cross_complex_closure, False, "gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature"),
        ("appendix_wide_symmetric_cosmology_cross_complex_closure_and_computational_falsification_interface", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_symmetric_cosmology_cross_complex_closure, False, "gravitational_cosmological_and_quantum_dynamics_architecture/emergent_cosmological_spark_dynamics"),
        ("meyer_cut_and_project_structure_non_meyer_diffuse_support", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_meyer_cut_and_project_structure, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("z_2_2_sign_symmetry_parity_bias_symmetry_breaking", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_z2x2_sign_symmetry, True, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("elastic_invariance_of_support_nonlinear_leakage", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_elastic_invariance_of_support, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("ou_noise_5_d_scatter_robustness_noise_induced_smearing", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_ou_noise_5d_scatter, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("autocorrelation_completeness_mixed_autocorrelation", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_autocorrelation_completeness, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("algebraic_analytic_reconstruction_equivalence_non_invertible_reconstruction", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_reconstruction_equivalence, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("wavelet_ridge_locking_ridge_drift_shear", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_wavelet_ridge_locking, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("floquet_free_robustness_dual_2_adic_criterionicity_disorder_reliant_stability", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_floquet_free_robustness, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("drift_boundedness_criterion_unbounded_drift_breakdown", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_drift_boundedness, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("dfi_compatible_tail_control_tail_driven_mass_imbalance", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_dfi_compatible_tail_control, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
        ("figure_backed_closure_bragg_cwt_figure_contradicted_claims", GRAVITATIONAL, GRAVITATIONAL_SHA256, evaluate_figure_backed_closure, False, "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint"),
    )
    result = []
    for identifier, appendix, digest, function, positional, module in definitions:
        operator = partial(_call_positional, function) if positional else function
        input_types = (PositionalContractInput,) if positional else (object,)
        result.append(
            ComplexContract(
                ComplexId(identifier),
                appendix,
                digest,
                ComplexLevel.A,
                (),
                DomainSpec(
                    f"{identifier} input",
                    "typed recertified source-law input",
                    input_types,
                ),
                CodomainSpec(
                    f"{identifier} result",
                    "fail-closed typed contract result",
                    (ContractResult,),
                ),
                operator,
                residual=partial(_residual, identifier),
                exact_semantics=False,
                implementation_path=f"the_nothingness_effect/{module}/recertified_contracts.py",
            )
        )
    return tuple(result)


def sample_inputs() -> dict[str, object]:
    """Deterministic finite witnesses used only for artifact smoke evidence."""

    from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.recertified_contracts import TwoAdicUnificationInput
    from the_nothingness_effect.foundational_architecture.duality.recertified_contracts import KernelRecursionInput
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.recertified_contracts import CurvatureInput, EDIBridgeInput, EntropicStabilityInput, GeometryInput, evaluate_bridge_duality_and_2_adic_criterion, evaluate_elastic_curvature_smoothness, evaluate_elastic_entropic_stability, evaluate_elastic_geometric_consistency
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics.recertified_contracts import SymmetricCosmologyInput
    from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.recertified_contracts import AutocorrelationInput, DFITailInput, DriftInput, ElasticSupportInput, FigureClosureInput, FloquetRobustnessInput, MeyerInput, OUScatterInput, ReconstructionInput, WaveletRidgeInput

    x = np.linspace(-1.0, 1.0, 9)
    edi = (
        evaluate_bridge_duality_and_2_adic_criterion(EDIBridgeInput(np.array([[0.0], [1.0], [2.0]]), np.ones(3), np.ones(3), True)),
        evaluate_elastic_curvature_smoothness(CurvatureInput(x**2, x[1] - x[0], True)),
        evaluate_elastic_entropic_stability(EntropicStabilityInput(-np.eye(2), np.eye(2), np.eye(2), 1.0)),
        evaluate_elastic_geometric_consistency(GeometryInput(np.stack([np.eye(2), np.eye(2)]), np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0, 1]]), True)),
    )
    wavelet = np.zeros((3, 4))
    wavelet[1, :] = 1.0
    figure_hash = hashlib.sha256((REPOSITORY_ROOT / FIGURE_FIXTURE).read_bytes()).hexdigest()
    return {
        "kernel_alternator": PositionalContractInput(([1.0, 2.0], [3.0, 4.0])),
        "necessity_and_sufficiency_of_2_adic_mirror_history_coding_and_coordinatewise_reflection_closure_nece": TwoAdicUnificationInput((0, 1), (1, 1), (0, 1), 2),
        "kernel_recursion": KernelRecursionInput(np.array([1.0, -1.0]), np.eye(2), 3, np.ones(2), 1e-12),
        "order_two_symmetry_recursion": PositionalContractInput(([1.0, 2.0], [[0.0, 1.0], [1.0, 0.0]], np.eye(2))),
        "affine_spatial_involution_orbit": PositionalContractInput(([2.0, 1.0], [0.0, 0.0], [[-1.0, 0.0], [0.0, 1.0]])),
        "bridge_duality_and_the_2_adic_criterion": EDIBridgeInput(np.array([[0.0], [1.0], [2.0]]), np.ones(3), np.ones(3), True),
        "elastic_curvature_smoothness_curvature_singularity": CurvatureInput(x**2, x[1] - x[0], True),
        "elastic_entropic_stability_entropic_instability": EntropicStabilityInput(-np.eye(2), np.eye(2), np.eye(2), 1.0),
        "elastic_geometric_consistency_geometric_degeneracy": GeometryInput(np.stack([np.eye(2), np.eye(2)]), np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0, 1]]), True),
        "appendix_wide_edi_cross_complex_closure_and_computational_falsification_interface": edi,
        "appendix_wide_symmetric_cosmology_cross_complex_closure_and_computational_falsification_interface": SymmetricCosmologyInput(np.linspace(-1, 1, 5), (np.linspace(-1, 1, 5), np.linspace(-1, 1, 5) ** 2 + 1), ("a", "b"), np.eye(5), np.zeros(5, dtype=bool), 3.0),
        "meyer_cut_and_project_structure_non_meyer_diffuse_support": MeyerInput(np.arange(6.0), np.linspace(-1, 1, 6), (-1, 1), 2, True),
        "z_2_2_sign_symmetry_parity_bias_symmetry_breaking": PositionalContractInput((np.arange(16.0).reshape(4, 4),)),
        "elastic_invariance_of_support_nonlinear_leakage": ElasticSupportInput(np.array([1.0, 0.0, 2.0]), np.array([True, False, True]), 2.0),
        "ou_noise_5_d_scatter_robustness_noise_induced_smearing": OUScatterInput(np.linspace(0, 1, 8), 0.5, 0.1, 0.1, np.ones((5, 8)), 7, 4),
        "autocorrelation_completeness_mixed_autocorrelation": AutocorrelationInput(1.0, 0.0, 0.0, 0.0, True),
        "algebraic_analytic_reconstruction_equivalence_non_invertible_reconstruction": ReconstructionInput(np.eye(3), np.eye(3), np.arange(3.0), "l2", True),
        "wavelet_ridge_locking_ridge_drift_shear": WaveletRidgeInput(wavelet, np.array([1.0, 2.0, 3.0]), np.ones_like(wavelet, dtype=bool), np.full(4, 2.0), 0.1, True),
        "floquet_free_robustness_dual_2_adic_criterionicity_disorder_reliant_stability": FloquetRobustnessInput(np.array([0.2, 0.3]), np.array([[0.1, 0.2], [0.2, 0.2]]), True, True, "seeded Gaussian ensemble"),
        "drift_boundedness_criterion_unbounded_drift_breakdown": DriftInput(np.ones(6), np.arange(6.0), "affine"),
        "dfi_compatible_tail_control_tail_driven_mass_imbalance": DFITailInput(np.array([1.0, 1.0, 0.0, 0.0]), np.ones(4), np.array([True, True, False, False]), (2, 4), True),
        "figure_backed_closure_bragg_cwt_figure_contradicted_claims": FigureClosureInput(
            np.zeros((4, 2)),
            np.arange(4.0),
            np.zeros(3),
            (figure_hash,),
            {"window": 4, "generated_files": [FIGURE_FIXTURE]},
            0,
            True,
        ),
    }
