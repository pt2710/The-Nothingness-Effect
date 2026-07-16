import pytest

from the_nothingness_effect.the_completeness_theorem.models import (
    ClosureRule,
    FormalSystem,
    RuleType,
    StatementNode,
    StatementStatus,
)
from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import DualClosureOperator
from the_nothingness_effect.the_completeness_theorem.simulation.godel_boundary import (
    contradiction_system,
    fully_pairable_system,
    godel_boundary_system,
    missing_dual_system,
    unpaired_boundary_system,
)


def _run(system: FormalSystem, max_steps: int = 8):
    return DualClosureOperator().run(system, max_steps=max_steps)


def test_formally_proved_requires_explicit_rule():
    unruled_trace = _run(fully_pairable_system())
    unruled_statuses = [
        node["status"] for node in unruled_trace.final_state["nodes"].values()
    ]
    assert "formally_proved" not in unruled_statuses

    ruled_system = FormalSystem(
        name="explicit_formal_rule_system",
        nodes={
            "p": StatementNode(
                id="p",
                label="Explicitly ruled finite toy statement",
                status=StatementStatus.OPEN,
            )
        },
        rules=[
            ClosureRule(
                id="explicit_formal_rule",
                target_id="p",
                rule_type=RuleType.MARK_FORMALLY_PROVED,
                description="Explicit finite toy rule for formal-proof status.",
            )
        ],
    )
    ruled_trace = _run(ruled_system, max_steps=2)
    final_node = ruled_trace.final_state["nodes"]["p"]
    assert final_node["status"] == "formally_proved"
    assert final_node["metadata"]["explicit_formal_proof_rule"] == "explicit_formal_rule"


def test_unprovable_within_system_is_not_false():
    system = godel_boundary_system()
    node = system.nodes["godel_like_statement"]
    assert node.status == StatementStatus.UNPROVABLE_WITHIN_SYSTEM
    assert node.metadata["interpretation"] == "unprovable_within_system is not treated as false"

    trace = _run(system)
    all_statuses = {node["status"] for node in trace.final_state["nodes"].values()}
    assert "false" not in all_statuses


def test_paradox_boundary_is_not_automatically_closed():
    trace = _run(unpaired_boundary_system())
    final_node = trace.final_state["nodes"]["g"]
    assert final_node["status"] == "paradox_boundary"
    assert "unpaired_boundary" in final_node["metadata"]["failure_modes"]


def test_dual_closure_requires_represented_counterparts():
    trace = _run(missing_dual_system())
    final_q = trace.final_state["nodes"]["q"]
    assert final_q["status"] != "closed"
    assert "missing_dual" in final_q["metadata"]["failure_modes"]


def test_fully_represented_pairs_can_close():
    trace = _run(fully_pairable_system())
    statuses = {node["status"] for node in trace.final_state["nodes"].values()}
    assert statuses == {"closed"}
    assert trace.fixed_point_type == "stable_closed_fixed_point"


def test_contradiction_system_flags_boundary_instead_of_silent_closure():
    trace = _run(contradiction_system())
    statuses = {node["status"] for node in trace.final_state["nodes"].values()}
    assert statuses == {"contradiction"}
    for node in trace.final_state["nodes"].values():
        assert "contradiction" in node["metadata"]["failure_modes"]


def test_unknown_required_node_is_not_silently_closed():
    system = FormalSystem(
        name="unknown_dependency_system",
        nodes={
            "p": StatementNode(
                id="p",
                label="Finite toy statement with missing dependency",
                status=StatementStatus.OPEN,
                dual_id="not_p",
                metadata={"requires_closed": ["missing_dependency"]},
            ),
            "not_p": StatementNode(
                id="not_p",
                label="Represented dual with missing dependency",
                status=StatementStatus.OPEN,
                dual_id="p",
                metadata={"requires_closed": ["missing_dependency"]},
            ),
        },
    )
    trace = _run(system)
    statuses = {node["status"] for node in trace.final_state["nodes"].values()}
    assert "closed" not in statuses
    for node in trace.final_state["nodes"].values():
        assert "unresolved_dependency" in node["metadata"]["failure_modes"]

