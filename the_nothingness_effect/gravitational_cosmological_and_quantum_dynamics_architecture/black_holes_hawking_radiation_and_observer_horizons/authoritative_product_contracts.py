"""Exact appendix-declared black-hole B/C product carriers."""

from the_nothingness_effect._runtime.theorem_complex_runtime.exact_declared_products import promote_exact_products

from .contracts import contracts as _contracts


IMPLEMENTATION = "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/authoritative_product_contracts.py"
TARGETS = (
    "spatiotemporal_hawking_flux_density",
    "certified_residual_memory_lower_bound",
    "observable_hawking_memory_certification",
)


def contracts():
    return promote_exact_products(_contracts(), TARGETS, implementation_path=IMPLEMENTATION)
