"""Data model for finite illustrative dual-closure simulations.

These classes describe computational support artifacts for the TNE
completeness discussion. They model finite toy systems and trace state
classification. They are not formal proof substitutes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


CLAIM_BOUNDARY = (
    "finite illustrative model; computational support artifact; "
    "not a formal proof substitute"
)


class StatementStatus(str, Enum):
    """Finite toy-system statuses used by the closure trace."""

    PROVABLE = "provable"
    FORMALLY_PROVED = "formally_proved"
    UNPROVABLE_WITHIN_SYSTEM = "unprovable_within_system"
    DUAL_COMPLEMENT = "dual_complement"
    CLOSURE_CANDIDATE = "closure_candidate"
    CLOSED = "closed"
    OPEN = "open"
    PARADOX_BOUNDARY = "paradox_boundary"
    CONTRADICTION = "contradiction"
    UNRESOLVED = "unresolved"


class RuleType(str, Enum):
    """Rule types for explicit finite toy-system updates."""

    MARK_PROVABLE = "mark_provable"
    MARK_FORMALLY_PROVED = "mark_formally_proved"
    REQUIRE_CLOSED = "require_closed"
    TOGGLE_STATUS = "toggle_status"
    DRIFT_UNRESOLVED = "drift_unresolved"


@dataclass
class StatementNode:
    """A statement or represented dual counterpart in a finite toy system."""

    id: str
    label: str
    status: StatementStatus
    dual_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def clone(self) -> "StatementNode":
        return StatementNode(
            id=self.id,
            label=self.label,
            status=StatementStatus(self.status),
            dual_id=self.dual_id,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "status": self.status.value,
            "dual_id": self.dual_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ClosureRule:
    """A finite rule used by the toy closure operator.

    A node may only enter ``formally_proved`` through
    ``RuleType.MARK_FORMALLY_PROVED``. This keeps proof status separate from
    representational closure in the simulation artifacts.
    """

    id: str
    target_id: str
    rule_type: RuleType
    description: str
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "target_id": self.target_id,
            "rule_type": self.rule_type.value,
            "description": self.description,
            "depends_on": list(self.depends_on),
        }


@dataclass
class FormalSystem:
    """A finite toy formal system for dual-closure trace visualization."""

    name: str
    nodes: dict[str, StatementNode]
    rules: list[ClosureRule] = field(default_factory=list)
    edges: list[tuple[str, str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def clone(self) -> "FormalSystem":
        return FormalSystem(
            name=self.name,
            nodes={node_id: node.clone() for node_id, node in self.nodes.items()},
            rules=list(self.rules),
            edges=list(self.edges),
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "claim_boundary": CLAIM_BOUNDARY,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "rules": [rule.to_dict() for rule in self.rules],
            "edges": [list(edge) for edge in self.edges],
            "metadata": dict(self.metadata),
        }

    def verified_dual_nodes(self) -> set[str]:
        verified: set[str] = set()
        for node in self.nodes.values():
            if not node.dual_id or node.dual_id not in self.nodes:
                continue
            dual = self.nodes[node.dual_id]
            if dual.dual_id == node.id:
                verified.add(node.id)
        return verified

    def dual_pairs(self) -> list[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for node in self.nodes.values():
            if not node.dual_id or node.dual_id not in self.nodes:
                continue
            dual = self.nodes[node.dual_id]
            if dual.dual_id == node.id:
                pairs.add(tuple(sorted((node.id, dual.id))))
        return sorted(pairs)

    def status_counts(self) -> dict[str, int]:
        counts = {status.value: 0 for status in StatementStatus}
        for node in self.nodes.values():
            counts[node.status.value] += 1
        return counts

    def failure_modes(self) -> set[str]:
        modes: set[str] = set()
        for node in self.nodes.values():
            values = node.metadata.get("failure_modes", [])
            modes.update(str(value) for value in values)
        return modes

    def pair_coverage(self) -> dict[str, float | int]:
        total = len(self.nodes)
        verified = len(self.verified_dual_nodes())
        percent = 0.0 if total == 0 else round((verified / total) * 100.0, 2)
        return {
            "node_count": total,
            "verified_dual_nodes": verified,
            "verified_dual_percent": percent,
        }

    def signature(self) -> tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]:
        """Return a deterministic signature for fixed-point detection."""

        tracked_keys = (
            "failure_modes",
            "phase",
            "drift",
            "explicit_rule",
            "explicit_formal_proof_rule",
        )
        values: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
        for node_id in sorted(self.nodes):
            node = self.nodes[node_id]
            metadata_signature = tuple(
                (key, repr(node.metadata.get(key)))
                for key in tracked_keys
                if key in node.metadata
            )
            values.append((node_id, node.status.value, metadata_signature))
        return tuple(values)


def closure_metrics(
    system: FormalSystem,
    step_index: int,
    changed_nodes: list[str] | None = None,
) -> dict[str, Any]:
    """Return compact iteration metrics for JSON and CSV export."""

    counts = system.status_counts()
    unresolved_count = sum(
        counts[status.value]
        for status in (
            StatementStatus.OPEN,
            StatementStatus.UNRESOLVED,
            StatementStatus.UNPROVABLE_WITHIN_SYSTEM,
            StatementStatus.CLOSURE_CANDIDATE,
        )
    )
    boundary_count = counts[StatementStatus.PARADOX_BOUNDARY.value]
    contradiction_count = counts[StatementStatus.CONTRADICTION.value]
    coverage = system.pair_coverage()
    return {
        "system_name": system.name,
        "step": step_index,
        "changed_nodes": sorted(changed_nodes or []),
        "changed_count": len(set(changed_nodes or [])),
        "closed_count": counts[StatementStatus.CLOSED.value],
        "unresolved_count": unresolved_count,
        "boundary_count": boundary_count,
        "contradiction_count": contradiction_count,
        "provable_count": counts[StatementStatus.PROVABLE.value],
        "formally_proved_count": counts[StatementStatus.FORMALLY_PROVED.value],
        "verified_dual_percent": coverage["verified_dual_percent"],
        "failure_modes": sorted(system.failure_modes()),
        "scope_note": CLAIM_BOUNDARY,
    }

