from dataclasses import replace

from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.source_faithful_contracts import contracts as explicit_contracts

SPEC = SPECS["elastic_pi_ripples"]
LEGACY_META_ID = "appendix_wide_gravitational_ripples_cross_complex_closure_and_computational_falsification_interface"
CANONICAL_META_ID = "appendix_wide_gravitational_ripple_wavefront_cross_complex_closure_and_computational_falsification_i"


def _normalized_explicit_contracts():
    return tuple(
        replace(contract, complex_id=ComplexId(CANONICAL_META_ID))
        if str(contract.complex_id) == LEGACY_META_ID
        else contract
        for contract in explicit_contracts()
    )


def contracts():
    return (*contracts_for(SPEC), *_normalized_explicit_contracts())


def registered_ripple_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    for contract in _normalized_explicit_contracts():
        registry.register(contract)
    return registry
