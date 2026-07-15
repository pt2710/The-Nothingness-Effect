"""Compatibility import for the canonical SOInet runtime.

The historical :mod:`soi_net` module remains available for reproducing legacy
experiments. New code should import from ``equations.artificial_intelligence``.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "tne_concepts.SOInet.canonical is a compatibility path; import "
    "equations.artificial_intelligence.soinets.SOInetModel instead",
    DeprecationWarning,
    stacklevel=2,
)

from equations.artificial_intelligence.soinets import SOInetModel, SOInetOutput

__all__ = ["SOInetModel", "SOInetOutput"]
