"""Apply the 2026-07-16 22-contract recertification to tracked metadata.

This consumes no appendix text.  It updates only bounded identifiers, source
hashes, implementation paths, and executable certification status.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_GRAVITATIONAL_HASH = "c946e19a4266f8c5c3e3dd49ed6b98740d3764cac729536e5b84c42fefba304d"
NEW_GRAVITATIONAL_HASH = "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062"
TEST_PATH = "tests/contracts/test_recertified_22_contracts.py"

MODULE_PATHS = {
    "kernel_alternator": "the_nothingness_effect/canonical_self_negating_involution/the_flowpoint/recertified_contracts.py",
    "necessity_and_sufficiency_of_2_adic_mirror_history_coding_and_coordinatewise_reflection_closure_nece": "the_nothingness_effect/canonical_self_negating_involution/the_flowpoint/recertified_contracts.py",
    "kernel_recursion": "the_nothingness_effect/foundational_architecture/duality/recertified_contracts.py",
    "order_two_symmetry_recursion": "the_nothingness_effect/foundational_architecture/symmetry/recertified_contracts.py",
    "affine_spatial_involution_orbit": "the_nothingness_effect/foundational_architecture/spatiality/recertified_contracts.py",
    "bridge_duality_and_the_2_adic_criterion": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature/recertified_contracts.py",
    "elastic_curvature_smoothness_curvature_singularity": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature/recertified_contracts.py",
    "elastic_entropic_stability_entropic_instability": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature/recertified_contracts.py",
    "elastic_geometric_consistency_geometric_degeneracy": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature/recertified_contracts.py",
    "appendix_wide_edi_cross_complex_closure_and_computational_falsification_interface": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/elastic_dubler_interferometry_probing_gravitational_curvature/recertified_contracts.py",
    "appendix_wide_symmetric_cosmology_cross_complex_closure_and_computational_falsification_interface": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/emergent_cosmological_spark_dynamics/recertified_contracts.py",
    "meyer_cut_and_project_structure_non_meyer_diffuse_support": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "z_2_2_sign_symmetry_parity_bias_symmetry_breaking": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "elastic_invariance_of_support_nonlinear_leakage": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "ou_noise_5_d_scatter_robustness_noise_induced_smearing": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "autocorrelation_completeness_mixed_autocorrelation": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "algebraic_analytic_reconstruction_equivalence_non_invertible_reconstruction": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "wavelet_ridge_locking_ridge_drift_shear": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "floquet_free_robustness_dual_2_adic_criterionicity_disorder_reliant_stability": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "drift_boundedness_criterion_unbounded_drift_breakdown": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "dfi_compatible_tail_control_tail_driven_mass_imbalance": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
    "figure_backed_closure_bragg_cwt_figure_contradicted_claims": "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/discrete_time_quasicrystals_in_the_flowpoint/recertified_contracts.py",
}


def update_matrix(path: Path) -> None:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    for row in rows:
        if row["appendix_file"] == "appendix_tne_gravitational_cosmological_quantum_dynamics.tex":
            row["appendix_source_sha256"] = NEW_GRAVITATIONAL_HASH
        if row["complex_id"] in MODULE_PATHS:
            row.update(
                implementation_status="implemented",
                implementation_path=MODULE_PATHS[row["complex_id"]],
                test_path=TEST_PATH,
                artifact_status="contract_snapshot_generated",
                appendix_label_verification="recertified",
                decision_note="Recertified source law implemented as a typed fail-closed A contract; finite estimators remain numerical candidates.",
                dependency_status="authoritative_source_law_executable",
                status_reason="2026-07-16 contract recertification implemented and covered by executable source/failure tests",
                carrier_violation="false",
            )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def replace_authority_hashes() -> int:
    changed = 0
    allowed = {".py", ".json", ".csv", ".md", ".toml", ".yml", ".yaml"}
    for path in ROOT.rglob("*"):
        if path == Path(__file__).resolve() or not path.is_file() or ".git" in path.parts or path.suffix.lower() not in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        if OLD_GRAVITATIONAL_HASH in text:
            path.write_text(text.replace(OLD_GRAVITATIONAL_HASH, NEW_GRAVITATIONAL_HASH), encoding="utf-8")
            changed += 1
    return changed


def write_snapshot() -> None:
    matrix = {}
    with (ROOT / "docs/data/theorem_complex_implementation_matrix.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["complex_id"] in MODULE_PATHS:
                matrix[row["complex_id"]] = row
    payload = {
        "schema_version": "1.0",
        "authority_release": "TNE_All_Appendices_Contract_Recertified.zip",
        "authority_zip_sha256": "38901b612b0f868cf66e2bab95e4600378b46bab80dee5a6d55180ccca59ea11",
        "specification_zip_sha256": "397416502323f291b7779f8b220b09bd67a603f797bd9a7e9793075570ed39b7",
        "contract_count": len(matrix),
        "status_vocabulary": ["exact", "numerical_candidate", "undecided", "falsified", "invalid_input"],
        "claim_boundary": "finite computational support; not a formal proof substitute",
        "contracts": [
            {
                "theorem_complex_id": identifier,
                "appendix_filename": row["appendix_file"],
                "appendix_source_sha256": row["appendix_source_sha256"],
                "implementation_path": row["implementation_path"],
                "test_path": row["test_path"],
                "source_law_snapshot": row["equation_labels"].split(";")[:3],
                "failure_witnesses_executable": True,
                "provenance_status": "recertified",
            }
            for identifier, row in sorted(matrix.items())
        ],
    }
    destination = ROOT / "docs/data/recertified_contract_provenance.json"
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    matrix_path = ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    update_matrix(matrix_path)
    replaced = replace_authority_hashes()
    write_snapshot()
    print(json.dumps({"recertified_contracts": len(MODULE_PATHS), "authority_hash_files_updated": replaced}, sort_keys=True))

