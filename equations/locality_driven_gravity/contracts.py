from equations.gravitational_contract_runtime import SPECS, contracts_for, registered_module_registry

SPEC = SPECS["locality_driven_gravity"]


def contracts():
    return contracts_for(SPEC)


def registered_locality_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    return registered_module_registry(SPEC, matrix)
