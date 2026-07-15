from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry

SPEC = SPECS["elastic_dubler_effect"]


def contracts():
    return contracts_for(SPEC)


def registered_elastic_dubler_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    return registered_module_registry(SPEC, matrix)
