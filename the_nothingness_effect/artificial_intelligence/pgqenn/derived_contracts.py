"""Remaining appendix-derived PGQENN B and C contracts."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    additive_contract,
    spatial_contract,
)


APPENDIX = "appendix_tne_artificial_intelligence_architechture.tex"
APPENDIX_SHA256 = "2f2e67b68c18c75f8fe0e8f78c243ca585c0ef8413c579752c3299816e5bc8de"
IMPLEMENTATION = "the_nothingness_effect/artificial_intelligence/pgqenn/derived_contracts.py"

B_SPECS = (
    (
        "quasicrystal_soi_annealing_transport",
        (
            "prime_quasicrystal_support_equivalence_support_mismatch_leakage",
            "soi_scaled_annealing_invariance_soi_mis_scaling_spurious_entropy",
        ),
    ),
    (
        "exhaustion_parseval_coverage_energy",
        (
            "motif_exhaustion_completeness_coverage_bias_long_memory_drift",
            "weight_energy_parseval_equivalence_layerwise_l_2_energy_mismatch",
        ),
    ),
    (
        "parity_orthogonal_shell_growth_connection",
        (
            "parity_orthogonal_optimization_cross_parity_gradient_contamination",
            "prime_shell_growth_regularity_shell_instability_phase_slips",
        ),
    ),
)

C_SPECS = (
    (
        "multiscale_prime_shell_training_closure",
        (
            "quasicrystal_soi_annealing_transport",
            "exhaustion_parseval_coverage_energy",
            "parity_orthogonal_shell_growth_connection",
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
