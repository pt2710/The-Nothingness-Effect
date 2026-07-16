"""Canonical Spectrum-Of-Infinities neural meta-network.

Torch-backed model exports are lazy so theorem-contract modules remain
available in backend-neutral environments.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


_LAZY_EXPORTS = {
    "SOInetModel": (".model", "SOInetModel"),
    "SOInetOutput": (".model", "SOInetOutput"),
    "TNEMultimodalOutput": (".multimodal", "TNEMultimodalOutput"),
    "TNEMultimodalSOInet": (".multimodal", "TNEMultimodalSOInet"),
}

__all__ = list(_LAZY_EXPORTS)


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
