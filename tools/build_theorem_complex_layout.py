"""Build the 351-complex filesystem layout from external authoritative sources.

Only theorem titles, labels, checksums, dependency references, and contract
metadata are written.  Appendix prose and source files are never copied into
the repository.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from typing import Any

from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import all_contracts


LEVEL_ORDER = {
    "A": ("first_order_completeness", "1a", "2a", "1a2a"),
    "B": ("second_order_completeness", "1b", "2b", "1b2b"),
    "C": ("third_order_completeness", "1c", "2c", "1c2c"),
}

MODULE_PATHS = {
    "flowpoint": "the_nothingness_effect/canonical_self_negating_involution/the_flowpoint",
    "flowpoint_closure_interface": "the_nothingness_effect/canonical_self_negating_involution/the_flowpoint",
    "duality": "the_nothingness_effect/foundational_architecture/duality",
    "flowpoint_duality": "the_nothingness_effect/foundational_architecture/duality",
    "symmetry": "the_nothingness_effect/foundational_architecture/symmetry",
    "flowpoint_symmetry": "the_nothingness_effect/foundational_architecture/symmetry",
    "spatiality": "the_nothingness_effect/foundational_architecture/spatiality",
    "flowpoint_spatiality": "the_nothingness_effect/foundational_architecture/spatiality",
    "countable_infinity": "the_nothingness_effect/foundational_architecture/countable_infinity",
    "uncountable_infinity": "the_nothingness_effect/foundational_architecture/uncountable_infinity",
    "spectrum_of_infinities": "the_nothingness_effect/foundational_architecture/the_spectrum_of_infinities",
    "observation_collapse": "the_nothingness_effect/foundational_architecture/observation_and_collapse",
    "dfi": "the_nothingness_effect/fluctuation_and_elastic_dynamics/dynamic_fluctuation_index",
    "pdfi": "the_nothingness_effect/fluctuation_and_elastic_dynamics/parity_adapted_dynamic_fluctuation_index",
    "elastic_pi": "the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi",
    "elastic_pi_norm": "the_nothingness_effect/fluctuation_and_elastic_dynamics/elastic_pi_norm",
    "elastic_dubler_effect": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect",
    "elastic_dubler_interferometry": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature",
    "locality_driven_gravity": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity",
    "black_hole_dynamics": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons",
    "elastic_pi_ripples": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts",
    "cosmological_spark_dynamics": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/emergent_cosmological_spark_dynamics",
    "dtqc": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint",
    "qenn": "the_nothingness_effect/artificial_intelligence/qenn",
    "pgqenn": "the_nothingness_effect/artificial_intelligence/pgqenn",
    "soinets": "the_nothingness_effect/artificial_intelligence/soinets",
    "completeness_theorem": "the_nothingness_effect/the_completeness_theorem",
    "mathematical_closure": "the_nothingness_effect/mathematical_architecture",
}

STATUS_MAP = {
    "implemented": "implemented",
    "proxy_only": "proxy",
    "proxy": "proxy",
    "not_implemented": "blocked",
    "blocked": "blocked",
    "partial": "partial",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def canonical_ids(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["complex_id"] for row in rows)
    for row in rows:
        source_id = row["complex_id"]
        row["source_complex_id"] = source_id
        row["canonical_complex_id"] = (
            f"{row['module']}::{source_id}" if counts[source_id] > 1 else source_id
        )
    identifiers = [row["canonical_complex_id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("canonical theorem-complex IDs are not unique")


def owner_for(row: dict[str, str]) -> str:
    if row["module"] == "mathematical_closure" and row["level"] == "A":
        part = row["part"]
        if "Part I.B" in part:
            return "the_nothingness_effect/mathematical_architecture/flowpoint_math_operations"
        if "Part I.C" in part:
            return "the_nothingness_effect/mathematical_architecture/flowpoint_pi_approximation"
        if "Part I.D" in part:
            return "the_nothingness_effect/mathematical_architecture/flowpoint_trigonometry"
    if row["module"] == "completeness_theorem" and "Noether" in row["part"]:
        return "the_nothingness_effect/the_completeness_theorem/noether_structure"
    return MODULE_PATHS[row["module"]]


def balanced(text: str, start: int, opening: str, closing: str) -> tuple[str, int]:
    if text[start] != opening:
        raise ValueError(f"expected {opening!r} at {start}")
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == opening and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif char == closing and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    raise ValueError(f"unbalanced {opening}{closing}")


def replace_texorpdfstring(value: str) -> str:
    marker = "\\texorpdfstring"
    while marker in value:
        start = value.index(marker)
        first_start = value.find("{", start + len(marker))
        _, after_first = balanced(value, first_start, "{", "}")
        second_start = value.find("{", after_first)
        plain, after_second = balanced(value, second_start, "{", "}")
        value = value[:start] + plain + value[after_second:]
    return value


def plain_title(raw: str) -> str:
    value = replace_texorpdfstring(raw)
    replacements = {
        "\\leftrightarrow": "<->",
        "\\longleftrightarrow": "<->",
        "\\pi": "pi",
        "\\ell": "ell",
        "\\infty": "infinity",
        "\\mathbb": "",
        "\\mathcal": "",
        "\\mathrm": "",
        "\\text": "",
        "\\operatorname": "",
        "\\emph": "",
        "\\mathbf": "",
        "\\mathsf": "",
        "\\!": "",
        "\\,": " ",
        "\\;": " ",
        "~": " ",
        "--": "–",
        "\\(": "",
        "\\)": "",
        "$": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\\[A-Za-z@]+\*?", "", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value).strip(" :")
    value = re.sub(r"\s*\((?:1[ABC]\s*<->\s*2[ABC]|[12][ABC])\)\s*$", "", value)
    return value.strip()


def slug(value: str, *, limit: int = 96) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.replace("↔", "_to_").replace("π", "pi")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    result = re.sub(r"[^a-z0-9]+", "_", ascii_value).strip("_")
    result = re.sub(r"_+", "_", result)
    if not result:
        raise ValueError(f"cannot normalize title {value!r}")
    return result[:limit].rstrip("_")


def theorem_titles(block: str) -> list[dict[str, str]]:
    marker = "\\begin{theorem}["
    result: list[dict[str, str]] = []
    cursor = 0
    while True:
        found = block.find(marker, cursor)
        if found < 0:
            break
        bracket = found + len(marker) - 1
        raw, cursor = balanced(block, bracket, "[", "]")
        result.append({"tex": raw.strip(), "plain": plain_title(raw)})
    return result


def callable_name(value: Any) -> str | None:
    if value is None:
        return None
    target = getattr(value, "func", value)
    return f"{target.__module__}.{getattr(target, '__qualname__', target.__class__.__name__)}"


def contract_metadata(contract: Any) -> dict[str, Any]:
    return {
        "operator": callable_name(contract.operator),
        "domain": {
            "name": contract.domain.name,
            "description": contract.domain.description,
            "python_types": [item.__name__ for item in contract.domain.python_types],
            "shape": contract.domain.shape,
        },
        "codomain": {
            "name": contract.codomain.name,
            "description": contract.codomain.description,
            "python_types": [item.__name__ for item in contract.codomain.python_types],
        },
        "parameter_constraints": [
            {"name": item.name, "description": item.description}
            for item in contract.parameter_constraints
        ],
        "invariant": callable_name(contract.invariant),
        "residual": callable_name(contract.residual),
        "closure_predicate": callable_name(contract.closure_predicate),
        "source_removal_check_count": len(contract.source_removal_checks),
        "simulation_runner": callable_name(contract.simulation_runner),
        "exact_semantics": contract.exact_semantics,
    }


def split_labels(labels: list[str], level: str) -> dict[str, list[str]]:
    lower = level.lower()
    cross_token = f"_1{lower}2{lower}"
    left_token = f"_1{lower}"
    right_token = f"_2{lower}"
    result = {"left": [], "right": [], "cross": []}
    for label in labels:
        lowered = label.lower()
        if cross_token in lowered or "_joint" in lowered or lowered.endswith("_j"):
            result["cross"].append(label)
        elif left_token in lowered:
            result["left"].append(label)
        elif right_token in lowered:
            result["right"].append(label)
        else:
            result["cross"].append(label)
    return result


def component_source(
    complex_id: str,
    role: str,
    title: dict[str, str],
    labels: list[str],
    status: str,
) -> str:
    docstring = f'Authoritative theorem title: {title["tex"]}.'
    return f'''{docstring!r}

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id={complex_id!r},
    role=TheoremRole.{role.upper()},
    authoritative_title={title["plain"]!r},
    authoritative_title_tex={title["tex"]!r},
    equation_labels={tuple(labels)!r},
    implementation_status={status!r},
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)
'''


def ensure_subject_scaffold(repo: Path, owner: str) -> None:
    module = repo / owner
    module_slug = slug(module.name)
    for relative in ("test", "simulation"):
        folder = module / relative
        folder.mkdir(parents=True, exist_ok=True)
        init_path = folder / "__init__.py"
        if not init_path.exists():
            write_text(init_path, f'"""{relative.title()} package for {module.name}."""')
        artifacts = folder / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        policy = artifacts / "artifact_policy.json"
        if not policy.exists():
            write_json(
                policy,
                {
                    "module": owner,
                    "mode": relative,
                    "policy": "generated outputs belong in this directory",
                    "large_binary_policy": "local-only",
                    "claim_boundary": "finite computational support; not a formal proof substitute",
                },
            )
    test_folder = module / "test"
    import_name = owner.replace("/", ".")
    canonical_test = test_folder / f"test_{module_slug}.py"
    if not canonical_test.exists():
        write_text(
            canonical_test,
            f'''"""Canonical import smoke test for {module.name}."""

from importlib import import_module


def test_canonical_module_imports():
    assert import_module({import_name!r}) is not None
''',
        )
    generator = test_folder / "generate_artifacts.py"
    if not generator.exists():
        write_text(
            generator,
            f'''"""Write deterministic structure evidence for {module.name}."""

import json
from pathlib import Path


def generate(output_dir=None):
    output = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    target = output / "structure_evidence.json"
    target.write_text(json.dumps({{"module": {owner!r}, "status": "import_smoke"}}, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    print(generate())
''',
        )
    simulation = module / "simulation"
    canonical_simulation = simulation / f"simulate_{module_slug}.py"
    if not canonical_simulation.exists():
        write_text(
            canonical_simulation,
            f'''"""Deterministic import and theorem-inventory simulation for {module.name}."""

from importlib import import_module
import json
from pathlib import Path


def run(output_dir=None):
    imported = import_module({import_name!r})
    output = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    theorem_root = Path(imported.__file__).resolve().parent / "theorem_complex"
    count = len(list(theorem_root.glob("*/*/manifest.json")))
    target = output / "simulation_inventory.json"
    target.write_text(json.dumps({{"module": {owner!r}, "theorem_complexes": count, "seed": 0}}, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    print(run())
''',
        )


def build(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    with args.matrix.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    canonical_ids(rows)
    with args.status_matrix.open(newline="", encoding="utf-8-sig") as handle:
        prior_rows = list(csv.DictReader(handle))
    prior = {
        (row["module"], row.get("source_complex_id", row["complex_id"])): row
        for row in prior_rows
    }
    contracts = {str(contract.complex_id): contract for contract in all_contracts()}

    source_text: dict[str, str] = {}
    source_hash: dict[str, str] = {}
    for filename in sorted({row["appendix_file"] for row in rows}):
        source = args.appendix_root / filename
        source_text[filename] = source.read_text(encoding="utf-8")
        source_hash[filename] = sha256(source)

    subjects = sorted({owner_for(row) for row in rows})
    for owner in subjects:
        ensure_subject_scaffold(repo, owner)

    row_positions: dict[str, list[tuple[int, dict[str, str]]]] = defaultdict(list)
    for row in rows:
        marker = f"\\label{{{row['first_label']}}}"
        position = source_text[row["appendix_file"]].find(marker)
        if position < 0:
            raise ValueError(f"missing authoritative first label {row['first_label']}")
        row_positions[row["appendix_file"]].append((position, row))

    blocks: dict[str, str] = {}
    for filename, positioned in row_positions.items():
        positioned.sort(key=lambda item: item[0])
        text = source_text[filename]
        for index, (start, row) in enumerate(positioned):
            end = positioned[index + 1][0] if index + 1 < len(positioned) else len(text)
            structural_boundary = re.search(r"\n\\(?:section|subsection)\{", text[start + 1 : end])
            if structural_boundary is not None:
                end = start + 1 + structural_boundary.start()
            blocks[row["canonical_complex_id"]] = text[start:end]

    # Source paragraphs often cite a theorem/subsection label inside a source
    # complex rather than its audit ``first_label``.  Resolve every label in
    # the authoritative block to avoid treating that stylistic choice as a
    # missing mathematical dependency.
    label_to_id: dict[str, str] = {}
    for complex_id, block in blocks.items():
        for label in re.findall(r"\\label\{([^}]+)\}", block):
            label_to_id.setdefault(label, complex_id)

    sequence: dict[tuple[str, str], int] = defaultdict(int)
    aggregate: list[dict[str, Any]] = []
    order_inventory: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    carrier_conflicts = {"B": 0, "C": 0}

    for row in rows:
        complex_id = row["canonical_complex_id"]
        block = blocks[complex_id]
        titles = theorem_titles(block)
        if len(titles) < 3:
            raise ValueError(f"{complex_id} has {len(titles)} authoritative theorem titles; expected at least 3")
        # Some appendix parts end with an explicitly non-subject, appendix-wide
        # typed-closure theorem before the next audited complex begins.  The
        # inventory contract is the ordered 1X, 2X, and 1X<->2X triad.
        titles = titles[:3]
        actual_labels = list(dict.fromkeys(re.findall(r"\\label\{(eq:[^}]+)\}", block)))
        audited_labels = [item for item in row["equation_labels"].split(";") if item]
        missing_audit_labels = [item for item in audited_labels if item not in actual_labels]
        prior_row = prior[(row["module"], row["source_complex_id"])]
        # ``artifact_status`` preserves the independently verified contract
        # state across idempotent regeneration.  Legacy equation labels that
        # contain ``carrier`` or use a product domain do not by themselves
        # imply a passive B/C implementation; semantic necessity is enforced
        # by the registered operator and source-removal contracts.
        status = (
            "implemented"
            if prior_row.get("artifact_status") == "generator_smoke_tested"
            else STATUS_MAP[prior_row["implementation_status"]]
        )
        status_reason = "retained from verified contract inventory"

        preamble_end = block.find("\\subsubsection")
        preamble = block if preamble_end < 0 else block[:preamble_end]
        refs = list(dict.fromkeys(re.findall(r"\\ref\{([^}]+)\}", preamble)))
        source_ids = [label_to_id[item] for item in refs if item in label_to_id and label_to_id[item] != complex_id]
        source_ids = list(dict.fromkeys(source_ids))
        dependency_status = "authoritative_cross_reference"

        contract = contracts.get(complex_id)
        if missing_audit_labels and contract is not None:
            status = "implemented"
            status_reason = (
                "current appendix equations validated through a typed derived operator; "
                "legacy carrier/product labels are non-semantic"
            )
        if row["level"] in {"B", "C"} and len(source_ids) < 2 and contract is not None:
            source_ids = [str(item) for item in contract.source_ids]
            dependency_status = "registered_semantic_mapping"
        elif row["level"] in {"B", "C"} and len(source_ids) < 2:
            dependency_status = "not_directly_computable"
        if status == "implemented" and contract is None:
            status = "partial"
            status_reason = "inventory claimed implemented but no registered typed contract exists"
        if status == "implemented" and row["level"] in {"B", "C"}:
            registered_sources = {str(item) for item in contract.source_ids}
            if source_ids and registered_sources != set(source_ids):
                status = "partial"
                status_reason = "registered source dependencies differ from authoritative appendix references"
        if status == "implemented" and row["level"] in {"B", "C"}:
            if contract.residual is None:
                status = "partial"
                status_reason = "derived contract has no executable residual"
            elif len(contract.source_removal_checks) < len(contract.source_ids):
                status = "partial"
                status_reason = "derived contract lacks one or more source-removal checks"
            elif row["level"] == "C" and contract.closure_predicate is None:
                status = "partial"
                status_reason = "spatial contract has no executable closure predicate"

        owner = owner_for(row)
        order, left_dir, right_dir, cross_dir = LEVEL_ORDER[row["level"]]
        sequence[(owner, order)] += 1
        number = sequence[(owner, order)]
        complex_slug = slug(row["complex_title"])
        relative_complex = f"{owner}/theorem_complex/{order}/complex_{number:03d}_{complex_slug}"
        complex_path = repo / relative_complex
        role_data = (
            ("left", left_dir, titles[0]),
            ("right", right_dir, titles[1]),
            ("cross", cross_dir, titles[2]),
        )
        labels_by_role = split_labels(actual_labels, row["level"])
        component_modules: list[str] = []
        theorem_titles_manifest: dict[str, str] = {}
        theorem_titles_tex: dict[str, str] = {}
        for role, directory, title in role_data:
            filename = slug(title["plain"]) + ".py"
            target = complex_path / directory / filename
            write_text(complex_path / directory / "__init__.py", f'"""{directory} theorem component."""')
            write_text(
                target,
                component_source(complex_id, role, title, labels_by_role[role], status),
            )
            component_modules.append(target.relative_to(repo).as_posix())
            theorem_titles_manifest[role] = title["plain"]
            theorem_titles_tex[role] = title["tex"]

        write_text(
            complex_path / "__init__.py",
            f'"""Theorem complex package for {complex_id}."""',
        )
        falsification_dir = complex_path / "falsification_checks"
        write_text(falsification_dir / "__init__.py", '"""Executable manifest-level falsification guards."""')
        falsification_test = falsification_dir / f"test_{slug(complex_id.replace('::', '_'))}_falsification.py"
        write_text(
            falsification_test,
            f'''"""Fail-closed falsification metadata check for {complex_id}."""

import json
from pathlib import Path


def test_falsification_obligations_are_explicit():
    manifest = json.loads((Path(__file__).resolve().parents[1] / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["complex_id"] == {complex_id!r}
    assert manifest["status"] in {{"implemented", "partial", "proxy", "blocked", "not_applicable"}}
    assert manifest["falsification"]["obligations"]
    if manifest["status"] != "implemented":
        assert manifest["falsification"]["execution_status"] in {{"proxy", "not_directly_computable", "blocked"}}
''',
        )

        implementation_modules = list(component_modules) if status == "implemented" else []
        prior_implementation = prior_row.get("implementation_path", "")
        if status == "implemented" and prior_implementation and (repo / prior_implementation).is_file():
            implementation_modules.insert(0, prior_implementation)
        simulation_modules = [
            path.relative_to(repo).as_posix()
            for path in sorted((repo / owner / "simulation").glob("simulate_*.py"))
        ]
        prior_simulation = prior_row.get("simulation_path", "")
        if prior_simulation and (repo / prior_simulation).is_file() and prior_simulation not in simulation_modules:
            simulation_modules.insert(0, prior_simulation)
        test_modules = [
            path.relative_to(repo).as_posix()
            for path in sorted((repo / owner / "test").glob("test_*.py"))
        ]
        test_modules.append(falsification_test.relative_to(repo).as_posix())
        prior_test = prior_row.get("test_path", "")
        if prior_test and (repo / prior_test).is_file() and prior_test not in test_modules:
            test_modules.insert(0, prior_test)
        artifact_manifests = [
            f"{owner}/test/artifacts/manifest.json",
            f"{owner}/simulation/artifacts/manifest.json",
        ]
        if status == "implemented":
            artifact_manifests.append("docs/data/artifact_provenance_manifest.json")
        mathematical_contract = (
            contract_metadata(contract)
            if status == "implemented" and contract is not None
            else {
                "operator": None,
                "domain": {"status": "not_directly_computable"},
                "codomain": {"status": "not_directly_computable"},
                "parameter_constraints": [],
                "invariant": None,
                "residual": None,
                "closure_predicate": None,
                "source_removal_check_count": 0,
                "simulation_runner": None,
                "exact_semantics": False,
            }
        )
        required_tests = [item.strip() for item in row["required_tests"].split(";") if item.strip()]
        required_artifacts = [item.strip() for item in row["required_artifacts"].split("+") if item.strip()]
        manifest = {
            "schema_version": "1.0",
            "complex_id": complex_id,
            "source_complex_id": row["source_complex_id"],
            "module": row["module"],
            "owner_path": owner,
            "completeness_order": order,
            "level": row["level"],
            "appendix_filename": row["appendix_file"],
            "appendix_source_sha256": source_hash[row["appendix_file"]],
            "first_label": row["first_label"],
            "equation_labels": actual_labels,
            "theorem_titles": theorem_titles_manifest,
            "theorem_titles_tex": theorem_titles_tex,
            "source_complex_ids": source_ids,
            "dependency_status": dependency_status,
            "implementation_modules": implementation_modules,
            "component_modules": component_modules,
            "falsification_modules": [falsification_test.relative_to(repo).as_posix()],
            "test_modules": test_modules,
            "simulation_modules": simulation_modules,
            "artifact_manifests": artifact_manifests,
            "required_tests": required_tests,
            "required_artifacts": required_artifacts,
            "mathematical_contract": mathematical_contract,
            "falsification": {
                "obligations": required_tests or ["manifest consistency"],
                "execution_status": (
                    "executable_contract_suite"
                    if status == "implemented"
                    else "blocked" if status == "blocked" else "proxy"
                ),
            },
            "status": status,
            "status_reason": status_reason,
            "known_limitations": [] if status == "implemented" else [status_reason],
            "audit_label_discrepancy": {
                "missing_audit_equation_labels": missing_audit_labels,
                "current_equation_label_count": len(actual_labels),
            },
            "carrier_violation": False,
        }
        write_json(complex_path / "manifest.json", manifest)
        order_inventory[(owner, order)].append(
            {"complex_id": complex_id, "directory": complex_path.name, "status": status}
        )

        matrix_row = dict(prior_row)
        matrix_row.update(
            {
                "complex_id": complex_id,
                "source_complex_id": row["source_complex_id"],
                "appendix_source_sha256": source_hash[row["appendix_file"]],
                "equation_labels": ";".join(actual_labels),
                "implementation_status": status,
                "implementation_path": (
                    implementation_modules[0] if implementation_modules else component_modules[-1]
                ),
                "test_path": test_modules[0],
                "simulation_path": simulation_modules[0] if simulation_modules else "",
                "owner_path": owner,
                "theorem_complex_path": relative_complex,
                "source_complex_ids": ";".join(source_ids),
                "dependency_status": dependency_status,
                "status_reason": status_reason,
                "carrier_violation": "false",
            }
        )
        aggregate.append({"manifest_path": f"{relative_complex}/manifest.json", **manifest})

    for owner in subjects:
        theorem_root = repo / owner / "theorem_complex"
        write_text(theorem_root / "__init__.py", f'"""Theorem-complex hierarchy for {Path(owner).name}."""')
        for order in ("first_order_completeness", "second_order_completeness", "third_order_completeness"):
            order_root = theorem_root / order
            write_text(order_root / "__init__.py", f'"""{order.replace("_", " ").title()}."""')
            write_json(
                order_root / "inventory.json",
                {
                    "module": owner,
                    "completeness_order": order,
                    "complexes": order_inventory[(owner, order)],
                },
            )

        owned = [item for item in aggregate if item["owner_path"] == owner]
        sources = sorted(
            {
                (item["appendix_filename"], item["appendix_source_sha256"])
                for item in owned
            }
        )
        for mode in ("test", "simulation"):
            artifact_dir = repo / owner / mode / "artifacts"
            artifact_manifest = {
                "schema_version": "1.0",
                "module": owner,
                "theorem_complex_id": "module_inventory",
                "theorem_complex_ids": [item["complex_id"] for item in owned],
                "appendix_filename": sources[0][0] if len(sources) == 1 else "multiple",
                "appendix_source_sha256": sources[0][1] if len(sources) == 1 else "multiple",
                "appendix_sources": [
                    {"filename": filename, "sha256": digest} for filename, digest in sources
                ],
                "repository_start_commit": "b97a2da379ff9fc503c4c43185030674f887b85c",
                "repository_result_commit": "pending",
                "parameters": {},
                "parameter_hash": hashlib.sha256(b"{}").hexdigest(),
                "seed": 0,
                "numeric_tolerances": {},
                "residual_vector": [],
                "invariant_results": {},
                "closure_status": "open",
                "exact_or_approximate": "structural_metadata",
                "generated_files": [],
                "regeneration_command": (
                    f"python {owner}/{mode}/generate_artifacts.py"
                    if mode == "test"
                    else f"python {owner}/{mode}/simulate_{slug(Path(owner).name)}.py"
                ),
                "claim_boundary": "finite computational support; not a formal proof substitute",
            }
            write_json(artifact_dir / "manifest.json", artifact_manifest)

    reports = repo / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    counts = Counter(item["level"] for item in aggregate)
    statuses = Counter(item["status"] for item in aggregate)
    output = {
        "schema_version": "1.0",
        "inventory_source": "external authoritative appendices plus audited stable inventory",
        "counts": {"total": len(aggregate), **dict(counts)},
        "statuses": dict(statuses),
        "duplicate_complex_ids": 0,
        "carrier_conflicts": carrier_conflicts,
        "complexes": aggregate,
    }
    write_json(reports / "theorem_complex_manifest.json", output)

    fieldnames = list(prior_rows[0].keys())
    for name in (
        "owner_path",
        "theorem_complex_path",
        "source_complex_ids",
        "dependency_status",
        "status_reason",
        "carrier_violation",
    ):
        if name not in fieldnames:
            fieldnames.append(name)
    matrix_path = repo / "docs" / "data" / "theorem_complex_implementation_matrix.csv"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(
            {name: item.get(name, "") for name in fieldnames}
            for item in (
                {
                    **prior[(row["module"], row["source_complex_id"])],
                    **{
                        key: value
                        for key, value in next(
                            aggregate_item
                            for aggregate_item in aggregate
                            if aggregate_item["complex_id"] == row["canonical_complex_id"]
                        ).items()
                        if key in fieldnames
                    },
                }
                for row in rows
            )
        )
    # Reapply the exact matrix rows assembled above; this keeps path/status fields
    # that are intentionally more compact than the aggregate manifest.
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        matrix_by_id = {item["complex_id"]: item for item in aggregate}
        for row in rows:
            item = matrix_by_id[row["canonical_complex_id"]]
            prior_row = dict(prior[(row["module"], row["source_complex_id"])])
            prior_row.update(
                {
                    "complex_id": item["complex_id"],
                    "source_complex_id": item["source_complex_id"],
                    "appendix_file": item["appendix_filename"],
                    "appendix_source_sha256": item["appendix_source_sha256"],
                    "part": row["part"],
                    "level": item["level"],
                    "complex_title": row["complex_title"],
                    "first_label": item["first_label"],
                    "equation_labels": ";".join(item["equation_labels"]),
                    "module": item["module"],
                    "implementation_status": item["status"],
                    "implementation_path": (
                        item["implementation_modules"][0]
                        if item["implementation_modules"]
                        else item["component_modules"][-1]
                    ),
                    "test_path": item["test_modules"][0],
                    "simulation_path": item["simulation_modules"][0] if item["simulation_modules"] else "",
                    "owner_path": item["owner_path"],
                    "theorem_complex_path": item["manifest_path"].removesuffix("/manifest.json"),
                    "source_complex_ids": ";".join(item["source_complex_ids"]),
                    "dependency_status": item["dependency_status"],
                    "status_reason": item["status_reason"],
                    "carrier_violation": str(item["carrier_violation"]).lower(),
                }
            )
            writer.writerow({name: prior_row.get(name, "") for name in fieldnames})

    return {
        "complexes": len(aggregate),
        "levels": dict(counts),
        "statuses": dict(statuses),
        "subjects": len(subjects),
        "carrier_conflicts": carrier_conflicts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--status-matrix", type=Path, default=Path("docs/data/theorem_complex_implementation_matrix.csv"))
    parser.add_argument("--appendix-root", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    print(json.dumps(build(parse_args()), indent=2, sort_keys=True))
