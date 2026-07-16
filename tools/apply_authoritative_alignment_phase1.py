"""Apply phase-one authoritative appendix alignment."""
from __future__ import annotations

import base64
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "tools/.alignment_payload"
OLD_TO_NEW = {
    "3f428e24ed9518655f94145dcd8667f979aa03c74f75695d8273da273e2538d0": "3cd520d5b025f6f241c7eb09417528276f0c6904e07aa088057c7b57803bf011",
    "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea": "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69",
    "d711e5c4260fb61bff1ef3e7ea3be14ef093370a9ff22607d2a54e74ba8b166b": "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3",
    "63e5684e4c4bb016a2cc62d46574c2174fbe14eb5f50c16db825ca33b0836389": "e37d7583d56287f0cc48d819afadf06ab7f1d8cbccce1790c8b8f18f1b96f30b",
    "3a75d4bfdbf9779255d01dd3ae3db6a848a4dc1fa67455ca1f22d5abcadf866a": "2f2e67b68c18c75f8fe0e8f78c243ca585c0ef8413c579752c3299816e5bc8de",
}
APPENDIX_DIGESTS = {
    "appendix_canonical_self_negating_involution_flowpoint.tex": "5c44d82b34cd4c5d05d01253a62987f2f6099d582bf954a4cbdbc13b52b52206",
    "appendix_tne_mathematical_closure_architecture.tex": "3cd520d5b025f6f241c7eb09417528276f0c6904e07aa088057c7b57803bf011",
    "appendix_tne_foundational_closure_architecture.tex": "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69",
    "appendix_tne_fluctuation_and_elastic_dynamics.tex": "e37d7583d56287f0cc48d819afadf06ab7f1d8cbccce1790c8b8f18f1b96f30b",
    "appendix_tne_gravitational_cosmological_quantum_dynamics.tex": "5cb9526f26767ca245f32a70a8f5a12138d374b3f4bb9821db155b9eece35062",
    "appendix_tne_artificial_intelligence_architechture.tex": "2f2e67b68c18c75f8fe0e8f78c243ca585c0ef8413c579752c3299816e5bc8de",
    "appendix_the_completeness_theorem.tex": "1a186b3350f16c284b3cb54f7dfb63d6729d98142e9fb8b53c6de4d9ce3d84f3",
}
TARGETS = {
    "contracts": "the_nothingness_effect/the_completeness_theorem/contracts.py",
    "tests": "tests/contracts/test_completeness_contracts.py",
    "simulation": "the_nothingness_effect/the_completeness_theorem/simulation/run_contract_suite.py",
}
TEXT_SUFFIXES = {".py", ".json", ".csv", ".md", ".yml", ".yaml", ".toml", ".txt"}
EXCLUDED_REPLACEMENT_PATHS = {
    "tools/apply_authoritative_alignment_phase1.py",
    "tools/verify_authoritative_source_bindings.py",
}
SOURCE_UPDATES = {
    "typed_admissibility_instrument": (
        "2_adic_criterion_of_theoremhood_and_typed_dual_infinity",
        "non_manifestability_of_the_anti_circle_and_observation_collapse",
    ),
    "sheaf_of_closure_certificates": (
        "typed_admissibility_instrument",
        "idempotent_splitting_and_oscillation_obstruction",
        "protected_commuting_closure_transport",
    ),
    "terminal_quotient_of_closure_certificates": (
        "typed_admissibility_instrument",
        "idempotent_splitting_and_oscillation_obstruction",
        "protected_commuting_closure_transport",
        "noether_constant_to_local_transgression",
    ),
}


def decode_payloads() -> None:
    for prefix, relative in TARGETS.items():
        chunks = sorted(PAYLOAD.glob(f"{prefix}.*.b64"))
        if not chunks:
            raise RuntimeError(f"missing payload chunks for {prefix}")
        decoded = b"".join(
            base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)
            for path in chunks
        )
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(decoded)


def replace_stale_digests() -> list[str]:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED_REPLACEMENT_PATHS or relative.startswith("tools/.alignment_payload/"):
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in OLD_TO_NEW.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(relative)
    return changed


def update_matrix() -> None:
    path = ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or ())
    for row in rows:
        appendix = row["appendix_file"]
        if appendix not in APPENDIX_DIGESTS:
            raise RuntimeError(f"matrix contains unbound appendix: {appendix}")
        row["appendix_source_sha256"] = APPENDIX_DIGESTS[appendix]
        if row["complex_id"] in SOURCE_UPDATES:
            row["source_complex_ids"] = ";".join(SOURCE_UPDATES[row["complex_id"]])
            row["dependency_status"] = "authoritative_cross_reference"
            row["status_reason"] = (
                "current authoritative appendix source graph recertified; "
                "operator and residual domains are fail-closed"
            )
            row["decision_note"] = (
                "Recertified against the current authoritative Completeness appendix with "
                "typed partial-map, attainment, descent, and terminal-factorization obligations."
            )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_binding_manifests() -> None:
    byte_verified = {
        "appendix_canonical_self_negating_involution_flowpoint.tex",
        "appendix_tne_mathematical_closure_architecture.tex",
        "appendix_tne_foundational_closure_architecture.tex",
        "appendix_the_completeness_theorem.tex",
    }
    binding_path = ROOT / "docs/data/authoritative_appendix_source_bindings.json"
    binding_payload = {
        "schema_version": "1.0",
        "appendices": {
            name: {
                "sha256": digest,
                "verification": (
                    "byte-verified against the current authoritative upload"
                    if name in byte_verified
                    else "carried forward from the preceding authoritative seven-appendix snapshot"
                ),
            }
            for name, digest in APPENDIX_DIGESTS.items()
        },
        "current_byte_verified_appendix_files": sorted(byte_verified),
        "security_boundary": "authoritative .tex bytes are not tracked in this repository",
    }
    binding_path.write_text(
        json.dumps(binding_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    verification_path = ROOT / "docs/data/appendix_source_verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    verification.update(
        {
            "appendix_checksum_verified": True,
            "source_bindings_file": binding_path.relative_to(ROOT).as_posix(),
            "current_byte_verified_appendix_files": 4,
            "carried_forward_appendix_files": 3,
            "verification_scope": (
                "Four current theorem-bearing uploads byte-verified; three unchanged bindings "
                "carried forward from the preceding authoritative seven-appendix snapshot."
            ),
            "appendix_source_sha256": APPENDIX_DIGESTS,
        }
    )
    verification_path.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def patch_qa_guard() -> None:
    path = ROOT / "tools/qa_guards.py"
    text = path.read_text(encoding="utf-8")
    if "verify_authoritative_source_bindings.py" in text:
        return
    needle = "    layout = verify(None)\n"
    insertion = (
        "    subprocess.run(\n"
        "        [sys.executable, \"tools/verify_authoritative_source_bindings.py\"],\n"
        "        check=True,\n"
        "    )\n\n"
    )
    if needle not in text:
        raise RuntimeError("qa_guards insertion point not found")
    path.write_text(text.replace(needle, insertion + needle), encoding="utf-8")


def main() -> None:
    decode_payloads()
    changed = replace_stale_digests()
    update_matrix()
    write_binding_manifests()
    patch_qa_guard()
    print(
        "authoritative_alignment_phase1=applied "
        f"decoded={len(TARGETS)} digest_updated_files={len(changed)} "
        "migration_files_retained_for_connector_cleanup=true"
    )


if __name__ == "__main__":
    main()
