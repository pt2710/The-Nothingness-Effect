"""Exact appendix-declared locality-gravity C product carriers."""

from the_nothingness_effect._runtime.theorem_complex_runtime.exact_declared_products import promote_exact_products

from .contracts import contracts as _contracts


IMPLEMENTATION = "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity/authoritative_product_contracts.py"
TARGETS = (
    "screened_rotation_halo_geometry",
    "information_preserving_cosmic_network_closure",
)


def contracts():
    return promote_exact_products(_contracts(), TARGETS, implementation_path=IMPLEMENTATION)
