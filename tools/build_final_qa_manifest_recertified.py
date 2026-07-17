"""Build final QA with explicit provenance and execution-evidence semantics."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect._runtime.theorem_complex_runtime.provenance_authority import (
    bind_provenance_manifest,
    provenance_binding_report,
)
from tools import build_final_qa_manifest as _base


# The preserved final-QA builder imports the historical authority API. Replace
# only its provenance hooks with the observational, recertification-aware API.
_base.bind_provenance_manifest = bind_provenance_manifest
_base.provenance_binding_report = provenance_binding_report


_EXECUTION_CLASSES = {
    "producer_local_simulation": "actual_simulation",
    "ai_six_output_or_capability_suite": "actual_simulation",
    "typed_contract_or_evidence_suite": "contract_evidence",
    "bounded_contract_inventory_fallback": "inventory_fallback",
}


def _status_summary(entries: list[dict[str, Any]]) -> dict[str, object]:
    statuses = Counter(str(item.get("status", "unknown")) for item in entries)
    return {
        "entrypoints": len(entries),
        "passed": statuses.get("passed", 0),
        "failed": statuses.get("failed", 0),
        "timeout": statuses.get("timeout", 0),
        "other": sum(
            count
            for status, count in statuses.items()
            if status not in {"passed", "failed", "timeout"}
        ),
        "runtime_seconds": sum(float(item.get("runtime_seconds", 0.0)) for item in entries),
        "paths": [str(item.get("path", "")) for item in entries],
    }


def classify_simulation_evidence(
    manifest: dict[str, Any],
) -> dict[str, object]:
    """Separate actual simulations, contract evidence and inventory fallbacks."""

    raw_entries = manifest.get("entrypoints")
    if not isinstance(raw_entries, list):
        raise RuntimeError("simulation execution manifest lacks entrypoint list")
    grouped: dict[str, list[dict[str, Any]]] = {
        "actual_simulation": [],
        "contract_evidence": [],
        "inventory_fallback": [],
        "unknown": [],
    }
    for item in raw_entries:
        if not isinstance(item, dict):
            raise RuntimeError("simulation execution entry must be an object")
        target = _EXECUTION_CLASSES.get(str(item.get("execution_kind", "")), "unknown")
        grouped[target].append(item)

    summaries = {name: _status_summary(entries) for name, entries in grouped.items()}
    classified_total = sum(int(summary["entrypoints"]) for summary in summaries.values())
    if classified_total != len(raw_entries):
        raise RuntimeError("simulation evidence classification cardinality mismatch")
    return {
        "schema_version": "1.0",
        "registered_entrypoints": len(raw_entries),
        "actual_simulation": summaries["actual_simulation"],
        "contract_evidence": summaries["contract_evidence"],
        "inventory_fallback": summaries["inventory_fallback"],
        "unknown": summaries["unknown"],
        "all_entrypoints_classified": int(summaries["unknown"]["entrypoints"]) == 0,
        "policy": (
            "bounded_contract_inventory_fallback is inventory evidence and is not "
            "counted as a simulation; typed contract suites are contract evidence"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/data/final_qa_manifest.json"),
    )
    parser.add_argument("--passed", type=int)
    parser.add_argument("--failed", type=int)
    parser.add_argument("--skipped", type=int)
    parser.add_argument("--warnings", type=int)
    parser.add_argument("--runtime-seconds", type=float)
    parser.add_argument("--python-version", default="3.14.3")
    parser.add_argument(
        "--dependency-status",
        default="pip check passed",
    )
    parser.add_argument(
        "--source-law-regression-status",
        default="passed",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when any release blocker is present.",
    )
    arguments = parser.parse_args()

    payload = _base.build(arguments)
    simulation_manifest = json.loads(
        Path("reports/simulation_execution_manifest.json").read_text(encoding="utf-8")
    )
    classification = classify_simulation_evidence(simulation_manifest)
    entrypoint_execution = payload.setdefault("entrypoint_execution", {})
    if not isinstance(entrypoint_execution, dict):
        raise RuntimeError("final QA entrypoint execution record is invalid")
    legacy_summary = entrypoint_execution.get("simulation", {})
    entrypoint_execution["registered_simulation_paths"] = legacy_summary
    entrypoint_execution["simulation"] = classification["actual_simulation"]
    entrypoint_execution["contract_evidence"] = classification["contract_evidence"]
    entrypoint_execution["inventory_fallback"] = classification["inventory_fallback"]
    entrypoint_execution["unknown_execution_kind"] = classification["unknown"]
    entrypoint_execution["classification_policy"] = classification["policy"]

    blockers = payload.setdefault("release_blockers", [])
    if not isinstance(blockers, list):
        raise RuntimeError("final QA release blockers record is invalid")
    if not bool(classification["all_entrypoints_classified"]):
        blockers.append("unknown_simulation_execution_kind")
    payload["release_blockers"] = sorted(set(str(item) for item in blockers))
    payload["final_qa_passed"] = not payload["release_blockers"]
    payload["schema_version"] = "1.4"
    payload["execution_evidence_claim_boundary"] = (
        "Only producer-local simulations and AI capability runs are counted as "
        "simulations. Typed contract suites and inventory fallbacks remain separate."
    )

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"final_qa_manifest={arguments.output} "
        f"final_qa_passed={payload['final_qa_passed']} "
        f"actual_simulations={classification['actual_simulation']['entrypoints']} "
        f"inventory_fallbacks={classification['inventory_fallback']['entrypoints']} "
        f"release_blockers={payload['release_blockers']}"
    )
    return 1 if arguments.check and not payload["final_qa_passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
