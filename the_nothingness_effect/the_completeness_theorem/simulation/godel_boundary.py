"""Deterministic finite toy systems for completeness-boundary artifacts."""

from __future__ import annotations

from the_nothingness_effect.the_completeness_theorem.models import (
    CLAIM_BOUNDARY,
    ClosureRule,
    FormalSystem,
    RuleType,
    StatementNode,
    StatementStatus,
)


def _node(
    node_id: str,
    label: str,
    status: StatementStatus,
    dual_id: str | None = None,
    **metadata: object,
) -> StatementNode:
    return StatementNode(
        id=node_id,
        label=label,
        status=status,
        dual_id=dual_id,
        metadata=dict(metadata),
    )


def godel_boundary_system() -> FormalSystem:
    """Return a finite illustrative boundary graph.

    The system is a repository-linked supplementary simulation, not a direct
    simulation of Godel's theorems and not a formal proof substitute.
    """

    nodes = {
        "axiom_base": _node(
            "axiom_base",
            "Finite toy axiom base",
            StatementStatus.PROVABLE,
            "axiom_base_dual",
        ),
        "axiom_base_dual": _node(
            "axiom_base_dual",
            "Represented dual of axiom base",
            StatementStatus.DUAL_COMPLEMENT,
            "axiom_base",
        ),
        "godel_like_statement": _node(
            "godel_like_statement",
            "Boundary-like undecidable statement",
            StatementStatus.UNPROVABLE_WITHIN_SYSTEM,
            "represented_dual_statement",
            boundary_like=True,
            interpretation="unprovable_within_system is not treated as false",
        ),
        "represented_dual_statement": _node(
            "represented_dual_statement",
            "Represented dual counterpart",
            StatementStatus.DUAL_COMPLEMENT,
            "godel_like_statement",
        ),
        "paradox_boundary_marker": _node(
            "paradox_boundary_marker",
            "Boundary classification marker",
            StatementStatus.PARADOX_BOUNDARY,
            None,
            boundary_like=True,
        ),
        "open_context": _node(
            "open_context",
            "Open finite context node",
            StatementStatus.OPEN,
            None,
        ),
    }
    return FormalSystem(
        name="godel_boundary",
        nodes=nodes,
        edges=[
            ("axiom_base", "godel_like_statement", "derivation frontier"),
            ("godel_like_statement", "paradox_boundary_marker", "boundary flag"),
            ("godel_like_statement", "represented_dual_statement", "represented dual"),
            ("open_context", "godel_like_statement", "finite context"),
        ],
        metadata={
            "description": (
                "Finite illustrative dual-closure boundary graph for manuscript "
                "computational support artifacts."
            ),
            "scope_note": CLAIM_BOUNDARY,
        },
    )


def fully_pairable_system() -> FormalSystem:
    nodes = {
        "p": _node("p", "Statement p", StatementStatus.OPEN, "not_p"),
        "not_p": _node("not_p", "Represented dual of p", StatementStatus.OPEN, "p"),
        "q": _node("q", "Statement q", StatementStatus.OPEN, "not_q"),
        "not_q": _node("not_q", "Represented dual of q", StatementStatus.OPEN, "q"),
    }
    return FormalSystem(
        name="fully_pairable_system",
        nodes=nodes,
        edges=[("p", "not_p", "dual"), ("q", "not_q", "dual")],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def missing_dual_system() -> FormalSystem:
    nodes = {
        "p": _node("p", "Statement p", StatementStatus.OPEN, "not_p"),
        "not_p": _node("not_p", "Represented dual of p", StatementStatus.OPEN, "p"),
        "q": _node("q", "Statement q lacking represented dual", StatementStatus.OPEN, "not_q"),
    }
    return FormalSystem(
        name="missing_dual_system",
        nodes=nodes,
        edges=[("p", "not_p", "dual"), ("q", "not_q", "missing dual")],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def circular_dependency_system() -> FormalSystem:
    nodes = {
        "p": _node(
            "p",
            "Statement p requiring q closure",
            StatementStatus.OPEN,
            "not_p",
            requires_closed=["q"],
        ),
        "not_p": _node(
            "not_p",
            "Represented dual of p requiring not_q closure",
            StatementStatus.OPEN,
            "p",
            requires_closed=["not_q"],
        ),
        "q": _node(
            "q",
            "Statement q requiring p closure",
            StatementStatus.OPEN,
            "not_q",
            requires_closed=["p"],
        ),
        "not_q": _node(
            "not_q",
            "Represented dual of q requiring not_p closure",
            StatementStatus.OPEN,
            "q",
            requires_closed=["not_p"],
        ),
    }
    return FormalSystem(
        name="circular_dependency_system",
        nodes=nodes,
        edges=[
            ("p", "q", "requires closed"),
            ("q", "p", "requires closed"),
            ("not_p", "not_q", "requires closed"),
            ("not_q", "not_p", "requires closed"),
        ],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def contradiction_system() -> FormalSystem:
    nodes = {
        "p": _node(
            "p",
            "Provable statement p in finite toy system",
            StatementStatus.PROVABLE,
            "not_p",
            contradicts=["not_p"],
        ),
        "not_p": _node(
            "not_p",
            "Provable anti-statement in naive closure",
            StatementStatus.PROVABLE,
            "p",
            contradicts=["p"],
        ),
    }
    return FormalSystem(
        name="contradiction_system",
        nodes=nodes,
        edges=[("p", "not_p", "contradiction boundary")],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def unpaired_boundary_system() -> FormalSystem:
    nodes = {
        "g": _node(
            "g",
            "Boundary-like unpaired statement",
            StatementStatus.UNPROVABLE_WITHIN_SYSTEM,
            "not_g",
            boundary_like=True,
            interpretation="boundary classification remains distinct from proof",
        ),
        "context": _node(
            "context",
            "Finite context node",
            StatementStatus.PROVABLE,
            "context_dual",
        ),
        "context_dual": _node(
            "context_dual",
            "Represented context dual",
            StatementStatus.DUAL_COMPLEMENT,
            "context",
        ),
    }
    return FormalSystem(
        name="unpaired_boundary_system",
        nodes=nodes,
        edges=[("context", "g", "finite boundary relation")],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def oscillatory_system() -> FormalSystem:
    nodes = {
        "osc": _node("osc", "Oscillating finite toy node", StatementStatus.OPEN, None),
    }
    return FormalSystem(
        name="oscillatory_system",
        nodes=nodes,
        rules=[
            ClosureRule(
                id="toggle_osc",
                target_id="osc",
                rule_type=RuleType.TOGGLE_STATUS,
                description="Finite toy oscillation for fixed-point detection tests.",
            )
        ],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def non_convergent_system() -> FormalSystem:
    nodes = {
        "drift": _node(
            "drift",
            "Drifting unresolved finite toy node",
            StatementStatus.UNRESOLVED,
            None,
        ),
    }
    return FormalSystem(
        name="non_convergent_system",
        nodes=nodes,
        rules=[
            ClosureRule(
                id="drift_unresolved",
                target_id="drift",
                rule_type=RuleType.DRIFT_UNRESOLVED,
                description="Finite toy drift for non-convergence detection tests.",
            )
        ],
        metadata={"scope_note": CLAIM_BOUNDARY},
    )


def supplementary_systems() -> list[FormalSystem]:
    return [
        godel_boundary_system(),
        fully_pairable_system(),
        missing_dual_system(),
        circular_dependency_system(),
        contradiction_system(),
        unpaired_boundary_system(),
    ]

