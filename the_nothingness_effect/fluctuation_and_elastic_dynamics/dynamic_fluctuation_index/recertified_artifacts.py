"""Artifact adapter for the recertified and exact-closure DFI contracts."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.fluctuation_and_elastic_dynamics import artifacts as _base

from . import contracts as _legacy_contracts
from .closure_contracts import contracts as _closure_contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    """Run the deterministic DFI producer with the active closure contracts.

    The active tuple is materialized before the temporary module binding. This
    preserves historical artifact formats without recursive contract lookup.
    """

    active = _closure_contracts()
    original = _legacy_contracts.contracts
    _legacy_contracts.contracts = lambda: active
    try:
        return _base.run_suite("dfi", output_dir, seed=seed)
    finally:
        _legacy_contracts.contracts = original
