"""Repository-layout and artifact checks for the six TNE AI outputs."""

from __future__ import annotations

import json
from pathlib import Path
import wave

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
AI_ROOT = ROOT / "the_nothingness_effect" / "artificial_intelligence"
CAPABILITIES = (
    "color_classification",
    "sound_classification",
    "bidirectional_color_classification",
    "bidirectional_sound_classification",
    "color_cloning",
    "sound_cloning",
)
LEGACY_DIRECTORIES = (
    "test_bidirectional_color_classification_data",
    "test_bidirectional_sound_classification_data",
    "test_color_classification_data",
    "test_image_cloning_data",
    "test_sound_classification_data",
    "test_sound_cloning_data",
)


def test_legacy_ai_output_directories_are_absent() -> None:
    for name in LEGACY_DIRECTORIES:
        assert not (ROOT / name).exists()
        assert not (ROOT / "tne_concepts" / "SOInet" / name).exists()


def test_capability_artifacts_are_colocated_and_manifested() -> None:
    manifest_count = 0
    animation_count = 0
    wave_count = 0
    for capability in CAPABILITIES:
        capability_root = AI_ROOT / capability
        assert (capability_root / "model.py").is_file()
        assert (capability_root / "test" / "test_capability.py").is_file()
        assert (capability_root / "simulation" / "run_simulation.py").is_file()
        for mode in ("test", "simulation"):
            output = capability_root / mode / "artifacts"
            manifest_path = output / f"{capability}_{mode}_manifest.json"
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_count += 1
            assert data["capability_id"] == capability
            # These are untrained synthetic capability diagnostics, not entries in
            # the 351-row theorem-complex closure ledger. Their nonzero losses must
            # remain truthfully OPEN rather than being promoted by the theorem gate.
            assert data["closure_status"] == "open"
            assert data["source_status"] == ("soinet_architecture_coupled_train_validation_test")
            assert "synthetic" in data["claim_boundary"]
            assert "not a formal proof" in data["claim_boundary"]
            assert len(data["appendix_source_sha256"]) == 64
            for filename in data["generated_files"]:
                assert Path(filename).name == filename
                assert (output / filename).is_file()
            figure_path = output / f"{capability}_{mode}_figure.png"
            with Image.open(figure_path) as figure:
                figure.verify()
            if mode == "simulation":
                animation_path = output / f"{capability}_{mode}_animation.gif"
                with Image.open(animation_path) as movie:
                    assert movie.is_animated
                    assert movie.n_frames >= 10
                animation_count += 1
            for audio_path in output.glob("*.wav"):
                with wave.open(str(audio_path), "rb") as audio:
                    assert audio.getnchannels() == 1
                    assert audio.getframerate() == 8000
                    assert audio.getnframes() >= 2048
                wave_count += 1
    assert manifest_count == 12
    assert animation_count == 6
    assert wave_count == 5
