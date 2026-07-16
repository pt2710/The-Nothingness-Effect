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

    assert len(result["tables"]) == 14
    assert len(result["figures"]) == 32
    assert len(result["animations"]) == 19
    assert all(path.is_file() for path in result["tables"])
    assert all(path.is_file() for path in result["figures"])
    assert all(path.is_file() for path in result["animations"])
    payload = json.loads(result["manifest"].read_text(encoding="utf-8"))
    assert payload["source_status"] == "synthetic_deterministic_training_fixture"
    assert len(payload["generated_files"]) == 67
    assert payload["parameters"]["dynamic_K_D"]["enabled"] is True
    assert payload["parameters"]["dynamic_K_D"]["probe_count"] >= 6
    assert payload["parameters"]["dynamic_SOI_normalization"]["enabled"] is True
    assert any(path.name == "dynamic_kd_optimization.csv" for path in result["tables"])
    assert any(path.name == "dynamic_kd_trajectory.png" for path in result["figures"])
    assert any(path.name == "dynamic_kd_optimization.gif" for path in result["animations"])
    assert any(path.name == "dynamic_soi_trajectory.png" for path in result["figures"])
    assert any(path.name == "dynamic_kd_soi_validation_landscape.png" for path in result["figures"])
    assert any(path.name == "dynamic_kd_soi_optimization.gif" for path in result["animations"])
    assert result["network"]["manifest"].is_file()
    assert any(path.name.endswith("network_topology.png") for path in result["figures"])
    assert any(path.name.endswith("cluster_growth.gif") for path in result["animations"])
    assert any(path.name.endswith("rbm_reconstruction.gif") for path in result["animations"])
    assert any("signed_spectrum_growth" in path.name for path in result["figures"])
    assert any("signed_spectrum_signal" in path.name for path in result["animations"])
    assert result["network"]["spatial_growth"]["partner_involution_residual"] == 0
    assert "not a formal proof substitute" in payload["claim_boundary"]
