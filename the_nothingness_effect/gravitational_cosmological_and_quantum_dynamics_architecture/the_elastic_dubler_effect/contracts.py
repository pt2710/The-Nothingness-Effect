from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.contract_runtime import SPECS, contracts_for, registered_module_registry
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.source_faithful_contracts import contracts as explicit_contracts
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.potential_current_contract import contract as potential_current_contract
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.parity_elastic_spectral_contract import C_ID as SPECTRAL_C_ID, contract as spectral_contract

SPEC = SPECS["elastic_dubler_effect"]


def _remaining_explicit_contracts():
    return tuple(
        item for item in explicit_contracts()
        if str(item.complex_id) != SPECTRAL_C_ID
    )


def contracts():
    runtime = tuple(
        item for item in contracts_for(SPEC)
        if str(item.complex_id) != SPEC.c_id
    )
    return (
        *runtime,
        potential_current_contract(),
        spectral_contract(),
        *_remaining_explicit_contracts(),
    )


def registered_elastic_dubler_registry(matrix="docs/data/theorem_complex_implementation_matrix.csv"):
    registry = registered_module_registry(SPEC, matrix)
    registry.register(potential_current_contract())
    registry.register(spectral_contract())
    for contract in _remaining_explicit_contracts():
        registry.register(contract)
    return registry
