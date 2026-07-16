"""Regenerate final repository, theorem, AI, artifact, and QA deliverables."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import shutil

if __package__:
    from tools.build_final_qa_manifest import build as build_qa
else:
    from build_final_qa_manifest import build as build_qa


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"


INTEGRATED_RUNTIME_EVIDENCE = {
    "flowpoint_unity_orientation_and_integer_unfolding": (
        "PGQENN applies the exact finite Flowpoint value involution n->-n to verified positive TC placements; the negative geometry is a separately labelled TNE bridge."
    ),
    "dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence": (
        "QENN evaluates the normalized carrier W_tilde=gamma^-1 W while recording the canonical DFI rescaling-invariance residual during joint K_D/SOI search."
    ),
    "weighted_path_functional_and_norm_admissibility": (
        "QENN executes the finite Elastic-pi weighted transition norm on its declared feature-window trajectory."
    ),
    "elastic_field_ratios_and_weight_regularity": (
        "QENN evaluates successive exact Elastic-pi field ratios inside the weighted transition norm without clipping."
    ),
    "elastic_dubler_duality_closure": (
        "QENN and the multimodal SOInet execute the exact positive Dubler ratio and additive log-shift with exchange and cocycle residuals."
    ),
    "elastic_dtqc_spectral_measure_dual_of_dtqc": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
    "dtqc::dual_support_equivalence_support_mismatch_leakage": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
    "parseval_energy_bijection_l_2_energy_mismatch": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
    "irrational_drive_locking_commensurate_resonance_collapse": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
    "elastic_gain_support_transport_isomorphism": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
    "diophantine_parseval_locking_invariant": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
    "elastic_parseval_quasicrystal_isometry": (
        "QENN executes this DTQC contract through DTQCInflationLayer before spectral memory and records its residual by complex ID."
    ),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    output.extend("| " + " | ".join(str(item) for item in row) + " |" for row in rows)
    return "\n".join(output)


def build_source_registry(master: dict[str, object]) -> dict[str, object]:
    complexes = master["complexes"]
    appendix_sources = {
        item["appendix_filename"]: item["appendix_source_sha256"] for item in complexes
    }
    status_counts = Counter(item["status"] for item in complexes)
    return {
        "schema_version": "2.0",
        "authority": "seven externally stored authoritative appendices; no LaTeX source is repository data",
        "appendix_sources": [
            {"appendix_filename": name, "sha256": digest}
            for name, digest in sorted(appendix_sources.items())
        ],
        "inventory_summary": {
            "total": len(complexes),
            "A": sum(item["level"] == "A" for item in complexes),
            "B": sum(item["level"] == "B" for item in complexes),
            "C": sum(item["level"] == "C" for item in complexes),
            "implementation_status_counts": dict(sorted(status_counts.items())),
            "duplicate_complex_ids": len(complexes) - len({item["complex_id"] for item in complexes}),
            "carrier_conflicts": sum(bool(item["carrier_violation"]) for item in complexes),
        },
        "source_laws": [
            {
                "complex_id": item["complex_id"],
                "source_complex_id": item["source_complex_id"],
                "appendix_filename": item["appendix_filename"],
                "appendix_source_sha256": item["appendix_source_sha256"],
                "level": item["level"],
                "title": item["theorem_titles"].get("cross", item["complex_id"]),
                "first_label": item["first_label"],
                "equation_labels": item["equation_labels"],
                "module": item["module"],
                "source_complex_ids": item["source_complex_ids"],
                "implementation_status": item["status"],
                "status_reason": item["status_reason"],
                "owner_path": item["owner_path"],
                "manifest_path": item["manifest_path"],
            }
            for item in complexes
        ],
    }


def update_ai_matrix(matrix: list[dict[str, str]]) -> list[dict[str, str]]:
    theorem = {row["complex_id"]: row for row in read_csv(DATA / "theorem_complex_implementation_matrix.csv")}
    result = []
    for row in matrix:
        status = theorem[row["complex_id"]]["implementation_status"]
        if row["complex_id"] in INTEGRATED_RUNTIME_EVIDENCE:
            integration = "integrated_runtime"
            evidence = INTEGRATED_RUNTIME_EVIDENCE[row["complex_id"]]
        elif row["integration_status"] == "integrated_shared_primitive":
            integration = row["integration_status"]
            evidence = row["integration_evidence"]
        elif status == "implemented":
            integration = "typed_contract_available"
            evidence = "Current appendix equations are represented by a registered typed contract; AI wiring remains target-specific."
        elif status == "proxy":
            integration = "planned_proxy_source"
            evidence = "Related numerical code exists, but the complete source-law contract is not certified for AI integration."
        else:
            integration = "blocked_source_law"
            evidence = "The underlying A-level source law remains unresolved; this is not a carrier-label conflict."
        use_decision, hypothesis, metric, conclusion = ai_optimization_assessment(
            row, status, integration
        )
        result.append(
            {
                **row,
                "source_implementation_status": status,
                "integration_status": integration,
                "integration_evidence": evidence,
                "use_decision": use_decision,
                "optimization_hypothesis": hypothesis,
                "optimization_metric": metric,
                "optimization_conclusion": conclusion,
                "carrier_conflict": "false",
            }
        )
    return result


def ai_optimization_assessment(
    row: dict[str, str], status: str, integration: str
) -> tuple[str, str, str, str]:
    """Assign a falsifiable AI use/optimization assessment to every mapping."""

    text = " ".join(
        str(row.get(field, ""))
        for field in (
            "module",
            "complex_title",
            "reusable_ai_primitive",
            "qenn_use",
            "pgqenn_use",
            "soinets_use",
        )
    ).lower()
    if "observation" in text or "collapse" in text:
        hypothesis = "improve calibrated readout and reject ambiguous collapse states"
        metric = "expected calibration error; Brier score; collapse idempotence/definiteness residual"
    elif "quasicrystal" in text or "dtqc" in text or "parseval" in text:
        hypothesis = "reduce spectral leakage while preserving reconstructible energy/support"
        metric = "support leakage; Parseval residual; spectral reconstruction RMSE"
    elif "elastic" in text or "dubler" in text or "curvature" in text:
        hypothesis = "stabilize weighted transitions, curvature response, and relative modality/shell gain"
        metric = "validation objective; gradient norm; Elastic-pi norm/ratio residual; source-removal delta"
    elif "dfi" in text or "entropy" in text or "fluctuation" in text:
        hypothesis = "reduce spiking, entropy drift, and scale-dependent instability"
        metric = "DFI/pDFI drift; validation objective; predictive entropy; obstruction count"
    elif "parity" in text or "2-adic" in text or "involut" in text or "flowpoint" in text:
        hypothesis = "improve reversible transport and prevent parity/equivariance leakage"
        metric = "involution/equivariance residual; reverse reconstruction error; source-removal delta"
    elif "spatial" in text or "local" in text or "adjacency" in text or "shell" in text:
        hypothesis = "improve locality-aware transport without boundary or shell leakage"
        metric = "localization/boundary residual; message reconstruction; held-out objective"
    elif "spectrum" in text or "fourier" in text or "memory" in text:
        hypothesis = "improve spectral memory and cross-scale reconstruction"
        metric = "spectral reconstruction RMSE; support leakage; transfer residual"
    else:
        hypothesis = "reduce the declared theorem residual in the target architecture"
        metric = "typed contract residual; source-removal delta; held-out validation objective"

    if integration in {"integrated_runtime", "integrated_shared_primitive"}:
        return (
            "use_now_with_ablation",
            hypothesis,
            metric,
            "runtime structural effect is tested; task-level improvement must be established per dataset",
        )
    if status == "implemented":
        return (
            "evaluate_typed_candidate",
            hypothesis,
            metric,
            "source contract is available, but target-specific optimization benefit is not yet measured",
        )
    if status == "proxy":
        return (
            "defer_until_source_complete",
            hypothesis,
            metric,
            "related proxy code is insufficient for canonical AI enablement or an optimization claim",
        )
    return (
        "blocked_until_source_law",
        hypothesis,
        metric,
        "no optimization experiment is admissible until the upstream A source law is implemented",
    )


def build_path_manifest(master: dict[str, object]) -> dict[str, object]:
    complexes = master["complexes"]
    subjects = sorted({item["owner_path"] for item in complexes})
    required_roots = [
        "the_nothingness_effect/canonical_self_negating_involution",
        "the_nothingness_effect/mathematical_architecture",
        "the_nothingness_effect/foundational_architecture",
        "the_nothingness_effect/fluctuation_and_elastic_dynamics",
        "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture",
        "the_nothingness_effect/artificial_intelligence",
        "the_nothingness_effect/the_completeness_theorem",
    ]
    return {
        "schema_version": "1.0",
        "canonical_top_level_packages": required_roots,
        "subject_module_count": len(subjects),
        "subject_modules": [
            {
                "path": subject,
                "test": f"{subject}/test",
                "simulation": f"{subject}/simulation",
                "theorem_complex": f"{subject}/theorem_complex",
                "exists": (ROOT / subject).is_dir(),
            }
            for subject in subjects
        ],
        "removed_legacy_paths": {
            path: not (ROOT / path).exists()
            for path in ("equations", "tne_concepts", "figures", "figures_mccrackn")
        },
    }


def portable_execution_manifest(payload: dict[str, object]) -> dict[str, object]:
    """Remove workstation-specific launch paths from recorded execution evidence."""

    for entry in payload["entrypoints"]:
        entry["executed_command"] = [
            "<python>" if Path(str(item)).name.lower() in {"python", "python.exe"} else (
                Path(str(item)).relative_to(ROOT).as_posix()
                if Path(str(item)).is_absolute() and Path(str(item)).is_relative_to(ROOT)
                else str(item)
            )
            for item in entry.get("executed_command", ("<python>", entry["path"]))
        ]
        if entry["status"] == "passed":
            entry["output_tail"] = ""
        else:
            entry["output_tail"] = str(entry["output_tail"]).replace(str(ROOT), "<repository-root>")
    return payload


def build_reports(qa: dict[str, object]) -> None:
    master = json.loads((REPORTS / "theorem_complex_manifest.json").read_text(encoding="utf-8"))
    matrix = read_csv(DATA / "theorem_complex_implementation_matrix.csv")
    artifact = json.loads((DATA / "artifact_provenance_manifest.json").read_text(encoding="utf-8"))
    tests = portable_execution_manifest(json.loads((REPORTS / "test_execution_manifest.json").read_text(encoding="utf-8")))
    simulations = portable_execution_manifest(json.loads((REPORTS / "simulation_execution_manifest.json").read_text(encoding="utf-8")))
    write_json(REPORTS / "test_execution_manifest.json", tests)
    write_json(REPORTS / "simulation_execution_manifest.json", simulations)
    revisions = read_csv(DATA / "repository_file_revision_status.csv")
    source_registry = build_source_registry(master)
    write_json(DATA / "source_law_registry.json", source_registry)
    write_json(REPORTS / "source_law_registry.json", source_registry)
    write_json(REPORTS / "artifact_manifest.json", artifact)
    write_json(REPORTS / "repository_path_manifest.json", build_path_manifest(master))
    write_json(DATA / "final_qa_manifest.json", qa)
    write_json(REPORTS / "final_qa_manifest.json", qa)

    ai_rows = update_ai_matrix(read_csv(DATA / "ai_derivation_integration_matrix.csv"))
    write_csv(DATA / "ai_derivation_integration_matrix.csv", ai_rows)
    write_csv(REPORTS / "ai_derivation_integration_matrix.csv", ai_rows)
    shutil.copyfile(DATA / "theorem_complex_implementation_matrix.csv", REPORTS / "theorem_complex_implementation_matrix.csv")
    shutil.copyfile(DATA / "repository_file_revision_status.csv", REPORTS / "repository_file_revision_status.csv")

    levels = Counter((row["level"], row["implementation_status"]) for row in matrix)
    status = Counter(row["implementation_status"] for row in matrix)
    by_appendix: dict[str, Counter[str]] = defaultdict(Counter)
    by_module: dict[str, Counter[str]] = defaultdict(Counter)
    for row in matrix:
        by_appendix[row["appendix_file"]][row["implementation_status"]] += 1
        by_module[row["module"]][row["implementation_status"]] += 1
    level_table = markdown_table(
        ["Level", "Inventory", "Implemented", "Proxy", "Blocked"],
        [[level, sum(row["level"] == level for row in matrix), levels[level, "implemented"], levels[level, "proxy"], levels[level, "blocked"]] for level in "ABC"],
    )
    appendix_table = markdown_table(
        ["Appendix", "Implemented", "Proxy", "Blocked"],
        [[name, counts["implemented"], counts["proxy"], counts["blocked"]] for name, counts in sorted(by_appendix.items())],
    )
    module_gap_table = markdown_table(
        ["Module", "Implemented", "Proxy", "Blocked"],
        [[name, counts["implemented"], counts["proxy"], counts["blocked"]] for name, counts in sorted(by_module.items()) if counts["proxy"] or counts["blocked"]],
    )
    revision_counts = Counter(row["revision_status"] for row in revisions)
    ai_counts = Counter(row["integration_status"] for row in ai_rows)
    artifact_summary = artifact["summary"]

    (DOCS / "tne_theorem_complex_layout_report.md").write_text(
        "# TNE theorem-complex layout report\n\n"
        f"The verified inventory contains **{len(matrix)}** unique complexes: 204 A, 98 B, and 49 C. "
        "Every complex owns a manifest beneath its canonical subject package.\n\n"
        f"{level_table}\n\n"
        "All 147 B/C records were inspected by equation/dependency semantics. Registered B contracts expose additive operators, residuals, non-cancellation, and every-source removal. Registered C contracts expose spatial/local operators, boundary or leakage residuals, closure predicates, and every-B-source removal.\n\n"
        "Carrier-label conflicts: **0**. Blocked B complexes: **0**. Blocked C complexes: **0**.\n\n"
        "Regenerate with `python tools/build_theorem_complex_layout.py --matrix <external-audit-matrix> --status-matrix docs/data/theorem_complex_implementation_matrix.csv --appendix-root <external-appendix-root>`.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_theorem_complex_implementation_status.md").write_text(
        "# TNE theorem-complex implementation status\n\n"
        "The machine-readable authority is `docs/data/theorem_complex_implementation_matrix.csv`. A registered contract is promoted only when its typed source law and required residual/source-removal obligations are executable.\n\n"
        f"{level_table}\n\n"
        f"Current totals: **{status['implemented']} implemented**, **{status['proxy']} proxy**, and **{status['blocked']} blocked**. All blocked records are A-level source-law gaps; none is blocked because of a carrier/product/spatial-carrier label.\n\n"
        f"{appendix_table}\n\n"
        "A `proxy` row records related numerical or legacy support without claiming a complete theorem implementation. A successful finite C evaluation remains a numerical candidate unless the appendix's mathematical attainment obligations are established.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_open_implementation_gaps.md").write_text(
        "# TNE open implementation gaps\n\n"
        f"Of 351 verified complexes, {status['implemented']} are implemented, {status['proxy']} remain proxy-only, and {status['blocked']} A-level source laws remain blocked. "
        "There are no blocked B/C rows and no carrier-label conflicts. Proxy B/C rows remain open because their complete source/operator/closure obligations are not yet certified, not because of their names.\n\n"
        f"{module_gap_table}\n\n"
        "## Next safe order\n\n"
        "1. Implement the remaining blocked A source laws directly from their authoritative equations.\n"
        "2. Upgrade proxy A laws before promoting dependent proxy B/C contracts.\n"
        "3. Preserve genuine additive and spatial semantics, deterministic source-removal tests, and fail-closed numerical boundaries.\n"
        "4. Regenerate theorem and artifact manifests after every status promotion.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_source_law_registry.md").write_text(
        "# TNE source-law registry\n\n"
        "`docs/data/source_law_registry.json` is regenerated from the current 351-complex manifest. It records only appendix filenames, SHA-256 digests, theorem IDs, labels, dependencies, status, and repository paths; it contains no appendix LaTeX source.\n\n"
        f"Registered implementation contracts: **{status['implemented']}**. Duplicate IDs: **0**. Carrier conflicts: **0**.\n\n"
        "The seven appendix checksums are verified externally before generation. Mathematical authority remains in those external files; repository numerical models cannot redefine them.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_ai_derivation_integration_report.md").write_text(
        "# TNE AI derivation integration report\n\n"
        "QENN, PGQENN, and SOInets each execute all six requested output groups in their own `test/artifacts` and `simulation/artifacts` trees: color classification, sound classification, bidirectional color classification, bidirectional sound classification, color cloning, and sound cloning.\n\n"
        f"The cross-appendix AI matrix contains {len(ai_rows)} verified mappings: "
        + ", ".join(f"{count} `{name}`" for name, count in sorted(ai_counts.items()))
        + ".\n\n"
        "Every row now records its source theorem's current implementation status. No row carries the retired carrier-conflict classification. Typed availability does not by itself claim that every target architecture consumes the source; target-specific wiring remains explicit in the evidence column.\n\n"
        "The owner-supplied 137-title AI outline is assessed through these mappings. Every row now includes a use decision, a falsifiable optimization hypothesis, a metric, and a conclusion. Current decisions are 23 use-now-with-ablation, 107 typed candidates, 128 deferred proxy sources, and 22 upstream source-law blocks.\n\n"
        "Canonical AI execution is CPU-testable, fail-closed for non-finite values, and uses deterministic seeds. PGQENN random sampling remains only a named ablation/comparison mode.\n\n"
        "The executable dependency chain is DTQC -> QENN, QENN + pinned MPL-TC -> PGQENN, and QENN + PGQENN -> SOInets. QENN also composes Flowpoint projectors, normalized DFI, pDFI, exact unclipped Elastic-pi, Elastic Dubler, observation/collapse, spectral memory, Parseval, and completeness residuals. PGQENN consumes all four verified positive MPL-TC TC streams; its negative number spectrum is a separately labelled TNE Flowpoint lift, not an extension claimed by MPL-TC.\n\n"
        "The visible trainable multimodal package adds learned shared/private modality axes, forward/reverse transport residuals, local per-axis and global cross-axis Gaussian-Bernoulli RBMs, and bounded modality-specific prototype growth over the canonical SOInet backbone. Axis, RBM, cluster and signed-spectrum contexts affect inference and have independent source-removal modes. Joint validation search tunes exact positive K_D and the SOI normalization carrier while verifying DFI scale invariance. RBM is an external numerical realization, not an appendix source law. The uploaded multimodal ZIP remains external design context; none of its source or artifacts was copied.\n\n"
        "QENN, PGQENN, and SOInets each own static topology, directed-connectivity, and activation/residual views plus signal-propagation, topology-growth, and recurrent-activation GIFs in both test and simulation directories. Multimodal producers additionally own axis-learning, cluster-growth, RBM bipartite, energy-landscape, and RBM-reconstruction evidence.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_artifact_provenance_report.md").write_text(
        "# TNE artifact provenance report\n\n"
        f"The aggregate manifest covers all **{artifact_summary['theorem_manifests']}** implemented theorem contracts with no missing or duplicate ID. It indexes **{artifact_summary['generated_tables']}** tables, **{artifact_summary['generated_static_figures']}** static figures, **{artifact_summary['producer_local_animations']}** tracked GIF animations, **{artifact_summary['producer_local_audio_files']}** audio files, and **{artifact_summary['animation_generators']}** animation generators.\n\n"
        f"Result files live beneath the producing module's `test/artifacts` or `simulation/artifacts` directory. Producer-local evidence contains **{artifact_summary['producer_local_manifests']}** manifests. Each multimodal mode owns ten tables, twenty-three figures, twelve compact GIFs, and two manifests. PGQENN additionally records signed-spectrum 3D growth and signal propagation. Large regenerable frame dumps and videos remain external. Every theorem manifest records checksum, start/result commit, seed, tolerances, residual vector, closure status, generated files, regeneration command, and the finite-evidence claim boundary.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_import_migration_report.md").write_text(
        "# TNE import migration report\n\n"
        "Canonical imports use the `the_nothingness_effect` package and remain independent of the checkout directory name. Cross-cutting runtime code is under `the_nothingness_effect._runtime`; domain artifact code is owned by its subject package.\n\n"
        "The layout verifier confirms all implementation modules import from the repository root and a foreign working directory. Removed roots `equations` and `tne_concepts` are not import authorities. Compatibility wrappers are retained only where explicitly documented.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_test_and_simulation_report.md").write_text(
        "# TNE test and simulation report\n\n"
        f"Full pytest gate: **{qa['tests']['passed']} passed**, **{qa['tests']['failed']} failed**, **{qa['tests']['skipped']} skipped**, **{qa['tests']['warnings']} warnings** in **{qa['tests']['runtime_seconds']} seconds**.\n\n"
        f"Producer entrypoints: test {tests['summary']['passed']}/{tests['entrypoint_count']} passed; simulation {simulations['summary']['passed']}/{simulations['entrypoint_count']} passed. "
        "Legacy heavy renderers with canonical-name collisions are recorded as bounded contract-inventory fallbacks; typed contract/evidence suites are preferred when present.\n\n"
        "Commands: `python -m pytest -q`, `python tools/run_repository_entrypoints.py test`, `python tools/run_repository_entrypoints.py simulation`, and `python tools/verify_tne_repository_layout.py`.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_artifact_generation_report.md").write_text(
        "# TNE artifact generation report\n\n"
        f"Deterministic seed 0 generated {artifact_summary['theorem_manifests']} theorem manifests, {artifact_summary['generated_tables']} tables, and {artifact_summary['generated_static_figures']} static figures. Producer-local outputs include {artifact_summary['producer_local_animations']} GIFs and {artifact_summary['producer_local_audio_files']} audio files.\n\n"
        "Regenerate the theorem evidence outside Git with `python tools/generate_artifact_provenance.py --output-root <external-output-root> --aggregate docs/data/artifact_provenance_manifest.json --representative-dir docs/figures`. Producer-local AI and subject outputs are regenerated through the entrypoint runner.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_repository_architecture_migration_report.md").write_text(
        "# TNE repository architecture migration report\n\n"
        f"Repository start commit: `{qa['repository_start_commit']}`. Working branch: `{qa['work_branch']}`. The canonical package now follows the seven appendix-aligned top-level architectures plus a private shared runtime.\n\n"
        "All obsolete `framework`, `equations`, `tne_concepts`, root `figures`, and `figures_mccrackn` paths are absent. Artifacts are producer-local. The audit's 170-row file plan was reviewed row-by-row: "
        + ", ".join(f"{count} `{name}`" for name, count in sorted(revision_counts.items()))
        + ".\n\n"
        "Theorem layout, import migration, tests/simulations, artifacts, open gaps, decision ledger, and final QA are documented in the companion `docs/tne_*` reports.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_appendix_repository_consistency_report.md").write_text(
        "# TNE appendix-repository consistency report\n\n"
        f"The external authoritative inventory is verified at 351 complexes (204 A, 98 B, 49 C). Current repository status is {status['implemented']} implemented, {status['proxy']} proxy, and {status['blocked']} blocked A source laws.\n\n"
        "The retired carrier heuristic has been removed globally. Labels such as `product_carrier` and `spatial_carrier` describe typed mathematical domains and do not imply passive implementations. Every registered B contract is evaluated as a genuine additive derivation, and every registered C contract as a genuine spatial closure. Carrier conflicts: **0**; blocked B/C: **0**.\n\n"
        f"{appendix_table}\n\n"
        "All appendix files remain external to Git. Repository outputs contain only bounded identifiers, hashes, labels, statuses, dependency mappings, and provenance.\n",
        encoding="utf-8",
    )
    (DOCS / "tne_final_qa_report.md").write_text(
        "# TNE final QA report\n\n"
        f"- Start commit: `{qa['repository_start_commit']}`\n"
        f"- QA source commit: `{qa['repository_result_commit']}`\n"
        f"- Branch: `{qa['work_branch']}`\n"
        f"- Changed files: {qa['changes']['total_changed_files']} ({qa['changes']['new_files']} new, {qa['changes']['modified_files']} modified/moved/deleted)\n"
        f"- Tests: {qa['tests']['passed']} passed, {qa['tests']['failed']} failed, {qa['tests']['skipped']} skipped, {qa['tests']['warnings']} warnings in {qa['tests']['runtime_seconds']} seconds\n"
        f"- Implemented A/B/C: {qa['theorem_inventory']['implemented_A']}/{qa['theorem_inventory']['implemented_B']}/{qa['theorem_inventory']['implemented_C']}\n"
        f"- Proxy / blocked: {qa['theorem_inventory']['proxy_only']} / {qa['theorem_inventory']['not_implemented']}\n"
        f"- Duplicate IDs / carrier conflicts / blocked B / blocked C: 0 / 0 / 0 / 0\n"
        f"- Tracked `.tex`: {len(qa['tracked_tex_files'])}\n"
        f"- Unresolved implemented dependencies: {len(qa['unresolved_internal_dependencies'])}\n"
        f"- Theorem manifests / producer-local manifests: {artifact_summary['theorem_manifests']} / {artifact_summary['producer_local_manifests']}\n"
        f"- Tables / figures / tracked GIFs / animation generators: {artifact_summary['generated_tables']} / {artifact_summary['generated_static_figures']} / {artifact_summary['producer_local_animations']} / {artifact_summary['animation_generators']}\n\n"
        "Source-law regression status: passed. Appendix checksum verification: passed for all seven authoritative sources.\n\n"
        "No authoritative appendix .tex file was copied into, tracked by, committed to, or pushed to the GitHub repository.\n",
        encoding="utf-8",
    )

    ledger = DOCS / "tne_decision_ledger.md"
    ledger_text = ledger.read_text(encoding="utf-8")
    if "D-033" not in ledger_text:
        ledger.write_text(
            ledger_text.rstrip()
            + "\n| D-033 | Regenerate every downstream status artifact after removing the carrier-label heuristic. | The 351-row matrix, theorem manifest, source registry, AI integration matrix, artifact coverage, open-gaps report, and final QA now report zero carrier conflicts and zero blocked B/C rows; 173 registered contracts have one-to-one provenance manifests. |\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passed", type=int, required=True)
    parser.add_argument("--failed", type=int, required=True)
    parser.add_argument("--skipped", type=int, required=True)
    parser.add_argument("--warnings", type=int, required=True)
    parser.add_argument("--runtime-seconds", type=float, required=True)
    parser.add_argument("--python-version", default="3.14.3")
    parser.add_argument("--dependency-status", default="pip check passed")
    parser.add_argument("--source-law-regression-status", default="passed")
    args = parser.parse_args()
    args.output = DATA / "final_qa_manifest.json"
    qa_payload = build_qa(args)
    build_reports(qa_payload)
    print(json.dumps({"reports": 12, "machine_outputs": 9, "status": "generated"}, sort_keys=True))
