"""Theorem-complex inventory and implementation registry."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .types import ComplexContract, ComplexId, ComplexLevel


@dataclass(frozen=True)
class ComplexInventoryRecord:
    complex_id: ComplexId
    source_complex_id: str
    appendix: str
    appendix_source_sha256: str
    level: ComplexLevel
    title: str
    first_label: str
    equation_labels: tuple[str, ...]
    module: str
    implementation_status: str
    implementation_path: str
    test_path: str
    simulation_path: str


class TheoremComplexRegistry:
    def __init__(self) -> None:
        self._inventory: dict[ComplexId, ComplexInventoryRecord] = {}
        self._contracts: dict[ComplexId, ComplexContract] = {}

    def add_inventory(self, record: ComplexInventoryRecord) -> None:
        if record.complex_id in self._inventory:
            raise ValueError(f"Duplicate theorem-complex ID: {record.complex_id}")
        self._inventory[record.complex_id] = record

    def register(self, contract: ComplexContract) -> None:
        if contract.complex_id in self._contracts:
            raise ValueError(f"Duplicate theorem contract: {contract.complex_id}")
        record = self._inventory.get(contract.complex_id)
        if record is None:
            raise KeyError(f"Contract is absent from inventory: {contract.complex_id}")
        if record.level is not contract.level:
            raise ValueError(f"Level mismatch for {contract.complex_id}")
        if record.appendix != contract.appendix:
            raise ValueError(f"Appendix mismatch for {contract.complex_id}")
        self._contracts[contract.complex_id] = contract

    def get(self, complex_id: str | ComplexId) -> ComplexInventoryRecord:
        key = complex_id if isinstance(complex_id, ComplexId) else ComplexId(complex_id)
        return self._inventory[key]

    def contract(self, complex_id: str | ComplexId) -> ComplexContract:
        key = complex_id if isinstance(complex_id, ComplexId) else ComplexId(complex_id)
        return self._contracts[key]

    def inventory(self) -> tuple[ComplexInventoryRecord, ...]:
        return tuple(self._inventory.values())

    def contracts(self) -> tuple[ComplexContract, ...]:
        return tuple(self._contracts.values())

    def counts(self) -> dict[str, int]:
        result = {"total": len(self._inventory), "A": 0, "B": 0, "C": 0}
        for record in self._inventory.values():
            result[record.level.value] += 1
        result["inventory_implemented"] = sum(
            record.implementation_status == "implemented"
            for record in self._inventory.values()
        )
        result["registered_contracts"] = len(self._contracts)
        return result

    @classmethod
    def from_csv(cls, path: str | Path) -> "TheoremComplexRegistry":
        registry = cls()
        with Path(path).open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                labels = tuple(
                    item.strip()
                    for item in row.get("equation_labels", "").replace("|", ";").split(";")
                    if item.strip()
                )
                registry.add_inventory(
                    ComplexInventoryRecord(
                        complex_id=ComplexId(row["complex_id"]),
                        source_complex_id=row.get("source_complex_id", row["complex_id"]),
                        appendix=row["appendix_file"],
                        appendix_source_sha256=row["appendix_source_sha256"],
                        level=ComplexLevel(row["level"]),
                        title=row["complex_title"],
                        first_label=row["first_label"],
                        equation_labels=labels,
                        module=row["module"],
                        implementation_status=row["implementation_status"],
                        implementation_path=row.get("implementation_path", ""),
                        test_path=row.get("test_path", ""),
                        simulation_path=row.get("simulation_path", ""),
                    )
                )
        return registry

    def missing_contract_ids(self) -> Iterable[ComplexId]:
        return (item for item in self._inventory if item not in self._contracts)
