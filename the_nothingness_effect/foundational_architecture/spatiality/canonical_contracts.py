"""Canonical Spatiality contract registry with recertified source identifiers.

The full operator implementation is preserved byte-identically in
``_canonical_contracts_impl.py``. This registry wrapper maps the former
long-form affine compatibility identifier to the active canonical A-contract
identifier used by both dependency closure and source-removal evidence.
"""

from __future__ import annotations

from dataclasses import replace
from functools import wraps

from the_nothingness_effect._runtime.theorem_complex_runtime import ComplexId

from ._canonical_contracts_impl import *  # noqa: F401,F403
from ._canonical_contracts_impl import contracts as _implementation_contracts


_SOURCE_ID_ALIASES = {
    "affine_spatial_involution_orbit_correspondence": (
        "affine_spatial_involution_orbit"
    ),
}


def _active_id(source_id) -> ComplexId:
    return ComplexId(_SOURCE_ID_ALIASES.get(str(source_id), str(source_id)))


def _normalized_check(check):
    @wraps(check)
    def wrapped(value):
        result = check(value)
        return replace(result, source_id=_active_id(result.source_id))

    return wrapped


def contracts():
    """Return canonical contracts with active source IDs normalized."""

    normalized = []
    for contract in _implementation_contracts():
        normalized.append(
            replace(
                contract,
                source_ids=tuple(_active_id(source_id) for source_id in contract.source_ids),
                source_removal_checks=tuple(
                    _normalized_check(check) for check in contract.source_removal_checks
                ),
            )
        )
    return tuple(normalized)
