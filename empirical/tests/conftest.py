from __future__ import annotations

import pytest

from empirical.comparison.run_empirical_comparisons import run_empirical_comparisons


@pytest.fixture(scope="session")
def empirical_fixture_run(tmp_path_factory: pytest.TempPathFactory):
    output_dir = tmp_path_factory.mktemp("empirical_outputs")
    return run_empirical_comparisons(
        output_dir=output_dir,
        dataset="all",
        offline=True,
        use_fixtures=True,
        quick=True,
    )
