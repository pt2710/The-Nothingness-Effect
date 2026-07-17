from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.canonical_contracts import contracts as explicit_contracts

SPEC = SPECS["elastic_pi_ripples"]


def contracts():
    return (*contracts_for(SPEC), *explicit_contracts())


def registered_ripple_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    for contract in explicit_contracts():
        registry.register(contract)
    return registry
