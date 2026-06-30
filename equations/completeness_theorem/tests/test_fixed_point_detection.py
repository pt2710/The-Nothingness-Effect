from equations.completeness_theorem.simulation.dual_closure import DualClosureOperator
from equations.completeness_theorem.simulation.godel_boundary import (
    circular_dependency_system,
    contradiction_system,
    fully_pairable_system,
    missing_dual_system,
    non_convergent_system,
    oscillatory_system,
)


def _run(system, max_steps=8):
    return DualClosureOperator().run(system, max_steps=max_steps)


def test_stable_closed_fixed_point_is_detected():
    trace = _run(fully_pairable_system())
    assert trace.fixed_point_type == "stable_closed_fixed_point"
    assert trace.final_status == "closed_finite_dual_representation"


def test_stable_incomplete_fixed_point_is_detected():
    trace = _run(missing_dual_system())
    assert trace.fixed_point_type == "stable_incomplete_fixed_point"
    assert trace.final_status == "incomplete_finite_dual_representation"


def test_circular_dependency_does_not_falsely_converge_as_closed():
    trace = _run(circular_dependency_system())
    assert trace.fixed_point_type != "stable_closed_fixed_point"
    assert trace.final_status == "circular_dependency_flagged"
    failure_modes = {
        mode
        for node in trace.final_state["nodes"].values()
        for mode in node.get("metadata", {}).get("failure_modes", [])
    }
    assert "circular_dependency" in failure_modes


def test_contradiction_system_has_obstruction_status():
    trace = _run(contradiction_system())
    assert trace.final_status == "contradiction_or_paradox_boundary_flagged"
    assert trace.fixed_point_type == "stable_incomplete_fixed_point"


def test_oscillatory_system_is_distinguished_from_stable_fixed_point():
    trace = _run(oscillatory_system(), max_steps=6)
    assert trace.fixed_point_type == "oscillatory_system"
    assert trace.final_status == "oscillatory_finite_toy_system"


def test_non_convergent_system_is_distinguished_from_oscillation():
    trace = _run(non_convergent_system(), max_steps=4)
    assert trace.fixed_point_type == "non_convergent_system"
    assert trace.final_status == "non_convergent_finite_toy_system"

