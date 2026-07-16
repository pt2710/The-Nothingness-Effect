"""Lazy catalog for canonical theorem-complex contracts.

The catalog lives inside the installed package so generated theorem-component
modules never depend on repository-only tooling. A contract can remain as a
quarantined legacy implementation while its current inventory status is
``blocked`` or ``proxy``; only ``implemented`` inventory rows are active.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from importlib import import_module
from pathlib import Path

from .types import ComplexContract


CONTRACT_MODULES = (
    ("the_nothingness_effect._runtime.theorem_complex_runtime.recertified_catalog", "contracts"),
    ("the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.contracts", "flowpoint_contracts"),
    ("the_nothingness_effect.mathematical_architecture.contracts", "mathematical_closure_contracts"),
    ("the_nothingness_effect.foundational_architecture.duality.contracts", "duality_contracts"),
    ("the_nothingness_effect.foundational_architecture.symmetry.derived_contracts", "contracts"),
    ("the_nothingness_effect.foundational_architecture.spatiality.derived_contracts", "contracts"),
    ("the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts", "contracts"),
    ("the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.derived_contracts", "contracts"),
    ("the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts", "contracts"),
    ("the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.contracts", "contracts"),
    ("the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.derived_contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts", "contracts"),
    ("the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.derived_contracts", "contracts"),
    ("the_nothingness_effect.the_completeness_theorem.contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.qenn.contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.qenn.derived_contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.pgqenn.contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.pgqenn.derived_contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.soinets.contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.soinets.derived_contracts", "contracts"),
)


@lru_cache(maxsize=1)
def all_contracts() -> tuple[ComplexContract, ...]:
    contracts: list[ComplexContract] = []
    for module_name, factory_name in CONTRACT_MODULES:
        contracts.extend(getattr(import_module(module_name), factory_name)())
    identifiers = [str(contract.complex_id) for contract in contracts]
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("duplicate canonical theorem-complex contracts")
    return tuple(contracts)


def _default_matrix() -> Path:
    return Path(__file__).resolve().parents[3] / "docs" / "data" / "theorem_complex_implementation_matrix.csv"


def active_contracts(matrix_path: str | Path | None = None) -> tuple[ComplexContract, ...]:
    path = Path(matrix_path) if matrix_path is not None else _default_matrix()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        active_ids = {
            row["complex_id"]
            for row in csv.DictReader(handle)
            if row["implementation_status"] == "implemented"
        }
    catalog = {str(contract.complex_id): contract for contract in all_contracts()}
    missing = active_ids - catalog.keys()
    if missing:
        raise RuntimeError(f"implemented inventory IDs lack contracts: {sorted(missing)[:5]}")
    return tuple(catalog[identifier] for identifier in sorted(active_ids))
