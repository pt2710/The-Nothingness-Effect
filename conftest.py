"""Pytest defaults for headless figure-generating tests."""

import os

os.environ.setdefault("MPLBACKEND", "Agg")

try:
    import matplotlib
except ImportError:
    pass
else:
    matplotlib.use(os.environ["MPLBACKEND"], force=True)
