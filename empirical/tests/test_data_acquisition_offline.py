from __future__ import annotations

from empirical.data_acquisition.fetch_all_empirical_data import run_fetch_all


def test_offline_fetch_summary_is_written(tmp_path):
    result = run_fetch_all(
        dataset="all",
        output_dir=tmp_path,
        offline=True,
        force=False,
        quick=True,
        strict=False,
    )

    statuses = {row["dataset_name"]: row["status"] for row in result["rows"]}
    assert result["summary_paths"]["metrics"].exists()
    assert result["summary_paths"]["manifest"].exists()
    assert set(statuses) == {
        "redshift_clock",
        "galaxy_rotation",
        "eht_observables",
        "ligo_waveforms",
    }
    assert all(status in {"fixture_only", "cached"} for status in statuses.values())
