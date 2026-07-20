"""Exact appendix-declared DTQC C product carriers."""

from the_nothingness_effect._runtime.theorem_complex_runtime.exact_declared_products import promote_exact_products

from .contracts import contracts as _contracts
from .derived_contracts import contracts as _derived_contracts


IMPLEMENTATION = "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/authoritative_product_contracts.py"
TARGETS = (
    "elastic_parseval_quasicrystal_isometry",
    "parity_meyer_noise_stable_diffraction_closure",
    "certified_multiscale_dtqc_reconstruction_closure",
)


def contracts():
    return promote_exact_products(
        (*_contracts(), *_derived_contracts()),
        TARGETS,
        implementation_path=IMPLEMENTATION,
    )
