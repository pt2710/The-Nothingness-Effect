"""Lazy catalog for canonical theorem-complex contracts.

The catalog lives inside the installed package so generated theorem-component
modules never depend on repository-only tooling. Release activation is
fail-closed: an inventory row requested as ``implemented`` is active only when
all of its declared source contracts are active as well. Contract and inventory
source digests are normalized through the authoritative appendix manifest.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from importlib import import_module
from pathlib import Path

from .authority import bind_contracts, bind_inventory_rows
from .types import ComplexContract


CONTRACT_MODULES = (
    (
        "the_nothingness_effect._runtime.theorem_complex_runtime.recertified_catalog",
        "contracts",
    ),
    (
        "the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.contracts",
        "flowpoint_contracts",
    ),
    (
        "the_nothingness_effect.mathematical_architecture.contracts",
        "mathematical_closure_contracts",
    ),
    (
        "the_nothingness_effect.foundational_architecture.duality.contracts",
        "duality_contracts",
    ),
    (
        "the_nothingness_effect.foundational_architecture.symmetry.derived_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.foundational_architecture.spatiality.derived_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.source_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.derived_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature.derived_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint.derived_contracts",
        "contracts",
    ),
    ("the_nothingness_effect.the_completeness_theorem.contracts", "contracts"),
    ("the_nothingness_effect.artificial_intelligence.qenn.contracts", "contracts"),
    (
        "the_nothingness_effect.artificial_intelligence.qenn.source_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.artificial_intelligence.qenn.derived_contracts",
        "contracts",
    ),
    ("the_nothingness_effect.artificial_intelligence.pgqenn.contracts", "contracts"),
    (
        "the_nothingness_effect.artificial_intelligence.pgqenn.derived_contracts",
        "contracts",
    ),
    ("the_nothingness_effect.artificial_intelligence.soinets.contracts", "contracts"),
    (
        "the_nothingness_effect.artificial_intelligence.soinets.derived_contracts",
        "contracts",
    ),
)


@lru_cache(maxsize=1)
def all_contracts() -> tuple[ComplexContract, ...]:
    contracts: list[ComplexContract] = []
    for module_name, factory_name in CONTRACT_MODULES:
        contracts.extend(getattr(import_module(module_name), factory_name)())
    bound = bind_contracts(contracts)
    identifiers = [str(contract.complex_id) for contract in bound]
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("duplicate canonical theorem-complex contracts")
    return bound


def _default_matrix() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "data"
        / "theorem_complex_implementation_matrix.csv"
    )


def _matrix_rows(matrix_path: str | Path | None = None) -> list[dict[str, str]]:
    path = Path(matrix_path) if matrix_path is not None else _default_matrix()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    return bind_inventory_rows(rows)


def release_statuses(matrix_path: str | Path | None = None) -> dict[str, str]:
    """Return dependency-closed release statuses for every inventory row.

    Rows requested as ``implemented`` are recursively downgraded to ``proxy``
    whenever at least one declared source contract is not itself release-active.
    This prevents a partially closed dependency graph from being advertised as
    a completed theorem-complex implementation.
    """

    rows = _matrix_rows(matrix_path)
    requested = {
        row["complex_id"]
        for row in rows
        if row["implementation_status"] == "implemented"
    }
    catalog = {str(contract.complex_id): contract for contract in all_contracts()}
    missing_contracts = requested - catalog.keys()
    if missing_contracts:
        raise RuntimeError(
            f"implemented inventory IDs lack contracts: {sorted(missing_contracts)[:5]}"
        )

    active = set(requested)
    while True:
        invalid = {
            identifier
            for identifier in active
            if any(
                str(source_id) not in active
                for source_id in catalog[identifier].source_ids
            )
        }
        if not invalid:
            break
        active.difference_update(invalid)

    statuses: dict[str, str] = {}
    for row in rows:
        identifier = row["complex_id"]
        requested_status = row["implementation_status"]
        statuses[identifier] = (
            "implemented"
            if requested_status == "implemented" and identifier in active
            else "proxy"
            if requested_status == "implemented"
            else requested_status
        )
    return statuses


def dependency_downgrades(
    matrix_path: str | Path | None = None,
) -> tuple[dict[str, object], ...]:
    """Describe every requested implementation removed by dependency closure."""

    rows = _matrix_rows(matrix_path)
    statuses = release_statuses(matrix_path)
    catalog = {str(contract.complex_id): contract for contract in all_contracts()}
    active = {
        identifier
        for identifier, status in statuses.items()
        if status == "implemented"
    }
    downgraded: list[dict[str, object]] = []
    for row in rows:
        identifier = row["complex_id"]
        if (
            row["implementation_status"] != "implemented"
            or statuses[identifier] == "implemented"
        ):
            continue
        contract = catalog[identifier]
        missing_sources = sorted(
            str(source_id)
            for source_id in contract.source_ids
            if str(source_id) not in active
        )
        downgraded.append(
            {
                "complex_id": identifier,
                "effective_status": "proxy",
                "reason": "dependency_closure_not_satisfied",
                "inactive_source_ids": missing_sources,
            }
        )
    return tuple(sorted(downgraded, key=lambda item: str(item["complex_id"])))


def active_contracts(
    matrix_path: str | Path | None = None,
) -> tuple[ComplexContract, ...]:
    """Return contracts explicitly requested as implemented in the inventory.

    This preserves the historical runtime API. Release gates must use
    :func:`release_active_contracts`, which additionally enforces recursive
    dependency closure.
    """

    rows = _matrix_rows(matrix_path)
    active_ids = {
        row["complex_id"]
        for row in rows
        if row["implementation_status"] == "implemented"
    }
    catalog = {str(contract.complex_id): contract for contract in all_contracts()}
    missing = active_ids - catalog.keys()
    if missing:
        raise RuntimeError(
            f"implemented inventory IDs lack contracts: {sorted(missing)[:5]}"
        )
    return tuple(catalog[identifier] for identifier in sorted(active_ids))


def release_active_contracts(
    matrix_path: str | Path | None = None,
) -> tuple[ComplexContract, ...]:
    """Return only implementations whose complete source graph is release-active."""

    statuses = release_statuses(matrix_path)
    active_ids = {
        identifier
        for identifier, status in statuses.items()
        if status == "implemented"
    }
    catalog = {str(contract.complex_id): contract for contract in all_contracts()}
    return tuple(catalog[identifier] for identifier in sorted(active_ids))
