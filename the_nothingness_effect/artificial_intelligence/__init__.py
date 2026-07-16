"""Canonical differentiable TNE AI architecture.

Model exports are resolved lazily so theorem-contract, metadata, and artifact
modules remain importable without the optional Torch backend. Accessing a
model class still fails normally when the AI extra is not installed.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


_LAZY_EXPORTS = {
    "BidirectionalColorClassifier": (
        ".bidirectional_color_classification",
        "BidirectionalColorClassifier",
    ),
    "BidirectionalSoundClassifier": (
        ".bidirectional_sound_classification",
        "BidirectionalSoundClassifier",
    ),
    "ColorClassifier": (".color_classification", "ColorClassifier"),
    "ColorCloner": (".color_cloning", "ColorCloner"),
    "TNETrainableMultimodalModel": (".multimodal", "TNETrainableMultimodalModel"),
    "SoundClassifier": (".sound_classification", "SoundClassifier"),
    "SoundCloner": (".sound_cloning", "SoundCloner"),
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
