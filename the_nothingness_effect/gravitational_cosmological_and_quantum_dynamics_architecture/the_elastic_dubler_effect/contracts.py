from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.source_faithful_contracts import contracts as explicit_contracts

SPEC = SPECS["elastic_dubler_effect"]


def contracts():
    return (*contracts_for(SPEC), *explicit_contracts())


def registered_elastic_dubler_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    for contract in explicit_contracts():
        registry.register(contract)
    return registry
