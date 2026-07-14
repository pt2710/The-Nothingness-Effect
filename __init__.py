"""Top-level compatibility export.

Pytest may import this file as ``__init__`` when a checkout directory contains
characters that are not valid in a Python package name. Support that collection
mode without mutating ``sys.path`` or hiding unrelated import failures.
"""

if __package__:
    from .the_nothingness_effect import NothingnessEffect
else:
    from the_nothingness_effect import NothingnessEffect

__all__ = ["NothingnessEffect"]
