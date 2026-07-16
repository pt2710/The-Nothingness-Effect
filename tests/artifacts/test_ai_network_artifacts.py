from __future__ import annotations

import json

import pytest
from PIL import Image

from the_nothingness_effect.artificial_intelligence.shared.network_artifacts import (
    generate_architecture_network_artifacts,
)


@pytest.mark.parametrize("architecture", ("qenn", "pgqenn", "soinets"))
def test_each_ai_architecture_generates_network_topology_and_animations(
    tmp_path, architecture
) -> None:
    result = generate_architecture_network_artifacts(
        architecture,
        tmp_path / architecture / "test" / "artifacts",
        observation=(0.15, 0.25, 0.6),
        residuals={"closure": 0.04, "source_removal": 0.2},
        seed=2,
        simulation=False,
    )

    assert len(result["figures"]) == 3
    assert len(result["animations"]) == 3
    assert result["table"].is_file()
    for movie in result["animations"]:
        with Image.open(movie) as image:
            assert image.is_animated
            assert image.n_frames >= 10
    manifest = json.loads(result["manifest"].read_text(encoding="utf-8"))
    assert manifest["artifact_family"] == "network_topology_and_activation"
    assert len(manifest["generated_files"]) == 7
