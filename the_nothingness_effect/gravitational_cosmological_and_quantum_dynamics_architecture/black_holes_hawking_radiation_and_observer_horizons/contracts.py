from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry

SPEC = SPECS["black_hole_dynamics"]


def contracts():
    return contracts_for(SPEC)


def registered_black_hole_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    return registered_module_registry(SPEC, matrix)
