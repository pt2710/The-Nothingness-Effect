from equations.gravitational_cosmological_quantum_dynamics.contract_runtime import SPECS, contracts_for, registered_module_registry

SPEC = SPECS["elastic_dubler_interferometry"]


def contracts():
    return contracts_for(SPEC)


def registered_interferometry_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    return registered_module_registry(SPEC, matrix)
