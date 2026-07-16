"""Remaining appendix-derived QENN B and C contracts."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    additive_contract,
    spatial_contract,
)


APPENDIX = "appendix_tne_artificial_intelligence_architechture.tex"
APPENDIX_SHA256 = "3a75d4bfdbf9779255d01dd3ae3db6a848a4dc1fa67455ca1f22d5abcadf866a"
IMPLEMENTATION = "the_nothingness_effect/artificial_intelligence/qenn/derived_contracts.py"

B_SPECS = (
    (
        "parity_resolved_autocorrelation_operator",
        (
            "autocorrelation_completeness_of_weight_trajectories_continuous_mixing_component",
            "flowpoint_flip_parity_constraint_parity_broken_bias_spurious_lines",
        ),
    ),
    (
        "support_transport_drift_certificate",
        (
            "qenn::dual_support_equivalence_support_mismatch_leakage",
            "bounded_remainder_drift_in_updates_long_memory_heavy_tail_drift",
        ),
    ),
    (
        "epoch_support_commutator_closure",
        (
            "inflation_collapse_support_invariance_nonlinear_sideband_mixing",
            "epoch_operator_closure_backprop_optimiser_induced_resonance",
        ),
    ),
    (
        "entropic_hyperparameter_stability_margin",
        (
            "entropy_balanced_landscape_no_sharp_minima_sharp_minima_trap",
            "hyper_parameter_stability_wedge_instability_lobe",
        ),
    ),
)

C_SPECS = (
    (
        "parity_support_memory_field_closure",
        ("parity_resolved_autocorrelation_operator", "support_transport_drift_certificate"),
    ),
    (
        "optimizer_stability_wedge_spatial_closure",
        ("epoch_support_commutator_closure", "entropic_hyperparameter_stability_margin"),
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
