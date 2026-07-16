"""Appendix-derived additive Flowpoint-symmetry law."""

from the_nothingness_effect._runtime.theorem_complex_runtime.derived_laws import additive_contract


APPENDIX = "appendix_tne_foundational_closure_architecture.tex"
APPENDIX_SHA256 = "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69"
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
