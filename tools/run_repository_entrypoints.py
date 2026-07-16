"""Run canonical producer-local test and simulation entrypoints.

The runner deliberately selects the small canonical subject entrypoints created by
the architecture migration.  Historical long-running exploratory scripts remain
available as numerical backends, but are exercised through pytest and the contract
suites instead of being mistaken for the canonical theorem-complex runners.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "the_nothingness_effect"


def _subject_entrypoints(mode: str) -> list[tuple[Path, tuple[str, ...], str]]:
    if mode == "test":
        return [(path, (sys.executable, str(path)), "producer_local_test") for path in sorted(PACKAGE.glob("**/test/generate_artifacts.py"))]

    result: list[tuple[Path, tuple[str, ...], str]] = []
    for directory in sorted(PACKAGE.glob("**/simulation")):
        if not directory.is_dir() or "theoretical_benchmarks" in directory.parts:
            continue
        owner = directory.parent.name
        candidate = directory / f"simulate_{owner}.py"
        if not candidate.is_file():
            continue
        alternatives = (
            directory / "run_contract_suite.py",
            directory / "run_evidence.py",
            directory / "run_suite.py",
        )
        selected = next((path for path in alternatives if path.is_file()), None)
        if selected is not None:
            selected_module = selected.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
            result.append((candidate, (sys.executable, "-m", selected_module), "typed_contract_or_evidence_suite"))
        elif candidate.stat().st_size <= 2_000:
            result.append((candidate, (sys.executable, str(candidate)), "producer_local_simulation"))
        else:
            module = directory.parent.relative_to(ROOT).as_posix().replace("/", ".")
            result.append(
                (
                    candidate,
                    (sys.executable, str(Path(__file__).resolve()), "inventory", "--module", module),
                    "bounded_contract_inventory_fallback",
                )
            )
    return result


def _ai_entrypoints(mode: str) -> list[tuple[Path, tuple[str, ...], str]]:
    ai = PACKAGE / "artificial_intelligence"
    capability_names = (
        "color_classification",
        "sound_classification",
        "bidirectional_color_classification",
        "bidirectional_sound_classification",
        "color_cloning",
        "sound_cloning",
    )
    architecture_names = ("qenn", "pgqenn", "soinets")
    if mode == "test":
        capability = [ai / name / "test" / "test_capability.py" for name in capability_names]
        architecture = [ai / name / "test" / "run_all_capabilities.py" for name in architecture_names]
    else:
        capability = [ai / name / "simulation" / "run_simulation.py" for name in capability_names]
        architecture = [ai / name / "simulation" / "run_all_capabilities.py" for name in architecture_names]
    return [
        (path, (sys.executable, str(path)), "ai_six_output_or_capability_suite")
        for path in (*capability, *architecture)
        if path.is_file()
    ]


def _run(path: Path, command: tuple[str, ...], execution_kind: str, timeout: float) -> dict[str, object]:
    started = time.perf_counter()
    environment = dict(os.environ)
    environment.update({"MPLBACKEND": "Agg", "PYTHONHASHSEED": "0"})
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        status = "passed" if completed.returncode == 0 else "failed"
        return_code: int | None = completed.returncode
        output = (completed.stdout + completed.stderr).strip()
    except subprocess.TimeoutExpired as error:
        status = "timeout"
        return_code = None
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        output = (stdout + stderr).strip()
    portable_command = []
    for item in command:
        candidate = Path(item)
        if item == sys.executable:
            portable_command.append("<python>")
        elif candidate.is_absolute() and candidate.is_relative_to(ROOT):
            portable_command.append(candidate.relative_to(ROOT).as_posix())
        else:
            portable_command.append(str(item))
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "executed_command": portable_command,
        "execution_kind": execution_kind,
        "status": status,
        "return_code": return_code,
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "output_tail": "" if status == "passed" else output[-2000:].replace(str(ROOT), "<repository-root>").replace(sys.executable, "<python>"),
    }


def run(mode: str, output: Path, timeout: float) -> dict[str, object]:
    entries = (*_subject_entrypoints(mode), *_ai_entrypoints(mode))
    unique = {entry[0]: entry for entry in entries}
    results = [_run(path, command, execution_kind, timeout) for path, command, execution_kind in unique.values()]
    counts = {status: sum(item["status"] == status for item in results) for status in ("passed", "failed", "timeout")}
    payload = {
        "schema_version": "1.0",
        "mode": mode,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "seed": 0,
        "entrypoint_count": len(results),
        "summary": counts,
        "claim_boundary": "finite computational support; not a formal proof substitute",
        "entrypoints": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def run_inventory(module: str) -> Path:
    """Create bounded producer-local evidence when a legacy simulation is huge."""

    from importlib import import_module

    imported = import_module(module)
    subject_root = Path(imported.__file__).resolve().parent
    output = subject_root / "simulation" / "artifacts" / "bounded_contract_inventory.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    manifests = sorted((subject_root / "theorem_complex").glob("*/*/manifest.json"))
    payload = {
        "module": module,
        "seed": 0,
        "theorem_complexes": len(manifests),
        "simulation_mode": "bounded contract-inventory fallback for historical heavy renderer",
        "claim_boundary": "finite computational support; not a formal proof substitute",
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("test", "simulation", "inventory"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--module")
    arguments = parser.parse_args()
    if arguments.mode == "inventory":
        if not arguments.module:
            parser.error("inventory mode requires --module")
        run_inventory(arguments.module)
        raise SystemExit(0)
    destination = arguments.output or ROOT / "reports" / f"{arguments.mode}_execution_manifest.json"
    result = run(arguments.mode, destination.resolve(), arguments.timeout)
    print(json.dumps({"mode": result["mode"], "entrypoint_count": result["entrypoint_count"], **result["summary"]}, sort_keys=True))
    if result["summary"]["failed"] or result["summary"]["timeout"]:
        raise SystemExit(1)
