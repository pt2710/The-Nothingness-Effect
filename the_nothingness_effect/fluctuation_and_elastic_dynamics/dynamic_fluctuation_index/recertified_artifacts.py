"""Artifact adapter for the recertified DFI A04/B02 contracts."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.fluctuation_and_elastic_dynamics import artifacts as _base

from . import contracts as _legacy_contracts
from .recertified_contracts import contracts as _recertified_contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    """Run the existing deterministic DFI producer with recertified contracts.

    The recertified tuple is materialized before the temporary module binding.
    This preserves the historical artifact format without making the adapter's
    own ``contracts`` function recursively call itself.
    """

    recertified = _recertified_contracts()
    original = _legacy_contracts.contracts
    _legacy_contracts.contracts = lambda: recertified
    try:
        return _base.run_suite("dfi", output_dir, seed=seed)
    finally:
        _legacy_contracts.contracts = original
