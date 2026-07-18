"""Artifact adapter for the byte-faithful DFI product contracts."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.fluctuation_and_elastic_dynamics import artifacts as _base

from . import contracts as _legacy_contracts
from .authoritative_product_contracts import contracts as _active_contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    active = _active_contracts()
    original = _legacy_contracts.contracts
    _legacy_contracts.contracts = lambda: active
    try:
        return _base.run_suite("dfi", output_dir, seed=seed)
    finally:
        _legacy_contracts.contracts = original
