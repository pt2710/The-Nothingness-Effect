"""Canonical theorem-complex catalog with explicit Foundational registration.

The prior catalog implementation is preserved byte-identically in
``_catalog_impl.py``. This adapter extends its module registry with the
Countable- and Uncountable-Infinity canonical contracts while delegating
catalog semantics, release closure, and cache behavior to the preserved
implementation.
"""

from __future__ import annotations

from . import _catalog_impl as _impl


_FOUNDATIONAL_MODULES = (
    (
        "the_nothingness_effect.foundational_architecture.countable_infinity."
        "canonical_contracts",
        "contracts",
    ),
    (
        "the_nothingness_effect.foundational_architecture.uncountable_infinity."
        "canonical_contracts",
        "contracts",
    ),
)
for module in _FOUNDATIONAL_MODULES:
    if module not in _impl.CONTRACT_MODULES:
        _impl.CONTRACT_MODULES = (*_impl.CONTRACT_MODULES, module)

CONTRACT_MODULES = _impl.CONTRACT_MODULES
all_contracts = _impl.all_contracts
release_statuses = _impl.release_statuses
dependency_downgrades = _impl.dependency_downgrades
active_contracts = _impl.active_contracts
release_active_contracts = _impl.release_active_contracts


def __getattr__(name: str):
    """Delegate compatibility access to the preserved catalog implementation."""

    return getattr(_impl, name)
