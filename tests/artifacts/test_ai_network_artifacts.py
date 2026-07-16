from __future__ import annotations

import json

import pytest
from PIL import Image

from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel
from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel
from the_nothingness_effect.artificial_intelligence.shared.architecture_capability_artifacts import (
    _evaluate_architecture,
)
from the_nothingness_effect.artificial_intelligence.shared.network_artifacts import (
    generate_architecture_network_artifacts,
)
from the_nothingness_effect.artificial_intelligence.soinets.model import SOInetModel


_MODELS = {
    "qenn": QENNModel,
    "pgqenn": PGQENNModel,
    "soinets": SOInetModel,
}


@pytest.mark.parametrize("architecture", ("qenn", "pgqenn", "soinets"))
def test_each_ai_architecture_generates_runtime_network_topology_and_animations(
    tmp_path, architecture
) -> None:
    architecture_result = _evaluate_architecture(
        architecture, _MODELS[architecture], seed=2
    )
    result = generate_architecture_network_artifacts(
        architecture,
        tmp_path / architecture / "test" / "artifacts",
        observation=architecture_result["observation"],
        residuals=architecture_result["residuals"],
        runtime_state=architecture_result["runtime_state"],
        seed=2,
        simulation=False,
    )

    expected_figures = 12
    expected_animations = 10
    assert len(result["figures"]) == expected_figures
    assert len(result["animations"]) == expected_animations
    assert result["table"].is_file()
    for movie in result["animations"]:
        with Image.open(movie) as image:
            assert image.is_animated
            assert image.n_frames >= 10
    manifest = json.loads(result["manifest"].read_text(encoding="utf-8"))
    assert manifest["artifact_family"] == "network_topology_and_activation"
    assert manifest["source_status"] == "runtime_derived_network_state"
    assert manifest["parameters"]["network_state_source"] == "runtime_derived_model_state"
    expected_generated = 30 if architecture == "pgqenn" else 28
    assert len(manifest["generated_files"]) == expected_generated
    assert result["spatial_growth"] is not None
    assert any("signed_spectrum_growth" in path.name for path in result["figures"])
    assert any("signed_spectrum_growth" in path.name for path in result["animations"])
    if architecture == "pgqenn":
        assert result["spatial_growth"]["graph"].triadic_growth.stream_counts
        assert any("triadic_stream_matrix" in path.name for path in result["figures"])
        assert any("triadic_stream_growth" in path.name for path in result["animations"])
        signed = result["spatial_growth"]["graph"].signed_triadic_growth
        assert signed.value_involution_residual == 0.0
        assert signed.coordinate_asymmetry > 0.0
    else:
        assert result["spatial_growth"]["partner_involution_residual"] == 0
        spatial_manifest = json.loads(
            result["spatial_growth"]["manifest"].read_text(encoding="utf-8")
        )
        assert spatial_manifest["source_status"] == "runtime_derived_spatial_state"
