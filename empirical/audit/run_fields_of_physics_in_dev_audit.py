"""Audit the fields_of_physics_in_dev tree for safe reuse recommendations."""

from __future__ import annotations

import argparse
import ast
import json
import warnings
from pathlib import Path
from typing import Any

from equations.artifact_io import save_json
from empirical.io import write_report


RECOMMENDED_ACTIONS = {
    "keep_experimental",
    "integrate_now",
    "integrate_later",
    "migrate_to_equations",
    "add_tests",
    "add_simulation_script",
    "remove_duplicate",
    "archive",
    "no_action",
}

AUDIT_TARGETS: list[dict[str, str]] = [
    {
        "path": "fields_of_physics_in_dev/general_relativity/gravitational_curvature",
        "category": "general_relativity",
        "reusable_for": "black_hole_dynamics|locality_driven_gravity|eht_mapping",
        "recommended_action": "integrate_later",
        "risk_level": "high",
        "notes": "Interesting curvature/galaxy ideas, but current module depends on legacy root imports and contains heavy ad hoc simulation code.",
    },
    {
        "path": "fields_of_physics_in_dev/general_relativity/three_body_problem",
        "category": "general_relativity",
        "reusable_for": "future_dynamics_work",
        "recommended_action": "keep_experimental",
        "risk_level": "medium",
        "notes": "Separate prototype; no direct Run 6 dependency.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/entanglement",
        "category": "quantum_mechanics",
        "reusable_for": "future_quantum_module",
        "recommended_action": "keep_experimental",
        "risk_level": "high",
        "notes": "No direct dependency on current empirical mappings; keep isolated until a dedicated quantum module is specified.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/fp_particle_models",
        "category": "quantum_mechanics",
        "reusable_for": "future_particle_models",
        "recommended_action": "keep_experimental",
        "risk_level": "medium",
        "notes": "Not directly useful for Run 6 empirical or Hawking work.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/quantum_uncertainty",
        "category": "quantum_mechanics",
        "reusable_for": "future_framework_text",
        "recommended_action": "no_action",
        "risk_level": "low",
        "notes": "Framework text only; no direct code integration target.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_pi_wave",
        "category": "wave_functionality",
        "reusable_for": "elastic_pi_ripples|ringdown_projection|hawking_spectrum_proxy",
        "recommended_action": "integrate_now",
        "risk_level": "medium",
        "notes": "Core fp_pi wave concept was selectively integrated into equations/elastic_pi_ripples/wave_adapters.py with tests.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_sine_wave",
        "category": "wave_functionality",
        "reusable_for": "ringdown_projection|wave_helpers",
        "recommended_action": "integrate_now",
        "risk_level": "medium",
        "notes": "Sine-wave helper concept was selectively integrated into equations/elastic_pi_ripples/wave_adapters.py with tests.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_wave_Interference",
        "category": "wave_functionality",
        "reusable_for": "elastic_pi_ripples|ringdown_projection|observer_memory_wavefronts",
        "recommended_action": "integrate_now",
        "risk_level": "medium",
        "notes": "Interference concept was selectively integrated into equations/elastic_pi_ripples/wave_adapters.py with tests.",
    },
    {
        "path": "fields_of_physics_in_dev/quantum_mechanics/wave_functionality/fp_waves",
        "category": "wave_functionality",
        "reusable_for": "future_wave_visuals",
        "recommended_action": "integrate_later",
        "risk_level": "medium",
        "notes": "Useful visual ideas, but current module executes plotting at import time and is not directly wired into Run 6.",
    },
    {
        "path": "fields_of_physics_in_dev/thermodynamics",
        "category": "thermodynamics",
        "reusable_for": "future_entropic_modules",
        "recommended_action": "keep_experimental",
        "risk_level": "medium",
        "notes": "Not directly required for current empirical comparison work.",
    },
]


def _non_init_files(path: Path) -> list[Path]:
    return [item for item in path.glob("*") if item.is_file() and item.name != "__init__.py"]


def _folder_has_outputs(path: Path, folder_name: str) -> bool:
    folder = path / folder_name
    if not folder.exists():
        return False
    return any(item.name != "__init__.py" for item in folder.rglob("*") if item.is_file())


def _module_status(path: Path) -> tuple[str, str]:
    py_files = [item for item in path.glob("*.py") if item.name != "__init__.py"]
    if not py_files:
        return "support_only", "No primary implementation module found at folder root."
    source = py_files[0].read_text(encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(source)
    guarded = "if __name__ == \"__main__\"" in source or "if __name__ == '__main__'" in source
    top_level_calls = [
        node
        for node in tree.body
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
    ]
    if top_level_calls and not guarded:
        return "prototype", "Primary module executes side effects at import time."
    return "module_present", "Primary module exists without obvious import-time side effects."


def run() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for target in AUDIT_TARGETS:
        path = Path(target["path"])
        status, status_note = _module_status(path)
        rows.append(
            {
                "path": target["path"],
                "category": target["category"],
                "status": status,
                "has_tests": _folder_has_outputs(path, "test"),
                "has_simulation_output": _folder_has_outputs(path, "simulation"),
                "reusable_for": target["reusable_for"],
                "recommended_action": target["recommended_action"],
                "risk_level": target["risk_level"],
                "notes": f"{target['notes']} {status_note}".strip(),
            }
        )

    csv_path = Path("fields_of_physics_in_dev_audit.csv")
    json_path = Path("fields_of_physics_in_dev_audit.json")
    report_path = Path("docs/fields_of_physics_in_dev_audit.md")

    import csv

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    save_json(
        json_path,
        {
            "rows": rows,
            "recommended_actions": sorted(RECOMMENDED_ACTIONS),
        },
    )

    lines = [
        "# fields_of_physics_in_dev Audit",
        "",
        "This audit reviews the development-only physics folders for Run 6 reuse opportunities. Recommendations are conservative and focus on tested, directly useful integration only.",
        "",
        "## Summary",
        "",
        "| Path | Status | Tests | Simulation Output | Recommended Action | Risk |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['path']} | {row['status']} | {row['has_tests']} | "
            f"{row['has_simulation_output']} | {row['recommended_action']} | {row['risk_level']} |"
        )
    lines.extend(
        [
            "",
            "## Integrated Now",
            "",
            "- `fp_pi_wave`, `fp_sine_wave`, and `fp_wave_Interference` concepts were selectively integrated into `equations/elastic_pi_ripples/wave_adapters.py` for ringdown/spectral proxy helpers.",
            "",
            "## Deferred / Experimental",
            "",
            "- `gravitational_curvature` remains deferred because of legacy root imports, heavy ad hoc simulation assumptions, and missing isolation from side effects.",
            "- entanglement, fp-particle, and thermodynamics modules remain experimental until a direct dependency or dedicated physics task requires them.",
            "",
            "## Run 6 Note",
            "",
            "Run 6 improves observable mappings and residual diagnostics. It does not establish empirical validation of TNE. Improved fit metrics, if any, are preliminary model-to-observable comparison results under explicit proxy mappings.",
        ]
    )
    write_report(report_path, "\n".join(lines))
    return {"rows": rows, "csv": csv_path, "json": json_path, "report": report_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit fields_of_physics_in_dev for safe reuse recommendations.")
    parser.parse_args(argv)
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
