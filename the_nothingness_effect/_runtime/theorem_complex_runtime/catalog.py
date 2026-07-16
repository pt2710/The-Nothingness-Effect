"""Canonical theorem-complex catalog with explicit Countable-Infinity registration.

The prior catalog implementation is preserved byte-identically in
``_catalog_impl.py``.  This adapter extends its module registry with the six
canonical Countable-Infinity contracts while delegating all catalog semantics,
release closure, and cache behavior to the preserved implementation.
"""

from __future__ import annotations

from . import _catalog_impl as _impl


_COUNTABLE_MODULE = (
    "the_nothingness_effect.foundational_architecture.countable_infinity."
    "canonical_contracts",
    "contracts",
)
if _COUNTABLE_MODULE not in _impl.CONTRACT_MODULES:
    _impl.CONTRACT_MODULES = (*_impl.CONTRACT_MODULES, _COUNTABLE_MODULE)

CONTRACT_MODULES = _impl.CONTRACT_MODULES
all_contracts = _impl.all_contracts
release_statuses = _impl.release_statuses
dependency_downgrades = _impl.dependency_downgrades
active_contracts = _impl.active_contracts
release_active_contracts = _impl.release_active_contracts


def __getattr__(name: str):
    """Delegate compatibility access to the preserved catalog implementation."""

    return getattr(_impl, name)
