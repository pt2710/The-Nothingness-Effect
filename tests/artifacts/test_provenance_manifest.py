from __future__ import annotations

import json

from the_nothingness_effect._runtime.theorem_complex_runtime import ClosureStatus, ComplexId, SimulationResult
from the_nothingness_effect._runtime.theorem_complex_runtime.artifacts import write_artifact_manifest
from the_nothingness_effect._runtime.theorem_complex_runtime.provenance import build_manifest


def test_manifest_contains_required_claim_boundary_and_reproduction_fields(theorem_artifact_dir):
    result = SimulationResult(
        complex_id=ComplexId("runtime_smoke"),
        closure_status=ClosureStatus.NUMERICAL_CANDIDATE,
        parameters={"steps": 4},
        seed=0,
        numeric_tolerances={"absolute": 1e-8},
        residual_vector=(1e-10,),
        generated_files=("metrics.csv",),
    )
    manifest = build_manifest(
        result,
        appendix_filename="external_appendix.tex",
        appendix_source_sha256="0" * 64,
        repository_start_commit="a" * 40,
        repository_result_commit="b" * 40,
        regeneration_command="python -m example",
    )
    path = write_artifact_manifest(theorem_artifact_dir / "manifest.json", manifest)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["claim_boundary"] == "finite computational support; not a formal proof substitute"
    assert payload["parameter_hash"]
    assert payload["closure_status"] == "numerical_candidate"
    assert payload["regeneration_command"] == "python -m example"
