"""Canonical catalog of implemented contracts and deterministic artifact suites."""

from __future__ import annotations

from importlib import import_module


CONTRACT_MODULES = (
    ("equations.flowpoint.contracts", "flowpoint_contracts"),
    ("equations.mathematical_closure.contracts", "mathematical_closure_contracts"),
    ("equations.duality.contracts", "duality_contracts"),
    ("equations.dynamic_fluctuation_index.contracts", "contracts"),
    ("equations.parity_dfi.contracts", "contracts"),
    ("equations.elastic_pi.contracts", "contracts"),
    ("equations.elastic_pi_norm.contracts", "contracts"),
    ("equations.elastic_dubler_effect.contracts", "contracts"),
    ("equations.elastic_dubler_interferometry.contracts", "contracts"),
    ("equations.locality_driven_gravity.contracts", "contracts"),
    ("equations.black_hole_dynamics.contracts", "contracts"),
    ("equations.elastic_pi_ripples.contracts", "contracts"),
    ("equations.cosmological_spark_dynamics.contracts", "contracts"),
    ("equations.dtqc.contracts", "contracts"),
    ("equations.completeness_theorem.contracts", "contracts"),
    ("equations.artificial_intelligence.qenn.contracts", "contracts"),
    ("equations.artificial_intelligence.pgqenn.contracts", "contracts"),
    ("equations.artificial_intelligence.soinets.contracts", "contracts"),
)

ARTIFACT_SUITES = (
    ("flowpoint", "equations.flowpoint.simulation.run_suite"),
    ("mathematical_closure", "equations.mathematical_closure.simulation.run_suite"),
    ("duality", "equations.duality.simulation.run_suite"),
    ("dfi", "equations.dynamic_fluctuation_index.simulation.run_contract_suite"),
    ("pdfi", "equations.parity_dfi.simulation.run_contract_suite"),
    ("elastic_pi", "equations.elastic_pi.simulation.run_contract_suite"),
    ("elastic_pi_norm", "equations.elastic_pi_norm.simulation.run_contract_suite"),
    ("elastic_dubler_effect", "equations.elastic_dubler_effect.simulation.run_contract_suite"),
    ("elastic_dubler_interferometry", "equations.elastic_dubler_interferometry.simulation.run_contract_suite"),
    ("locality_driven_gravity", "equations.locality_driven_gravity.simulation.run_contract_suite"),
    ("black_hole_dynamics", "equations.black_hole_dynamics.simulation.run_contract_suite"),
    ("elastic_pi_ripples", "equations.elastic_pi_ripples.simulation.run_contract_suite"),
    ("cosmological_spark_dynamics", "equations.cosmological_spark_dynamics.simulation.run_contract_suite"),
    ("dtqc", "equations.dtqc.simulation.run_contract_suite"),
    ("completeness", "equations.completeness_theorem.simulation.run_contract_suite"),
    ("qenn", "equations.artificial_intelligence.qenn.simulation.run_contract_suite"),
    ("pgqenn", "equations.artificial_intelligence.pgqenn.simulation.run_contract_suite"),
    ("soinets", "equations.artificial_intelligence.soinets.simulation.run_contract_suite"),
)


def implemented_contracts():
    contracts = []
    for module_name, factory_name in CONTRACT_MODULES:
        contracts.extend(getattr(import_module(module_name), factory_name)())
    return tuple(contracts)
