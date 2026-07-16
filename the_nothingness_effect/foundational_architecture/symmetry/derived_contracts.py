"""Appendix-derived additive Flowpoint-symmetry law."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import additive_contract


APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea"
IMPLEMENTATION = "the_nothingness_effect/foundational_architecture/symmetry/derived_contracts.py"


def contracts():
    return (
        additive_contract(
            "phase_gated_compensation_transport",
            ("kernel_recursion", "order_two_symmetry_recursion"),
            appendix=APPENDIX,
            appendix_sha256=APPENDIX_SHA256,
            implementation_path=IMPLEMENTATION,
        ),
    )
