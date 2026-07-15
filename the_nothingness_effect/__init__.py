"""Canonical package for The Nothingness Effect architectures.

The seven public architecture packages are direct children of this package.
Legacy physics-development helpers remain outside this namespace and consume
the canonical implementations through absolute imports.
"""

from fields_of_physics_in_dev.the_nothingness_effect import NothingnessEffect

__all__ = ["NothingnessEffect"]

