from __future__ import annotations

from pathlib import Path

import pytest

from the_nothingness_effect.artificial_intelligence.pgqenn.mpl_tc_dependency import (
    MPL_TC_COMMIT,
    MPL_TC_MODULE_SHA256,
    MPL_TC_REPOSITORY_URL,
    MPLTCDependencyError,
    MPLTCMotifProvider,
)


def test_pinned_mpl_tc_dependency_exposes_motif_prefix_and_provenance():
    provider = MPLTCMotifProvider()
    prefix = provider.prefix(9)

    assert prefix.primes == (2, 3, 5, 7, 11, 13, 17, 19, 23)
    assert prefix.gaps == (0, 1, 2, 2, 4, 2, 4, 2, 4)
    assert len(prefix.motifs) == len(prefix.motif_runs) == len(prefix.primes)
    assert prefix.repository_url == MPL_TC_REPOSITORY_URL
    assert prefix.repository_commit == MPL_TC_COMMIT
    assert prefix.module_sha256 == MPL_TC_MODULE_SHA256


def test_mpl_tc_dependency_is_fail_closed_when_checkout_is_missing(tmp_path: Path):
    with pytest.raises(MPLTCDependencyError, match="submodule update"):
        MPLTCMotifProvider(tmp_path / "missing")
