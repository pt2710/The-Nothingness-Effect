"""Canonical catalog of implemented contracts and deterministic artifact suites."""

from __future__ import annotations

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    active_contracts,
    release_active_contracts,
)

ARTIFACT_SUITES = (
    ("flowpoint", "the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.simulation.run_suite"),
    ("mathematical_closure", "the_nothingness_effect.mathematical_architecture.simulation.run_suite"),
    ("duality", "the_nothingness_effect.foundational_architecture.duality.simulation.run_suite"),
    ("dfi", "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.simulation.run_contract_suite"),
    ("pdfi", "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.simulation.run_contract_suite"),
    ("elastic_pi", "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.simulation.run_contract_suite"),
    ("elastic_pi_norm", "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.simulation.run_contract_suite"),
    ("elastic_dubler_effect", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.run_contract_suite"),
    ("elastic_dubler_interferometry", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.simulation.run_contract_suite"),
    ("locality_driven_gravity", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.simulation.run_contract_suite"),
    ("black_hole_dynamics", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.simulation.run_contract_suite"),
    ("elastic_pi_ripples", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.simulation.run_contract_suite"),
    ("cosmological_spark_dynamics", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics.simulation.run_contract_suite"),
    ("dtqc", "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.simulation.run_contract_suite"),
    ("completeness", "the_nothingness_effect.the_completeness_theorem.simulation.run_contract_suite"),
    ("qenn", "the_nothingness_effect.artificial_intelligence.qenn.simulation.run_contract_suite"),
    ("pgqenn", "the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite"),
    ("soinets", "the_nothingness_effect.artificial_intelligence.soinets.simulation.run_contract_suite"),
)


def implemented_contracts():
    """Historical runtime inventory, preserved for simulations and artifacts."""

    return active_contracts()


def release_implemented_contracts():
    """Dependency-closed implementation set used exclusively by release gates."""

    return release_active_contracts()
