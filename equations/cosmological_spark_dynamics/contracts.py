from equations.gravitational_contract_runtime import SPECS, contracts_for, registered_module_registry

SPEC = SPECS["cosmological_spark_dynamics"]


def contracts():
    return contracts_for(SPEC)


def registered_spark_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    return registered_module_registry(SPEC, matrix)
