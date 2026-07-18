"""Canonical catalog with explicit byte-backed recertification adapters."""
from __future__ import annotations

from . import _catalog_impl as _impl

_MATH_OLD = "the_nothingness_effect.mathematical_architecture.contracts"
_MATH_NEW = "the_nothingness_effect.mathematical_architecture.recertified_contracts"
_COMPLETENESS_OLD = "the_nothingness_effect.the_completeness_theorem.contracts"
_COMPLETENESS_NEW = "the_nothingness_effect.the_completeness_theorem.recertified_contracts"
_DFI_OLD = (
    "the_nothingness_effect.fluctuation_and_elastic_dynamics."
    "dynamic_fluctuation_index.contracts"
)
_DFI_NEW = (
    "the_nothingness_effect.fluctuation_and_elastic_dynamics."
    "dynamic_fluctuation_index.recertified_contracts"
)
_FOUNDATIONAL_PREFIX = "the_nothingness_effect.foundational_architecture."
_FOUNDATIONAL_RECERTIFIED = (
    "the_nothingness_effect.foundational_architecture.recertified_contracts",
    "contracts",
)

rebuilt = []
for module_name, factory_name in _impl.CONTRACT_MODULES:
    if module_name.startswith(_FOUNDATIONAL_PREFIX):
        continue
    if module_name == _MATH_OLD:
        rebuilt.append((_MATH_NEW, factory_name))
    elif module_name == _COMPLETENESS_OLD:
        rebuilt.append((_COMPLETENESS_NEW, factory_name))
    elif module_name == _DFI_OLD:
        rebuilt.append((_DFI_NEW, factory_name))
    else:
        rebuilt.append((module_name, factory_name))

rebuilt.append(_FOUNDATIONAL_RECERTIFIED)
_impl.CONTRACT_MODULES = tuple(rebuilt)
_impl.all_contracts.cache_clear()

CONTRACT_MODULES = _impl.CONTRACT_MODULES
all_contracts = _impl.all_contracts
release_statuses = _impl.release_statuses
dependency_downgrades = _impl.dependency_downgrades
active_contracts = _impl.active_contracts
release_active_contracts = _impl.release_active_contracts


def __getattr__(name: str):
    return getattr(_impl, name)
