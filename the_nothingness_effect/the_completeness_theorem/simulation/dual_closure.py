"""Dual-closure operator for finite illustrative toy systems.

The operator classifies represented dual pairs, boundary flags, missing duals,
contradictions, and fixed-point behavior. Closure here means representational
dual-pair closure in a finite toy system, not formal proof of a statement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from the_nothingness_effect.the_completeness_theorem.models import (
    CLAIM_BOUNDARY,
    ClosureRule,
    FormalSystem,
    RuleType,
    StatementNode,
    StatementStatus,
    closure_metrics,
)


CLOSABLE_STATUSES = {
    StatementStatus.PROVABLE,
    StatementStatus.UNPROVABLE_WITHIN_SYSTEM,
    StatementStatus.DUAL_COMPLEMENT,
    StatementStatus.CLOSURE_CANDIDATE,
    StatementStatus.OPEN,
    StatementStatus.UNRESOLVED,
}

BLOCKING_STATUSES = {
    StatementStatus.PARADOX_BOUNDARY,
    StatementStatus.CONTRADICTION,
}

ASSERTIVE_STATUSES = {
    StatementStatus.PROVABLE,
    StatementStatus.FORMALLY_PROVED,
    StatementStatus.CLOSED,
    StatementStatus.CLOSURE_CANDIDATE,
}


@dataclass
class StepUpdate:
    node_id: str
    before: str
    after: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "before": self.before,
            "after": self.after,
            "reason": self.reason,
        }


@dataclass
class ClosureStepResult:
    step: int
    updates: list[StepUpdate] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def changed_nodes(self) -> list[str]:
        return sorted({update.node_id for update in self.updates})

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "updates": [update.to_dict() for update in self.updates],
            "changed_nodes": self.changed_nodes,
            "metrics": dict(self.metrics),
        }


@dataclass
class ClosureTrace:
    system_name: str
    initial_state: dict[str, Any]
    steps: list[ClosureStepResult]
    final_state: dict[str, Any]
    fixed_point_type: str
    final_status: str
    metrics: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_name": self.system_name,
            "claim_boundary": CLAIM_BOUNDARY,
            "fixed_point_type": self.fixed_point_type,
            "final_status": self.final_status,
            "initial_state": self.initial_state,
            "steps": [step.to_dict() for step in self.steps],
            "final_state": self.final_state,
            "metrics": list(self.metrics),
        }


class DualClosureOperator:
    """Classify finite toy systems with conservative dual-closure semantics."""

    def step(self, system: FormalSystem, step_index: int) -> ClosureStepResult:
        updates: list[StepUpdate] = []

        for rule in system.rules:
            self._apply_rule(system, rule, updates)

        self._flag_missing_or_unverified_duals(system, updates)
        self._flag_circular_dependencies(system, updates)
        self._flag_contradictions(system, updates)
        self._classify_dual_pairs(system, updates)

        changed_nodes = sorted({update.node_id for update in updates})
        metrics = closure_metrics(system, step_index, changed_nodes)
        return ClosureStepResult(step=step_index, updates=updates, metrics=metrics)

    def run(self, system: FormalSystem, max_steps: int = 12) -> ClosureTrace:
        working = system.clone()
        initial_state = working.to_dict()
        initial_metrics = closure_metrics(working, 0, [])
        steps: list[ClosureStepResult] = []
        metrics = [initial_metrics]
        seen = {working.signature(): 0}
        fixed_point_type = "non_convergent_system"

        for step_index in range(1, max_steps + 1):
            result = self.step(working, step_index)
            steps.append(result)
            metrics.append(result.metrics)
            signature = working.signature()

            if not result.updates:
                fixed_point_type = self._classify_stable_fixed_point(working)
                break
            if signature in seen:
                fixed_point_type = "oscillatory_system"
                break
            seen[signature] = step_index

        final_status = self._final_status(working, fixed_point_type)
        return ClosureTrace(
            system_name=working.name,
            initial_state=initial_state,
            steps=steps,
            final_state=working.to_dict(),
            fixed_point_type=fixed_point_type,
            final_status=final_status,
            metrics=metrics,
        )

    def _apply_rule(
        self,
        system: FormalSystem,
        rule: ClosureRule,
        updates: list[StepUpdate],
    ) -> None:
        node = system.nodes.get(rule.target_id)
        if node is None:
            return

        if rule.rule_type == RuleType.MARK_PROVABLE:
            self._set_status(
                node,
                StatementStatus.PROVABLE,
                f"explicit finite rule '{rule.id}' marks the node provable",
                updates,
            )
            node.metadata["explicit_rule"] = rule.id
        elif rule.rule_type == RuleType.MARK_FORMALLY_PROVED:
            self._set_status(
                node,
                StatementStatus.FORMALLY_PROVED,
                f"explicit finite rule '{rule.id}' marks the node formally_proved",
                updates,
            )
            node.metadata["explicit_formal_proof_rule"] = rule.id
        elif rule.rule_type == RuleType.TOGGLE_STATUS:
            next_status = (
                StatementStatus.UNRESOLVED
                if node.status == StatementStatus.OPEN
                else StatementStatus.OPEN
            )
            node.metadata["phase"] = next_status.value
            self._set_status(
                node,
                next_status,
                f"toy oscillation rule '{rule.id}' toggles finite status",
                updates,
            )
        elif rule.rule_type == RuleType.DRIFT_UNRESOLVED:
            node.metadata["drift"] = int(node.metadata.get("drift", 0)) + 1
            self._set_status(
                node,
                StatementStatus.UNRESOLVED,
                f"toy non-convergence rule '{rule.id}' increments drift metadata",
                updates,
                force_record=True,
            )

    def _flag_missing_or_unverified_duals(
        self,
        system: FormalSystem,
        updates: list[StepUpdate],
    ) -> None:
        for node in system.nodes.values():
            if not node.dual_id or node.dual_id not in system.nodes:
                self._add_failure_mode(node, "missing_dual", updates)
                if node.metadata.get("boundary_like"):
                    self._add_failure_mode(node, "unpaired_boundary", updates)
                    self._set_status(
                        node,
                        StatementStatus.PARADOX_BOUNDARY,
                        "unpaired boundary-like node remains a boundary classification",
                        updates,
                    )
                elif node.status in CLOSABLE_STATUSES:
                    self._set_status(
                        node,
                        StatementStatus.UNRESOLVED,
                        "missing represented dual counterpart prevents closure",
                        updates,
                    )
                continue

            dual = system.nodes[node.dual_id]
            if dual.dual_id != node.id:
                self._add_failure_mode(node, "unverified_dual", updates)

    def _flag_circular_dependencies(
        self,
        system: FormalSystem,
        updates: list[StepUpdate],
    ) -> None:
        dependency_graph = {
            node.id: set(node.metadata.get("requires_closed", []))
            for node in system.nodes.values()
        }

        def has_cycle(start: str, current: str, seen: set[str]) -> bool:
            for dependency in dependency_graph.get(current, set()):
                if dependency == start:
                    return True
                if dependency in seen:
                    continue
                if has_cycle(start, dependency, seen | {dependency}):
                    return True
            return False

        for node in system.nodes.values():
            if dependency_graph.get(node.id) and has_cycle(node.id, node.id, {node.id}):
                self._add_failure_mode(node, "circular_dependency", updates)
                if node.status in CLOSABLE_STATUSES:
                    self._set_status(
                        node,
                        StatementStatus.UNRESOLVED,
                        "circular closure dependency prevents stable closed classification",
                        updates,
                    )

    def _flag_contradictions(
        self,
        system: FormalSystem,
        updates: list[StepUpdate],
    ) -> None:
        for node in system.nodes.values():
            for other_id in node.metadata.get("contradicts", []):
                other = system.nodes.get(other_id)
                if other is None:
                    continue
                if node.status in ASSERTIVE_STATUSES and other.status in ASSERTIVE_STATUSES:
                    self._add_failure_mode(node, "contradiction", updates)
                    self._add_failure_mode(other, "contradiction", updates)
                    self._set_status(
                        node,
                        StatementStatus.CONTRADICTION,
                        "assertive statement and represented anti-statement conflict",
                        updates,
                    )
                    self._set_status(
                        other,
                        StatementStatus.CONTRADICTION,
                        "assertive statement and represented anti-statement conflict",
                        updates,
                    )

    def _classify_dual_pairs(
        self,
        system: FormalSystem,
        updates: list[StepUpdate],
    ) -> None:
        for left_id, right_id in system.dual_pairs():
            left = system.nodes[left_id]
            right = system.nodes[right_id]
            if left.status in BLOCKING_STATUSES or right.status in BLOCKING_STATUSES:
                continue
            if self._has_unmet_dependency(left, system) or self._has_unmet_dependency(right, system):
                self._add_failure_mode(left, "unresolved_dependency", updates)
                self._add_failure_mode(right, "unresolved_dependency", updates)
                continue

            if (
                left.status == StatementStatus.CLOSURE_CANDIDATE
                and right.status == StatementStatus.CLOSURE_CANDIDATE
            ):
                self._set_status(
                    left,
                    StatementStatus.CLOSED,
                    "represented dual pair satisfies finite closure criteria",
                    updates,
                )
                self._set_status(
                    right,
                    StatementStatus.CLOSED,
                    "represented dual pair satisfies finite closure criteria",
                    updates,
                )
                continue

            if left.status in CLOSABLE_STATUSES and right.status in CLOSABLE_STATUSES:
                self._set_status(
                    left,
                    StatementStatus.CLOSURE_CANDIDATE,
                    "represented dual counterpart is present",
                    updates,
                )
                self._set_status(
                    right,
                    StatementStatus.CLOSURE_CANDIDATE,
                    "represented dual counterpart is present",
                    updates,
                )

    def _has_unmet_dependency(self, node: StatementNode, system: FormalSystem) -> bool:
        for dependency_id in node.metadata.get("requires_closed", []):
            dependency = system.nodes.get(dependency_id)
            if dependency is None or dependency.status != StatementStatus.CLOSED:
                return True
        return False

    def _add_failure_mode(
        self,
        node: StatementNode,
        mode: str,
        updates: list[StepUpdate],
    ) -> None:
        modes = set(node.metadata.get("failure_modes", []))
        if mode in modes:
            return
        before = node.status.value
        modes.add(mode)
        node.metadata["failure_modes"] = sorted(modes)
        updates.append(
            StepUpdate(
                node_id=node.id,
                before=before,
                after=node.status.value,
                reason=f"flagged {mode} in finite toy closure trace",
            )
        )

    def _set_status(
        self,
        node: StatementNode,
        status: StatementStatus,
        reason: str,
        updates: list[StepUpdate],
        force_record: bool = False,
    ) -> None:
        before = node.status
        if before == status and not force_record:
            return
        node.status = status
        updates.append(
            StepUpdate(
                node_id=node.id,
                before=before.value,
                after=status.value,
                reason=reason,
            )
        )

    def _classify_stable_fixed_point(self, system: FormalSystem) -> str:
        counts = system.status_counts()
        if (
            counts[StatementStatus.CLOSED.value] == len(system.nodes)
            and not system.failure_modes()
        ):
            return "stable_closed_fixed_point"
        return "stable_incomplete_fixed_point"

    def _final_status(self, system: FormalSystem, fixed_point_type: str) -> str:
        modes = system.failure_modes()
        if "contradiction" in modes:
            return "contradiction_or_paradox_boundary_flagged"
        if "circular_dependency" in modes:
            return "circular_dependency_flagged"
        if fixed_point_type == "stable_closed_fixed_point":
            return "closed_finite_dual_representation"
        if fixed_point_type == "oscillatory_system":
            return "oscillatory_finite_toy_system"
        if fixed_point_type == "non_convergent_system":
            return "non_convergent_finite_toy_system"
        return "incomplete_finite_dual_representation"

