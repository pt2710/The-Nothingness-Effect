"""Run the deterministic pDFI producer with the byte-faithful C01 contract."""

from __future__ import annotations

from pathlib import Path

from the_nothingness_effect.fluctuation_and_elastic_dynamics import artifacts

from . import contracts as legacy_contracts
from .authoritative_product_contracts import contracts as active_contracts


def run_suite(output_dir: str | Path, *, seed: int = 0):
    contract_tuple = active_contracts()
    previous_factory = legacy_contracts.contracts
    legacy_contracts.contracts = lambda: contract_tuple
    try:
        return artifacts.run_suite("pdfi", output_dir, seed=seed)
    finally:
        legacy_contracts.contracts = previous_factory
