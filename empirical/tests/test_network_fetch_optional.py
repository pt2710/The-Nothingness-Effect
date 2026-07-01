from __future__ import annotations

import pytest

from empirical.data_acquisition.fetch_galaxy_rotation_data import run


@pytest.mark.network
def test_live_galaxy_fetch_writes_public_dataset(tmp_path):
    payload = run(output_dir=tmp_path, offline=False, force=False, quick=True)
    assert payload["status"] in {"fetched", "cached"}
