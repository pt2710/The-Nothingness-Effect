"""Artifact adapter for the recertified DFI A04/B02 contracts."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.fluctuation_and_elastic_dynamics import artifacts as _base

from . import contracts as _legacy_contracts
from .recertified_contracts import contracts as _recertified_contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    """Run the existing deterministic DFI producer with recertified contracts.

    The base producer imports ``contracts`` at execution time.  The temporary
    binding keeps all historical artifact formats stable while ensuring the
    closure ledger is generated from the authoritative A04/B02 operators.
    """

    original = _legacy_contracts.contracts
    _legacy_contracts.contracts = _recertified_contracts
    try:
        return _base.run_suite("dfi", output_dir, seed=seed)
    finally:
        _legacy_contracts.contracts = original
