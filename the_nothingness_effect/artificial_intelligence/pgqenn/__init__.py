"""Canonical prime-grown quasi-entropic neural network.

Torch-backed graph and model classes are exported lazily so contract and
provenance modules remain available in the backend-neutral core environment.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .mpl_tc_dependency import MPLTCDependencyError, MPLTCMotifProvider, MPLTCPrefix


_LAZY_EXPORTS = {
    "CanonicalPrimeGrowth": (".growth_law", "CanonicalPrimeGrowth"),
    "PrimeGraph": (".growth_law", "PrimeGraph"),
    "SignedTriadicGrowthGraph": (".growth_law", "SignedTriadicGrowthGraph"),
    "TriadicGrowthGraph": (".growth_law", "TriadicGrowthGraph"),
    "TwoAdicDepth": (".growth_law", "TwoAdicDepth"),
    "PGQENNModel": (".model", "PGQENNModel"),
    "PGQENNOutput": (".model", "PGQENNOutput"),
}

__all__ = [
    *_LAZY_EXPORTS,
    "MPLTCDependencyError",
    "MPLTCMotifProvider",
    "MPLTCPrefix",
]


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted((*globals(), *__all__))
