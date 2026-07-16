"""Appendix-derived additive and spatial Flowpoint-spatiality laws."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import (
    additive_contract,
    spatial_contract,
)


APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea"
IMPLEMENTATION = "the_nothingness_effect/foundational_architecture/spatiality/derived_contracts.py"


def contracts():
    return (
        additive_contract(
            "involution_to_chord_linearization",
            ("order_two_symmetry_recursion", "affine_spatial_involution_orbit"),
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        ),
        spatial_contract(
            "twisted_orbit_balance_bundle",
            ("phase_gated_compensation_transport", "involution_to_chord_linearization"),
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        ),
    )
