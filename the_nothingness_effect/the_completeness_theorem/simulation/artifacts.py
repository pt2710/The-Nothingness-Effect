"""Artifact writers for finite completeness supplementary simulations."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from the_nothingness_effect.the_completeness_theorem.models import CLAIM_BOUNDARY
from the_nothingness_effect.the_completeness_theorem.simulation.dual_closure import ClosureTrace


TRACE_FILENAMES = {
    "godel_boundary": "godel_boundary_trace.json",
    "fully_pairable_system": "fully_pairable_system_trace.json",
    "missing_dual_system": "missing_dual_system_trace.json",
    "circular_dependency_system": "circular_dependency_system_trace.json",
    "contradiction_system": "contradiction_system_trace.json",
    "unpaired_boundary_system": "unpaired_boundary_system_trace.json",
}


def supplementary_root() -> Path:
    return Path(__file__).resolve().parent / "artifacts" / "supplementary"


def prepare_output_dirs(output_root: Path | None = None) -> dict[str, Path]:
    root = output_root or supplementary_root()
    dirs = {
        "root": root,
        "traces": root / "traces",
        "metrics": root / "metrics",
        "figures": root / "figures",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def write_trace(trace: ClosureTrace, traces_dir: Path) -> Path:
    filename = TRACE_FILENAMES.get(trace.system_name, f"{trace.system_name}_trace.json")
    path = traces_dir / filename
    path.write_text(
        json.dumps(trace.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def write_traces(traces: list[ClosureTrace], traces_dir: Path) -> list[Path]:
    return [write_trace(trace, traces_dir) for trace in traces]


def write_metrics(traces: list[ClosureTrace], metrics_dir: Path) -> list[Path]:
    paths = [
        _write_iteration_metrics(traces, metrics_dir / "closure_iteration_metrics.csv"),
        _write_pair_coverage(traces, metrics_dir / "duality_pair_coverage.csv"),
        _write_failure_modes(traces, metrics_dir / "closure_failure_modes.csv"),
        _write_fixed_point_summary(traces, metrics_dir / "fixed_point_summary.csv"),
    ]
    return paths


def _write_iteration_metrics(traces: list[ClosureTrace], path: Path) -> Path:
    rows: list[dict[str, Any]] = []
    for trace in traces:
        rows.extend(trace.metrics)
    fieldnames = [
        "system_name",
        "step",
        "changed_count",
        "changed_nodes",
        "closed_count",
        "unresolved_count",
        "boundary_count",
        "contradiction_count",
        "provable_count",
        "formally_proved_count",
        "verified_dual_percent",
        "failure_modes",
        "scope_note",
    ]
    _write_csv(path, fieldnames, rows)
    return path


def _write_pair_coverage(traces: list[ClosureTrace], path: Path) -> Path:
    rows = []
    for trace in traces:
        final_state = trace.final_state
        nodes = final_state["nodes"]
        verified = 0
        for node_id, node in nodes.items():
            dual_id = node.get("dual_id")
            if dual_id in nodes and nodes[dual_id].get("dual_id") == node_id:
                verified += 1
        total = len(nodes)
        rows.append(
            {
                "system_name": trace.system_name,
                "node_count": total,
                "verified_dual_nodes": verified,
                "verified_dual_percent": 0.0 if total == 0 else round((verified / total) * 100, 2),
                "scope_note": CLAIM_BOUNDARY,
            }
        )
    _write_csv(
        path,
        [
            "system_name",
            "node_count",
            "verified_dual_nodes",
            "verified_dual_percent",
            "scope_note",
        ],
        rows,
    )
    return path


def _write_failure_modes(traces: list[ClosureTrace], path: Path) -> Path:
    columns = [
        "missing_dual",
        "circular_dependency",
        "contradiction",
        "unpaired_boundary",
        "unresolved_open_state",
        "paradox_boundary",
    ]
    rows = []
    for trace in traces:
        nodes = trace.final_state["nodes"].values()
        modes = set()
        statuses = []
        for node in nodes:
            modes.update(node.get("metadata", {}).get("failure_modes", []))
            statuses.append(node.get("status"))
        rows.append(
            {
                "system_name": trace.system_name,
                "missing_dual": int("missing_dual" in modes),
                "circular_dependency": int("circular_dependency" in modes),
                "contradiction": int("contradiction" in modes),
                "unpaired_boundary": int("unpaired_boundary" in modes),
                "unresolved_open_state": int(
                    any(status in {"open", "unresolved", "closure_candidate"} for status in statuses)
                ),
                "paradox_boundary": int(any(status == "paradox_boundary" for status in statuses)),
                "scope_note": CLAIM_BOUNDARY,
            }
        )
    _write_csv(path, ["system_name", *columns, "scope_note"], rows)
    return path


def _write_fixed_point_summary(traces: list[ClosureTrace], path: Path) -> Path:
    rows = []
    for trace in traces:
        final_metrics = trace.metrics[-1]
        rows.append(
            {
                "system_name": trace.system_name,
                "fixed_point_type": trace.fixed_point_type,
                "final_status": trace.final_status,
                "step_count": len(trace.steps),
                "closed_count": final_metrics["closed_count"],
                "unresolved_count": final_metrics["unresolved_count"],
                "boundary_count": final_metrics["boundary_count"],
                "contradiction_count": final_metrics["contradiction_count"],
                "verified_dual_percent": final_metrics["verified_dual_percent"],
                "scope_note": CLAIM_BOUNDARY,
            }
        )
    _write_csv(
        path,
        [
            "system_name",
            "fixed_point_type",
            "final_status",
            "step_count",
            "closed_count",
            "unresolved_count",
            "boundary_count",
            "contradiction_count",
            "verified_dual_percent",
            "scope_note",
        ],
        rows,
    )
    return path


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            serialized = {}
            for key in fieldnames:
                value = row.get(key, "")
                if isinstance(value, (list, tuple, set)):
                    value = "|".join(str(item) for item in value)
                serialized[key] = value
            writer.writerow(serialized)

