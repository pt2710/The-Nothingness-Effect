"""Canonical Spatiality contract registry with recertified source identifiers.

The full operator implementation is preserved byte-identically in
``_canonical_contracts_impl.py``.  This registry wrapper only maps the former
long-form affine compatibility identifier to the active canonical A-contract
identifier used by the dependency-closed theorem catalogue.
"""

from __future__ import annotations

from dataclasses import replace

from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId

from ._canonical_contracts_impl import *  # noqa: F401,F403
from ._canonical_contracts_impl import contracts as _implementation_contracts


_SOURCE_ID_ALIASES = {
    "affine_spatial_involution_orbit_correspondence": (
        "affine_spatial_involution_orbit"
    ),
}


def contracts():
    """Return the canonical contracts with active source IDs normalized."""

    normalized = []
    for contract in _implementation_contracts():
        source_ids = tuple(
            ComplexId(_SOURCE_ID_ALIASES.get(str(source_id), str(source_id)))
            for source_id in contract.source_ids
        )
        normalized.append(replace(contract, source_ids=source_ids))
    return tuple(normalized)
