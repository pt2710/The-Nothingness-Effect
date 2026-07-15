"""Top-level compatibility export.

Pytest may import this file as ``__init__`` when a checkout directory contains
characters that are not valid in a Python package name. Support that collection
mode without mutating ``sys.path`` or hiding unrelated import failures.
"""

__all__ = ["NothingnessEffect"]


def __getattr__(name: str):
    """Lazily expose the relocated facade without affecting pytest bootstrap."""

    if name != "NothingnessEffect":
        raise AttributeError(name)
    if __package__:
        from .fields_of_physics_in_dev.the_nothingness_effect import NothingnessEffect
    else:
        from fields_of_physics_in_dev.the_nothingness_effect import NothingnessEffect
    return NothingnessEffect
