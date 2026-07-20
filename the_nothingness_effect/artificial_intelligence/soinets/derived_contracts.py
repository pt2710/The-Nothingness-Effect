"""Recertified SOInet A05--A18, B21--B28, and C30--C33 contracts."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    additive_contract,
    spatial_contract,
)

from .contracts import APPENDIX, APPENDIX_SHA256
from .source_contracts import contracts as source_contracts


IMPLEMENTATION = "the_nothingness_effect/artificial_intelligence/soinets/derived_contracts.py"

# The native SOInet B blocks name their complete 1B/2B semantic sources rather
# than cross-referencing A-complex labels. These pairings follow the exact
# left/right theorem subjects in B21--B28.
B_SPECS = (
    (
        "cross_modal_generalization_collapse_transfer",
        (
            "soinet_cross_modal_transfer_generalization_and_dual_stability",
            "soi_cross_domain_generalization_and_collapse",
        ),
    ),
    (
        "modality_compositionality_collapse_connection",
        (
            "soinet_cross_modal_compositionality_modality_invariant_collapse_principle",
            "soi_modality_dual_closure",
        ),
    ),
    (
        "error_entropy_dissipation_functional",
        (
            "soinet_error_contraction_and_dual_error_orthogonality",
            "soi_entropy_minimization_and_entropic_catastrophe",
        ),
    ),
    (
        "entropy_spectral_phase_locking_operator",
        (
            "universal_entropy_minimization_and_collapse_degeneracy_duality_in_soinet",
            "spectral_phase_locking_and_collapse_in_soinet",
        ),
    ),
    (
        "modality_spectrum_representation_coupling",
        (
            "soinet_modality_invariant_learning_and_universal_adaptation",
            "soi_spectrum_learning_and_classification_soi_spectrum_degeneracy_dual_instability",
        ),
    ),
    (
        "expressivity_meta_learnability_stability_functional",
        (
            "soinet_universal_expressivity_bound_entropy_minimal_generalization_principle",
            "soinet_meta_learnability_dual_closure",
        ),
    ),
    (
        "stack_domain_generalization_transport",
        (
            "hierarchical_soi_stack_transfer_cross_regime_collapse_duality",
            "soi_cross_domain_generalization_and_collapse",
        ),
    ),
    (
        "universalization_cloning_obstruction_functional",
        (
            "soinet_universal_generalization_principle_failure_brittleness_duality",
            "soinet_universal_cloning_principle_cloning_failure_duality",
        ),
    ),
)

C_SPECS = (
    (
        "cross_modal_compositional_spatial_closure",
        (
            "cross_modal_generalization_collapse_transfer",
            "modality_compositionality_collapse_connection",
        ),
    ),
    (
        "error_entropy_phase_locking_spatial_closure",
        (
            "error_entropy_dissipation_functional",
            "entropy_spectral_phase_locking_operator",
        ),
    ),
    (
        "modality_spectrum_meta_learnability_spatial_closure",
        (
            "modality_spectrum_representation_coupling",
            "expressivity_meta_learnability_stability_functional",
        ),
    ),
    (
        "stack_domain_cloning_spatial_closure",
        (
            "stack_domain_generalization_transport",
            "universalization_cloning_obstruction_functional",
        ),
    ),
)


def contracts():
    return (
        *source_contracts(),
        *(
            additive_contract(
                complex_id,
                source_ids,
                appendix=APPENDIX,
                appendix_sha256=APPENDIX_SHA256,
                implementation_path=IMPLEMENTATION,
            )
            for complex_id, source_ids in B_SPECS
        ),
        *(
            spatial_contract(
                complex_id,
                source_ids,
                appendix=APPENDIX,
                appendix_sha256=APPENDIX_SHA256,
                implementation_path=IMPLEMENTATION,
            )
            for complex_id, source_ids in C_SPECS
        ),
    )
