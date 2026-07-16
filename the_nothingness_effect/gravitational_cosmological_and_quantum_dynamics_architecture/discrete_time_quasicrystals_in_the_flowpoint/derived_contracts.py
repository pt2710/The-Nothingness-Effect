"""Genuine appendix-derived DTQC additive certificates and spatial closures."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    additive_contract,
    spatial_contract,
)


APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
IMPLEMENTATION = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "discrete_time_quasicrystals_in_the_flowpoint/derived_contracts.py"
)

B_SPECS = (
    (
        "parity_meyer_diffraction_decomposition",
        (
            "meyer_cut_and_project_structure_non_meyer_diffuse_support",
            "z_2_2_sign_symmetry_parity_bias_symmetry_breaking",
        ),
    ),
    (
        "elastic_gain_ou_support_margin",
        (
            "elastic_invariance_of_support_nonlinear_leakage",
            "ou_noise_5_d_scatter_robustness_noise_induced_smearing",
        ),
    ),
    (
        "autocorrelation_reconstruction_projector",
        (
            "autocorrelation_completeness_mixed_autocorrelation",
            "algebraic_analytic_reconstruction_equivalence_non_invertible_reconstruction",
        ),
    ),
    (
        "ridge_resolved_2_adic_robustness_certificate",
        (
            "wavelet_ridge_locking_ridge_drift_shear",
            "floquet_free_robustness_dual_2_adic_criterionicity_disorder_reliant_stability",
        ),
    ),
    (
        "drift_tail_figure_certification_functional",
        (
            "drift_boundedness_criterion_unbounded_drift_breakdown",
            "dfi_compatible_tail_control_tail_driven_mass_imbalance",
            "figure_backed_closure_bragg_cwt_figure_contradicted_claims",
        ),
    ),
)

C_SPECS = (
    (
        "parity_meyer_noise_stable_diffraction_closure",
        ("parity_meyer_diffraction_decomposition", "elastic_gain_ou_support_margin"),
    ),
    (
        "certified_multiscale_dtqc_reconstruction_closure",
        (
            "autocorrelation_reconstruction_projector",
            "ridge_resolved_2_adic_robustness_certificate",
            "drift_tail_figure_certification_functional",
        ),
    ),
)


def contracts():
    return tuple(
        additive_contract(
            complex_id,
            source_ids,
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        )
        for complex_id, source_ids in B_SPECS
    ) + tuple(
        spatial_contract(
            complex_id,
            source_ids,
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        )
        for complex_id, source_ids in C_SPECS
    )
