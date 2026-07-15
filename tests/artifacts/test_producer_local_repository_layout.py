"""Guards for the producer-local hierarchy requested by the repository owner."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EQUATIONS = ROOT / "equations"
AI = EQUATIONS / "artificial_intelligence"
AI_ARCHITECTURES = ("qenn", "pgqenn", "soinets")
CAPABILITIES = (
    "color_classification",
    "sound_classification",
    "bidirectional_color_classification",
    "bidirectional_sound_classification",
    "color_cloning",
    "sound_cloning",
)
LOCAL_MODULES = (
    "cosmological_spark_dynamics",
    "dtqc",
    "elastic_dubler_interferometry",
    "elastic_pi_norm",
    "mathematical_closure",
    "parity_dfi",
)


def test_removed_legacy_trees_and_loose_equation_infrastructure_are_absent() -> None:
    forbidden = (
        EQUATIONS / "mccrackns_prime_law",
        EQUATIONS / "numbers_domains",
        ROOT / "figures_mccrackn",
        ROOT / "figures",
        ROOT / "tne_concepts",
        ROOT / "theoretical_benchmarks",
    )
    assert all(not path.exists() for path in forbidden)
    assert not list(ROOT.rglob("framework"))
    loose_names = {
        "theorem_complex_runtime", "animation_artifacts_metadata.json",
        "animation_artifacts_summary.csv", "animation_io.py", "artifact_io.py",
        "fluctuation_elastic_artifacts.py", "gravitational_contract_artifacts.py",
        "gravitational_contract_runtime.py", "run_animation_artifacts.py",
    }
    assert not any((EQUATIONS / name).exists() for name in loose_names)


def test_relocated_runtime_facade_audits_and_hawking_benchmarks_exist() -> None:
    assert (ROOT / "tne_runtime" / "theorem_complex_runtime" / "types.py").is_file()
    assert (ROOT / "tne_runtime" / "artifacts" / "io.py").is_file()
    physics = ROOT / "fields_of_physics_in_dev"
    assert (physics / "the_nothingness_effect.py").is_file()
    assert (physics / "fields_of_physics_in_dev_audit.csv").is_file()
    assert (physics / "fields_of_physics_in_dev_audit.json").is_file()
    hawking = EQUATIONS / "black_hole_dynamics" / "hawking"
    assert (hawking / "test" / "theoretical_benchmarks" / "test_hawking_formulas.py").is_file()
    assert (
        hawking / "simulation" / "theoretical_benchmarks" / "simulate_hawking_theoretical_benchmark.py"
    ).is_file()
    assert list((hawking / "simulation").glob("*.png"))


def test_each_ai_architecture_owns_all_six_test_and_simulation_outputs() -> None:
    for architecture in AI_ARCHITECTURES:
        root = AI / architecture
        for mode in ("test", "simulation"):
            producer = root / mode
            assert (producer / "run_all_capabilities.py").is_file()
            aggregate = json.loads(
                (producer / f"{architecture}_{mode}_six_output_manifest.json").read_text(encoding="utf-8")
            )
            assert aggregate["capability_count"] == 6
            assert tuple(aggregate["output_groups"]) == CAPABILITIES
            assert (producer / f"{architecture}_{mode}_architecture_figure.png").is_file()
            for capability in CAPABILITIES:
                capability_dir = producer / capability
                assert (capability_dir / f"{capability}_{mode}_results.csv").is_file()
                assert (capability_dir / f"{capability}_{mode}_figure.png").is_file()
                manifest = json.loads(
                    (capability_dir / f"{capability}_{mode}_manifest.json").read_text(encoding="utf-8")
                )
                assert manifest["producer_architecture"] == architecture
                if mode == "simulation":
                    movie = capability_dir / f"{capability}_{mode}_animation.gif"
                    with Image.open(movie) as image:
                        assert image.is_animated
                        assert image.n_frames >= 10


def test_requested_theorem_modules_own_test_and_simulation_evidence() -> None:
    for module in LOCAL_MODULES:
        root = EQUATIONS / module
        assert (root / "test" / "test_evidence.py").is_file()
        assert (root / "simulation" / "run_evidence.py").is_file()
        for mode in ("test", "simulation"):
            producer = root / mode
            assert (producer / f"{module}_{mode}_evidence_manifest.json").is_file()
            movie = producer / f"{module}_{mode}_residual_animation.gif"
            with Image.open(movie) as image:
                assert image.is_animated
                assert image.n_frames >= 10
            assert list(producer.glob("*.csv"))
            assert list(producer.glob("*.png"))


def test_dtqc_recreates_all_five_static_views_and_dynamic_phase_clock() -> None:
    expected = {
        "qc_contour.png", "diffraction_fft.png", "wavelet_central_row.png",
        "dfi_surface.png", "elastic_pi_surface.png",
    }
    for mode in ("test", "simulation"):
        producer = EQUATIONS / "dtqc" / mode
        assert expected.issubset({path.name for path in producer.glob("*.png")})
        with Image.open(producer / "dtqc_phase_clock_animation.gif") as image:
            assert image.is_animated
            assert image.n_frames >= 10
