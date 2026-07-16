"""Figure generation for finite dual-closure supplementary artifacts."""

from __future__ import annotations

from pathlib import Path
from textwrap import shorten

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import ClosureTrace


STATUS_COLORS = {
    "provable": "#4c78a8",
    "formally_proved": "#1f4e79",
    "unprovable_within_system": "#f58518",
    "dual_complement": "#72b7b2",
    "closure_candidate": "#54a24b",
    "closed": "#2f7d32",
    "open": "#bab0ac",
    "paradox_boundary": "#b279a2",
    "contradiction": "#e45756",
    "unresolved": "#ffbf79",
}


def save_godel_boundary_figures(trace: ClosureTrace, figures_dir: Path) -> list[Path]:
    return [
        draw_godel_boundary_graph(trace, figures_dir / "godel_boundary_graph.png"),
        draw_dual_closure_lattice(figures_dir / "dual_closure_lattice.png"),
        draw_closure_iteration_trace(trace, figures_dir / "closure_iteration_trace.png"),
        draw_incompleteness_phase(figures_dir / "incompleteness_vs_dual_closure_phase.png"),
    ]


def save_supplementary_figures(traces: list[ClosureTrace], figures_dir: Path) -> list[Path]:
    return [
        draw_closure_fixed_point_trace(traces, figures_dir / "closure_fixed_point_trace.png"),
        draw_duality_pair_coverage(traces, figures_dir / "duality_pair_coverage.png"),
        draw_closure_failure_modes(traces, figures_dir / "closure_failure_modes.png"),
        draw_completeness_operator_convergence(
            traces, figures_dir / "completeness_operator_convergence.png"
        ),
        draw_closure_state_space_projection(
            traces, figures_dir / "closure_state_space_projection.png"
        ),
    ]


def draw_godel_boundary_graph(trace: ClosureTrace, path: Path) -> Path:
    graph = nx.DiGraph()
    initial = trace.initial_state
    nodes = initial["nodes"]
    for node_id, node in nodes.items():
        graph.add_node(node_id, label=node["label"], status=node["status"])
    for source, target, label in initial["edges"]:
        if source in graph and target in graph:
            graph.add_edge(source, target, label=label)

    positions = {
        "axiom_base": (-1.4, 0.5),
        "axiom_base_dual": (-1.4, -0.45),
        "godel_like_statement": (0.0, 0.45),
        "represented_dual_statement": (0.0, -0.45),
        "paradox_boundary_marker": (1.4, 0.45),
        "open_context": (1.4, -0.45),
    }
    colors = [STATUS_COLORS[graph.nodes[node]["status"]] for node in graph.nodes]
    labels = {
        node_id: shorten(data["label"], width=28, placeholder="...")
        for node_id, data in graph.nodes(data=True)
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw_networkx_nodes(graph, positions, node_color=colors, node_size=2200, ax=ax)
    nx.draw_networkx_edges(graph, positions, arrows=True, arrowstyle="-|>", width=1.4, ax=ax)
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=8, ax=ax)
    edge_labels = nx.get_edge_attributes(graph, "label")
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_size=7, ax=ax)
    _status_legend(ax)
    ax.set_title("Finite illustrative dual-closure boundary graph\nNot a formal proof substitute")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_dual_closure_lattice(path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    boxes = {
        "statement": (0.2, 0.75, "Statement"),
        "dual": (0.8, 0.75, "Represented dual"),
        "candidate": (0.5, 0.45, "Closure candidate"),
        "closed": (0.5, 0.15, "Representational\nclosed pair"),
    }
    for _, (x, y, label) in boxes.items():
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.35", "fc": "#f4f4f4", "ec": "#333333"},
            fontsize=10,
        )
    arrows = [
        ((0.2, 0.7), (0.46, 0.5)),
        ((0.8, 0.7), (0.54, 0.5)),
        ((0.5, 0.38), (0.5, 0.23)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.5})
    ax.text(
        0.5,
        0.02,
        "Closure requires paired representation in this finite toy system.",
        ha="center",
        va="bottom",
        fontsize=9,
    )
    ax.set_title("Finite illustrative dual-closure lattice\nNot a formal proof substitute")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_closure_iteration_trace(trace: ClosureTrace, path: Path) -> Path:
    metrics = trace.metrics
    steps = [row["step"] for row in metrics]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(steps, [row["closed_count"] for row in metrics], marker="o", label="closed")
    ax.plot(steps, [row["unresolved_count"] for row in metrics], marker="o", label="unresolved")
    ax.plot(steps, [row["boundary_count"] for row in metrics], marker="o", label="boundary")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Node count")
    ax.set_title("Toy-model closure trace\nFinite illustrative model")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_incompleteness_phase(path: Path) -> Path:
    states = ["open", "boundary", "paired", "closed"]
    values = np.array(
        [
            [1.0, 0.8, 0.4, 0.2],
            [0.9, 1.0, 0.6, 0.4],
            [0.5, 0.6, 0.3, 0.1],
            [0.3, 0.4, 0.1, 0.0],
        ]
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(values, cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(states)), states, rotation=30, ha="right")
    ax.set_yticks(range(len(states)), states)
    ax.set_title("Incompleteness vs dual-closure phase map\nFinite toy state classification")
    ax.set_xlabel("Represented dual-closure state")
    ax.set_ylabel("Boundary state")
    fig.colorbar(image, ax=ax, label="Illustrative unresolved intensity")
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_closure_fixed_point_trace(traces: list[ClosureTrace], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))
    for trace in traces:
        steps = [row["step"] for row in trace.metrics]
        unresolved = [row["unresolved_count"] for row in trace.metrics]
        closed = [row["closed_count"] for row in trace.metrics]
        ax.plot(steps, unresolved, marker="o", linewidth=1.5, label=f"{trace.system_name} unresolved")
        ax.plot(steps, closed, linestyle="--", linewidth=1.3, label=f"{trace.system_name} closed")
        if trace.fixed_point_type == "stable_closed_fixed_point":
            ax.scatter(steps[-1], closed[-1], s=80, marker="*", color="#2f7d32", zorder=5)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Node count")
    ax.set_title("Closure fixed-point trace for finite toy systems")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_duality_pair_coverage(traces: list[ClosureTrace], path: Path) -> Path:
    names = [trace.system_name for trace in traces]
    coverage = [trace.metrics[-1]["verified_dual_percent"] for trace in traces]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(names, coverage, color="#4c78a8")
    ax.set_ylim(0, 105)
    ax.set_ylabel("Verified dual counterpart coverage (%)")
    ax.set_title("Duality pair coverage in finite toy systems")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_closure_failure_modes(traces: list[ClosureTrace], path: Path) -> Path:
    mode_names = [
        "missing_dual",
        "circular_dependency",
        "contradiction",
        "unpaired_boundary",
        "unresolved_dependency",
    ]
    values = {mode: 0 for mode in mode_names}
    for trace in traces:
        for node in trace.final_state["nodes"].values():
            for mode in node.get("metadata", {}).get("failure_modes", []):
                if mode in values:
                    values[mode] += 1
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(values.keys(), values.values(), color="#e45756")
    ax.set_ylabel("Flagged node count")
    ax.set_title("Closure failure modes in finite supplementary simulations")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_completeness_operator_convergence(traces: list[ClosureTrace], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))
    for trace in traces:
        steps = [row["step"] for row in trace.metrics]
        changed = [row["changed_count"] for row in trace.metrics]
        ax.plot(steps, changed, marker="o", label=trace.system_name)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Changed node count")
    ax.set_title("Finite completeness-operator convergence trace")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def draw_closure_state_space_projection(traces: list[ClosureTrace], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))
    for trace in traces:
        final = trace.metrics[-1]
        x_value = final["closed_count"]
        y_value = (
            final["unresolved_count"]
            + final["boundary_count"]
            + final["contradiction_count"]
        )
        ax.scatter(x_value, y_value, s=90, label=trace.system_name)
        ax.annotate(trace.system_name, (x_value + 0.04, y_value + 0.04), fontsize=8)
    ax.set_xlabel("Closed represented-pair node count")
    ax.set_ylabel("Open, boundary, or contradiction count")
    ax.set_title("Closure state-space projection\nDeterministic finite toy systems")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=250)
    plt.close(fig)
    return path


def _status_legend(ax: plt.Axes) -> None:
    handles = []
    labels = []
    for status, color in STATUS_COLORS.items():
        if status in {
            "provable",
            "unprovable_within_system",
            "dual_complement",
            "closure_candidate",
            "open",
            "paradox_boundary",
        }:
            handles.append(
                plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=9)
            )
            labels.append(status)
    ax.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.08), ncol=3, fontsize=7)

