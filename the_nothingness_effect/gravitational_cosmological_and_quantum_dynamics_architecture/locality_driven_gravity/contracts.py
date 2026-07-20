from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.source_faithful_contracts import contracts as explicit_contracts
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.morphogenesis_contract import contract as morphogenesis_contract

SPEC = SPECS["locality_driven_gravity"]


def contracts():
    runtime = tuple(
        item for item in contracts_for(SPEC)
        if str(item.complex_id) != SPEC.c_id
    )
    return (*runtime, morphogenesis_contract(), *explicit_contracts())


def registered_locality_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    registry.register(morphogenesis_contract())
    for contract in explicit_contracts():
        registry.register(contract)
    return registry
