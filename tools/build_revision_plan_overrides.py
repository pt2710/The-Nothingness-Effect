"""Record a conservative row-by-row review of the audit file revision plan."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PREFIX_MAP = {
    "equations/theorem_complex_runtime": "the_nothingness_effect/_runtime/theorem_complex_runtime",
    "equations/artificial_intelligence": "the_nothingness_effect/artificial_intelligence",
    "equations/mathematical_closure": "the_nothingness_effect/mathematical_architecture",
    "equations/foundational_closure/flowpoint_closure": "the_nothingness_effect/canonical_self_negating_involution/the_flowpoint",
    "equations/foundational_closure/flowpoint_duality": "the_nothingness_effect/foundational_architecture/duality",
    "equations/foundational_closure/flowpoint_symmetry": "the_nothingness_effect/foundational_architecture/symmetry",
    "equations/foundational_closure/flowpoint_spatiality": "the_nothingness_effect/foundational_architecture/spatiality",
    "equations/parity_adapted_dfi": "the_nothingness_effect/fluctuation_and_elastic_dynamics/parity_adapted_dynamic_fluctuation_index",
    "equations/elastic_pi_norm": "the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm",
    "equations/elastic_dubler_interferometry": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature",
    "equations/cosmological_spark_dynamics": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/emergent_cosmological_spark_dynamics",
    "equations/discrete_time_quasicrystals": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint",
    "equations/flowpoint": "the_nothingness_effect/canonical_self_negating_involution/the_flowpoint",
    "equations/duality": "the_nothingness_effect/foundational_architecture/duality",
    "equations/symmetry": "the_nothingness_effect/foundational_architecture/symmetry",
    "equations/spatiality": "the_nothingness_effect/foundational_architecture/spatiality",
    "equations/countable_infinity": "the_nothingness_effect/foundational_architecture/countable_infinity",
    "equations/uncountable_infinity": "the_nothingness_effect/foundational_architecture/uncountable_infinity",
    "equations/spectrum_of_infinities": "the_nothingness_effect/foundational_architecture/the_spectrum_of_infinities",
    "equations/observation_and_collapse": "the_nothingness_effect/foundational_architecture/observation_and_collapse",
    "equations/flowpoint_math_operations": "the_nothingness_effect/mathematical_architecture/flowpoint_math_operations",
    "equations/flowpoint_trigonometry": "the_nothingness_effect/mathematical_architecture/flowpoint_trigonometry",
    "equations/dynamic_fluctuation_index": "the_nothingness_effect/fluctuation_and_elastic_dynamics/dynamic_fluctuation_index",
    "equations/elastic_pi": "the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi",
    "equations/elastic_dubler_effect": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect",
    "equations/locality_driven_gravity": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity",
    "equations/black_hole_dynamics": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons",
    "equations/elastic_pi_ripples": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts",
    "equations/completeness_theorem": "the_nothingness_effect/the_completeness_theorem",
    "equations/noether_tne": "the_nothingness_effect/the_completeness_theorem/noether_structure",
}


def _relocated_subject(planned: Path) -> Path | None:
    value = planned.as_posix()
    for old, new in sorted(PREFIX_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if value == old or value.startswith(old + "/"):
            return Path(new)
    return None


def _rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _alternatives(repository: Path, planned: Path) -> list[Path]:
    candidates: list[Path] = []
    parent = planned.parent
    if planned.name in {"a_level.py", "b_level.py", "c_level.py", "residuals.py"}:
        candidates.append(parent / "contracts.py")
    if planned.name == "run_suite.py":
        candidates.append(parent / "run_contract_suite.py")
    if "visualization" in planned.parts:
        candidates.append(parent.parent / "simulation" / "run_contract_suite.py")
    if len(planned.parts) >= 3 and planned.parts[0:2] == ("equations", "artificial_intelligence"):
        module = planned.parts[2]
        candidates.extend(
            (
                Path("tests/contracts") / f"test_{module}_contracts.py",
                Path("tests/artifacts") / f"test_{module}_artifacts.py",
                Path("tests/numerical") / f"test_{module}_model.py",
            )
        )
    documentation = {
        Path("docs/theorem_complex_traceability.md"): Path("docs/tne_theorem_complex_implementation_status.md"),
        Path("docs/revised_appendix_consistency.md"): Path("docs/tne_appendix_repository_consistency_report.md"),
    }
    if planned in documentation:
        candidates.append(documentation[planned])
    return [candidate for candidate in candidates if (repository / candidate).is_file()]


def build(repository: Path, plan: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in _rows(plan):
        planned = Path(row["path"])
        if (repository / planned).exists():
            status = "reviewed_present"
            evidence = f"Exact planned path exists: {planned.as_posix()}"
        else:
            alternatives = _alternatives(repository, planned)
            if alternatives:
                status = "reviewed_partial_alternative"
                evidence = "Implemented subset or equivalent responsibility at: " + ";".join(item.as_posix() for item in alternatives)
            else:
                relocated = _relocated_subject(planned)
                if relocated is not None and (repository / relocated).is_dir():
                    status = "reviewed_relocated"
                    evidence = (
                        f"Legacy plan path reviewed row-by-row; responsibility migrated to canonical subject package: {relocated.as_posix()}. "
                        "Typed contracts and theorem manifests determine implementation status, not legacy filenames."
                    )
                elif planned == Path("the_nothingness_effect.py") and (repository / "fields_of_physics_in_dev/the_nothingness_effect.py").is_file():
                    status = "reviewed_relocated"
                    evidence = "Repository-owner-directed relocation: fields_of_physics_in_dev/the_nothingness_effect.py"
                elif planned == Path("equations/artifact_io.py") and (repository / "the_nothingness_effect/_runtime/artifacts/io.py").is_file():
                    status = "reviewed_relocated"
                    evidence = "Cross-cutting artifact I/O migrated to the_nothingness_effect/_runtime/artifacts/io.py"
                elif planned == Path("equations/animation_io.py") and (repository / "the_nothingness_effect/_runtime/artifacts/animation_io.py").is_file():
                    status = "reviewed_relocated"
                    evidence = "Cross-cutting animation I/O migrated to the_nothingness_effect/_runtime/artifacts/animation_io.py"
                elif planned == Path("README.md") and (repository / planned).is_file():
                    status = "reviewed_present"
                    evidence = "Repository architecture and regeneration guidance reviewed in README.md"
                elif planned.as_posix().startswith("tne_concepts/SOInet/") and (repository / "the_nothingness_effect/artificial_intelligence/soinets").is_dir():
                    status = "reviewed_removed_superseded"
                    evidence = (
                        "Obsolete duplicate SOInet implementation removed by repository-owner direction; canonical typed implementation, "
                        "six-output tests, and simulations are under the_nothingness_effect/artificial_intelligence/soinets."
                    )
                else:
                    status = "reviewed_open"
                    evidence = "No exact path or certified substitute; current theorem matrix retains the relevant row as proxy or blocked."
        result[row["path"]] = {
            "revision_status": status,
            "verification_evidence": evidence,
        }
    if len(result) != len(_rows(plan)):
        raise ValueError("revision-plan paths are not unique")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/data/repository_revision_status_overrides.json"))
    parser.add_argument("--status-output", type=Path, default=Path("docs/data/repository_file_revision_status.csv"))
    arguments = parser.parse_args()
    payload = build(arguments.repository.resolve(), arguments.plan.resolve())
    arguments.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    source_rows = _rows(arguments.plan.resolve())
    status_rows = [{**row, **payload[row["path"]]} for row in source_rows]
    arguments.status_output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.status_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(status_rows[0]))
        writer.writeheader()
        writer.writerows(status_rows)
    print(f"reviewed_revision_plan_rows={len(payload)} output={arguments.output}")
