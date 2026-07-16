"""Fail-closed verifier for the canonical TNE repository architecture.

The verifier uses only repository metadata at runtime.  Passing an external
appendix directory enables the stronger source-content comparison used during
development and release QA; appendix files are never opened by package code.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
import sys
import tempfile
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "the_nothingness_effect"
MASTER_MANIFEST = ROOT / "reports" / "theorem_complex_manifest.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TOP_PACKAGES = (
    "canonical_self_negating_involution",
    "mathematical_architecture",
    "foundational_architecture",
    "fluctuation_and_elastic_dynamics",
    "gravitational_cosmological_and_quantum_dynamics_architecture",
    "artificial_intelligence",
    "the_completeness_theorem",
)

SUBJECT_PATHS = (
    "canonical_self_negating_involution/the_flowpoint",
    "mathematical_architecture",
    "mathematical_architecture/flowpoint_pi_approximation",
    "mathematical_architecture/flowpoint_math_operations",
    "mathematical_architecture/flowpoint_trigonometry",
    "foundational_architecture/duality",
    "foundational_architecture/symmetry",
    "foundational_architecture/spatiality",
    "foundational_architecture/countable_infinity",
    "foundational_architecture/uncountable_infinity",
    "foundational_architecture/the_spectrum_of_infinities",
    "foundational_architecture/observation_and_collapse",
    "fluctuation_and_elastic_dynamics/dynamic_fluctuation_index",
    "fluctuation_and_elastic_dynamics/parity_adapted_dynamic_fluctuation_index",
    "fluctuation_and_elastic_dynamics/elastic_pi",
    "fluctuation_and_elastic_dynamics/elastic_pi_norm",
    "gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect",
    "gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature",
    "gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity",
    "gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons",
    "gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts",
    "gravitational_cosmological_and_quantum_dynamics_architecture/emergent_cosmological_spark_dynamics",
    "gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint",
    "artificial_intelligence/qenn",
    "artificial_intelligence/pgqenn",
    "artificial_intelligence/soinets",
    "the_completeness_theorem",
    "the_completeness_theorem/noether_structure",
)

OBSOLETE_PATHS = (
    "the_nothingness_effect/equations",
    "the_nothingness_effect/tne_concepts",
    "the_nothingness_effect/mccrackns_prime_law",
    "the_nothingness_effect/numbers_domains",
    "the_nothingness_effect/figures",
    "figures",
    "figures_mccrackn",
    "theoretical_benchmarks",
)

APPENDIX_NAMES = {
    "appendix_canonical_self_negating_involution_flowpoint.tex",
    "appendix_tne_mathematical_closure_architecture.tex",
    "appendix_tne_foundational_closure_architecture.tex",
    "appendix_tne_fluctuation_and_elastic_dynamics.tex",
    "appendix_tne_gravitational_cosmological_quantum_dynamics.tex",
    "appendix_tne_gravitational_cosmological_and_quantum_dynamics.tex",
    "appendix_tne_artificial_intelligence_architechture.tex",
    "appendix_the_completeness_theorem.tex",
}

APPENDIX_HASHES = {
    "5c44d82b34cd4c5d05d01253a62987f2f6099d582bf954a4cbdbc13b52b52206",
    "3f428e24ed9518655f94145dcd8667f979aa03c74f75695d8273da273e2538d0",
    "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea",
    "63e5684e4c4bb016a2cc62d46574c2174fbe14eb5f50c16db825ca33b0836389",
    "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062",
    "3a75d4bfdbf9779255d01dd3ae3db6a848a4dc1fa67455ca1f22d5abcadf866a",
    "d711e5c4260fb61bff1ef3e7ea3be14ef093370a9ff22607d2a54e74ba8b166b",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    return [ROOT / item.decode("utf-8") for item in result.split(b"\0") if item]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module_name(path: Path) -> str:
    return path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")


def is_absolute_string(value: str) -> bool:
    if value.lower().startswith(("http://", "https://")):
        return False
    return (
        PureWindowsPath(value).is_absolute()
        or PurePosixPath(value).is_absolute()
        or bool(re.search(r"[A-Za-z]:[/\\]", value))
        or "file:///" in value.lower()
    )


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from strings(nested)


class Verification:
    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def check(self, number: int, name: str, action: Callable[[], list[str]]) -> None:
        try:
            failures = action()
        except Exception as error:  # fail closed and report the precise check
            failures = [f"{type(error).__name__}: {error}"]
        self.results.append(
            {"number": number, "name": name, "passed": not failures, "failures": failures}
        )


def verify(appendix_root: Path | None) -> Verification:
    report = Verification()
    master = load_json(MASTER_MANIFEST)
    complexes = master["complexes"]
    manifests = [ROOT / item["manifest_path"] for item in complexes]
    owners = sorted({ROOT / item["owner_path"] for item in complexes})
    tracked = tracked_files()

    report.check(1, "required top-level architecture packages", lambda: [
        name for name in TOP_PACKAGES if not (PACKAGE / name).is_dir()
    ])
    report.check(2, "required subject-module paths", lambda: [
        path for path in SUBJECT_PATHS if not (PACKAGE / path).is_dir()
    ])
    report.check(3, "required package initializers", lambda: [
        path.relative_to(ROOT).as_posix()
        for path in PACKAGE.rglob("*")
        if path.is_dir()
        and path.name != "__pycache__"
        and any(child.suffix == ".py" for child in path.iterdir() if child.is_file())
        and not (path / "__init__.py").is_file()
    ])
    report.check(4, "obsolete implementation paths absent", lambda: [
        path for path in OBSOLETE_PATHS if (ROOT / path).exists()
    ])

    def subject_structure() -> list[str]:
        failures: list[str] = []
        for owner in owners:
            python = [
                path for path in owner.glob("*.py")
                if path.name != "__init__.py" and not path.name.startswith("test_")
            ]
            for required in ("test", "simulation", "theorem_complex"):
                if not (owner / required).is_dir():
                    failures.append(f"{owner.relative_to(ROOT).as_posix()}: missing {required}")
            if not python:
                failures.append(f"{owner.relative_to(ROOT).as_posix()}: no canonical implementation")
        return failures

    report.check(5, "subject implementation/test/simulation/theorem structure", subject_structure)
    report.check(6, "theorem-complex manifests", lambda: [
        path.relative_to(ROOT).as_posix() for path in manifests if not path.is_file()
    ])
    report.check(7, "unique theorem-complex IDs", lambda: [] if (
        len({item["complex_id"] for item in complexes}) == len(complexes)
        and not master.get("duplicate_complex_ids")
    ) else ["duplicate complex IDs"])

    def count_failures() -> list[str]:
        actual = {level: sum(item["level"] == level for item in complexes) for level in "ABC"}
        expected = {"A": 204, "B": 98, "C": 49}
        failures = [] if actual == expected and len(complexes) == 351 else [f"actual={actual}, total={len(complexes)}"]
        if master.get("counts") != {**expected, "total": 351}:
            failures.append(f"manifest counts={master.get('counts')}")
        return failures

    report.check(8, "verified 204A+98B+49C inventory", count_failures)

    def import_failures() -> list[str]:
        failures: list[str] = []
        modules = sorted({
            module_name(ROOT / path)
            for item in complexes
            for path in item.get("implementation_modules", [])
            if path.endswith(".py") and (ROOT / path).is_file()
        })
        for name in modules:
            try:
                importlib.import_module(name)
            except Exception as error:
                failures.append(f"{name}: {type(error).__name__}: {error}")
        return failures

    report.check(9, "implementation modules import", import_failures)

    def manifest_references() -> list[str]:
        failures: list[str] = []
        path_keys = (
            "manifest_path", "owner_path", "component_modules", "implementation_modules",
            "falsification_modules", "test_modules", "simulation_modules", "artifact_manifests",
        )
        for item in complexes:
            for key in path_keys:
                values = item.get(key, [])
                if isinstance(values, str):
                    values = [values]
                for value in values:
                    if not (ROOT / value).exists():
                        failures.append(f"{item['complex_id']}:{key}:{value}")
        return failures

    report.check(10, "manifest file references", manifest_references)

    def appendix_tracking() -> list[str]:
        failures = []
        for path in tracked:
            relative = path.relative_to(ROOT).as_posix()
            if path.suffix.lower() == ".tex" or path.name in APPENDIX_NAMES:
                failures.append(relative)
        return failures

    report.check(11, "authoritative appendices not tracked", appendix_tracking)

    def copied_appendix_content() -> list[str]:
        failures = [
            path.relative_to(ROOT).as_posix()
            for path in tracked if path.is_file() and digest(path) in APPENDIX_HASHES
        ]
        if appendix_root and appendix_root.is_dir():
            sources = list(appendix_root.rglob("*.tex"))
            signatures: list[str] = []
            for source in sources:
                text = source.read_text(encoding="utf-8", errors="ignore")
                signatures.extend(
                    line.strip() for line in text.splitlines()
                    if len(line.strip()) >= 600 and not line.lstrip().startswith("%")
                )
            for path in tracked:
                if path.suffix.lower() not in {".md", ".txt", ".py", ".json", ".csv"}:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(signature in text for signature in signatures):
                    failures.append(f"long appendix-content match: {path.relative_to(ROOT).as_posix()}")
        return sorted(set(failures))

    report.check(12, "appendix content not copied", copied_appendix_content)

    def placeholder_failures() -> list[str]:
        failures: list[str] = []
        for owner in owners:
            substantive = [
                path for path in owner.rglob("*.py")
                if path.name != "__init__.py" and "theorem_complex" not in path.parts
            ]
            if not substantive:
                failures.append(owner.relative_to(ROOT).as_posix())
        return failures

    report.check(13, "no undocumented empty subject placeholders", placeholder_failures)

    def b_semantics() -> list[str]:
        failures: list[str] = []
        for item in complexes:
            if item["level"] != "B" or item["status"] != "implemented":
                continue
            contract = item.get("mathematical_contract", {})
            if (
                item.get("carrier_violation")
                or not contract.get("operator")
                or not contract.get("residual")
                or contract.get("source_removal_check_count", 0) < 2
                or len(item.get("source_complex_ids", [])) < 2
            ):
                failures.append(item["complex_id"])
        return failures

    report.check(14, "implemented B laws are genuine additive derivations", b_semantics)

    def c_semantics() -> list[str]:
        failures: list[str] = []
        for item in complexes:
            if item["level"] != "C" or item["status"] != "implemented":
                continue
            contract = item.get("mathematical_contract", {})
            if (
                item.get("carrier_violation")
                or not contract.get("operator")
                or not contract.get("residual")
                or not contract.get("closure_predicate")
                or contract.get("source_removal_check_count", 0) < 2
                or len(item.get("source_complex_ids", [])) < 2
            ):
                failures.append(item["complex_id"])
        return failures

    report.check(15, "implemented C laws are genuine spatial closures", c_semantics)

    def artifact_paths() -> list[str]:
        failures: list[str] = []
        transient_parts = {".git", ".qa_artifacts", ".pytest_cache", "__pycache__"}
        candidates = sorted(
            path for path in set(ROOT.rglob("*manifest*.json"))
            if path.name != "layout_verification_manifest.json"
            and transient_parts.isdisjoint(path.relative_to(ROOT).parts)
        )
        for path in candidates:
            try:
                value = load_json(path)
            except json.JSONDecodeError:
                continue
            for item in strings(value):
                if is_absolute_string(item):
                    failures.append(f"{path.relative_to(ROOT).as_posix()}: {item}")
        return failures

    report.check(16, "artifact manifests use relative paths", artifact_paths)

    def entrypoints() -> list[str]:
        failures: list[str] = []
        for owner in owners:
            tests = list((owner / "test").glob("test_*.py")) + list((owner / "test").glob("generate_*.py"))
            simulations = [path for path in (owner / "simulation").glob("*.py") if path.name != "__init__.py"]
            if not tests:
                failures.append(f"{owner.relative_to(ROOT).as_posix()}: test")
            if not simulations:
                failures.append(f"{owner.relative_to(ROOT).as_posix()}: simulation")
        return failures

    report.check(17, "required test and simulation entrypoints", entrypoints)

    def cwd_independent_imports() -> list[str]:
        imports = [f"the_nothingness_effect.{name}" for name in TOP_PACKAGES]
        code = ";".join(f"import {name}" for name in imports)
        with tempfile.TemporaryDirectory() as temporary:
            environment = dict(os.environ)
            environment.pop("PYTHONPATH", None)
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=temporary,
                env=environment,
                capture_output=True,
                text=True,
            )
        return [] if result.returncode == 0 else [result.stderr.strip() or result.stdout.strip()]

    report.check(18, "canonical imports are working-directory independent", cwd_independent_imports)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appendix-root", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    report = verify(args.appendix_root)
    for result in report.results:
        marker = "PASS" if result["passed"] else "FAIL"
        print(f"[{marker}] {result['number']:02d} {result['name']}")
        for failure in result["failures"][:20]:
            print(f"  - {failure}")
        if len(result["failures"]) > 20:
            print(f"  - ... {len(result['failures']) - 20} more")
    payload = {
        "checks": report.results,
        "passed": sum(item["passed"] for item in report.results),
        "failed": sum(not item["passed"] for item in report.results),
    }
    if args.json_output:
        output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
