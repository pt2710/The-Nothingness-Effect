from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.source_faithful_contracts import contracts as explicit_contracts
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.potential_current_contract import contract as potential_current_contract

SPEC = SPECS["elastic_dubler_effect"]


def contracts():
    runtime = tuple(
        item for item in contracts_for(SPEC)
        if str(item.complex_id) != SPEC.c_id
    )
    return (*runtime, potential_current_contract(), *explicit_contracts())


def registered_elastic_dubler_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    registry.register(potential_current_contract())
    for contract in explicit_contracts():
        registry.register(contract)
    return registry
