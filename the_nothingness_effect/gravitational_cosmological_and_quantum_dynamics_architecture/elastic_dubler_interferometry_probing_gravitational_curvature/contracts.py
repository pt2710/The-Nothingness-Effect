from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.memory_tomography_contract import contract as memory_tomography_contract

SPEC = SPECS["elastic_dubler_interferometry"]


def contracts():
    runtime = tuple(
        item for item in contracts_for(SPEC)
        if str(item.complex_id) != SPEC.c_id
    )
    return (*runtime, memory_tomography_contract())


def registered_interferometry_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    registry.register(memory_tomography_contract())
    return registry
