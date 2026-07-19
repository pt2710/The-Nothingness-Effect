"""Exact appendix-declared Elastic-Dubler B/C product carriers."""

from the_nothingness_effect._runtime.theorem_complex_runtime.exact_declared_products import promote_exact_products

from .contracts import contracts as _contracts


IMPLEMENTATION = "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect/authoritative_product_contracts.py"
TARGETS = (
    "temporal_directed_elastic_transport",
    "observable_conserved_directed_transport_closure",
    "spatially_calibrated_quantum_information_closure",
)


def contracts():
    return promote_exact_products(_contracts(), TARGETS, implementation_path=IMPLEMENTATION)
