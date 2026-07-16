from __future__ import annotations

import json

from the_nothingness_effect.artificial_intelligence.multimodal.artifacts import (
    run_multimodal_pipeline_artifacts,
)


def test_multimodal_pipeline_writes_diverse_training_validation_evaluation_evidence(
    tmp_path,
):
    result = run_multimodal_pipeline_artifacts(
        tmp_path / "multimodal" / "test" / "artifacts",
        seed=0,
        epochs=2,
        simulation=False,
    )

    assert len(result["tables"]) == 7
    assert len(result["figures"]) == 12
    assert len(result["animations"]) == 5
    assert all(path.is_file() for path in result["tables"])
    assert all(path.is_file() for path in result["figures"])
    assert all(path.is_file() for path in result["animations"])
    payload = json.loads(result["manifest"].read_text(encoding="utf-8"))
    assert payload["source_status"] == "synthetic_deterministic_training_fixture"
    assert len(payload["generated_files"]) == 24
    assert "not a formal proof substitute" in payload["claim_boundary"]
