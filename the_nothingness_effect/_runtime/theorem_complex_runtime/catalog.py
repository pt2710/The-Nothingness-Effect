"""Canonical catalog with explicit byte-backed recertification adapters."""
from __future__ import annotations

from . import _catalog_impl as _impl

_MATH_OLD = "the_nothingness_effect.mathematical_architecture.contracts"
_MATH_NEW = "the_nothingness_effect.mathematical_architecture.recertified_contracts"
_COMPLETENESS_OLD = "the_nothingness_effect.the_completeness_theorem.contracts"
_COMPLETENESS_NEW = "the_nothingness_effect.the_completeness_theorem.recertified_contracts"
_DFI_OLD = "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.contracts"
_DFI_NEW = "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.authoritative_product_contracts"
_PDFI_OLD = "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.contracts"
_PDFI_NEW = "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index.authoritative_product_contracts"
_ELASTIC_PI_OLD = "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.contracts"
_ELASTIC_PI_NEW = "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.authoritative_product_contracts"
_ELASTIC_PI_NORM_OLD = "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.contracts"
_ELASTIC_PI_NORM_NEW = "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm.authoritative_product_contracts"
_QENN_PREFIX = "the_nothingness_effect.artificial_intelligence.qenn."
_QENN_NEW = (
    "the_nothingness_effect.artificial_intelligence.qenn.authoritative_closure_contracts",
    "contracts",
)
_FOUNDATIONAL_PREFIX = "the_nothingness_effect.foundational_architecture."
_FOUNDATIONAL_RECERTIFIED = (
    "the_nothingness_effect.foundational_architecture.recertified_contracts",
    "contracts",
)

rebuilt = []
qenn_inserted = False
for module_name, factory_name in _impl.CONTRACT_MODULES:
    if module_name.startswith(_FOUNDATIONAL_PREFIX):
        continue
    if module_name.startswith(_QENN_PREFIX):
        if not qenn_inserted:
            rebuilt.append(_QENN_NEW)
            qenn_inserted = True
        continue
    if module_name == _MATH_OLD:
        rebuilt.append((_MATH_NEW, factory_name))
    elif module_name == _COMPLETENESS_OLD:
        rebuilt.append((_COMPLETENESS_NEW, factory_name))
    elif module_name == _DFI_OLD:
        rebuilt.append((_DFI_NEW, factory_name))
    elif module_name == _PDFI_OLD:
        rebuilt.append((_PDFI_NEW, factory_name))
    elif module_name == _ELASTIC_PI_OLD:
        rebuilt.append((_ELASTIC_PI_NEW, factory_name))
    elif module_name == _ELASTIC_PI_NORM_OLD:
        rebuilt.append((_ELASTIC_PI_NORM_NEW, factory_name))
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
