from __future__ import annotations

from empirical.comparison.run_empirical_comparisons import run_empirical_comparisons
from empirical.io import public_data_path, save_rows, write_manifest


def test_runner_uses_cached_public_data_when_available(tmp_path):
    save_rows(
        public_data_path("eht_public_observables.csv", tmp_path),
        [
            {
                "source": "M87*",
                "ring_diameter": 42.0,
                "ring_diameter_uncertainty": 3.0,
                "shadow_radius": 21.0,
                "shadow_radius_uncertainty": 1.5,
                "source_status": "cached",
            },
            {
                "source": "SgrA*",
                "ring_diameter": 51.8,
                "ring_diameter_uncertainty": 2.3,
                "shadow_radius": 25.9,
                "shadow_radius_uncertainty": 1.2,
                "source_status": "cached",
            },
        ],
    )
    write_manifest(
        tmp_path / "manifests" / "eht_observables_manifest.json",
        {
            "dataset_name": "eht_observables",
            "status": "cached",
            "source_url": "https://arxiv.org/abs/1906.11241",
            "derived_file_path": "empirical/outputs/data/eht_public_observables.csv",
        },
    )

    result = run_empirical_comparisons(
        output_dir=tmp_path,
        dataset="eht",
        fetch=False,
        offline=True,
        use_fixtures=True,
        quick=True,
    )

    assert result["summaries"][0]["data_status"] == "cached"
