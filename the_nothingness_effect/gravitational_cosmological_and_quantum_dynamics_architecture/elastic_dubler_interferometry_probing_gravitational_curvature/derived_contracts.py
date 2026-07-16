"""Genuine appendix-derived EDI barrier, identifiability, and spatial inverse laws."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    additive_contract,
    spatial_contract,
)


APPENDIX = "appendix_tne_gravitational_cosmological_quantum_dynamics.tex"
APPENDIX_SHA256 = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
IMPLEMENTATION = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "elastic_dubler_interferometry_probing_gravitational_curvature/derived_contracts.py"
)

B_SPECS = (
    (
        "2_adic_curvature_regularity_barrier",
        (
            "bridge_duality_and_the_2_adic_criterion",
            "elastic_curvature_smoothness_curvature_singularity",
        ),
    ),
    (
        "stability_conditioned_geometric_identifiability",
        (
            "elastic_entropic_stability_entropic_instability",
            "elastic_geometric_consistency_geometric_degeneracy",
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
    ) + (
        spatial_contract(
            "regularized_stable_geometric_reconstruction",
            (
                "2_adic_curvature_regularity_barrier",
                "stability_conditioned_geometric_identifiability",
            ),
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        ),
    )
