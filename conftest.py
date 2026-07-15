"""Pytest defaults for headless figure-generating tests."""

import os
import random

import numpy as np
import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

try:
    import matplotlib
except ImportError:
    pass
else:
    matplotlib.use(os.environ["MPLBACKEND"], force=True)


@pytest.fixture(autouse=True)
def _deterministic_test_seed():
    """Reset legacy global RNGs before every test."""

    random.seed(0)
    np.random.seed(0)
    try:
        import torch
    except ImportError:
        pass
    else:
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)


@pytest.fixture(scope="session")
def tne_numeric_tolerances():
    return {"absolute": 1e-10, "relative": 1e-8, "source_removal": 1e-8}


@pytest.fixture
def theorem_artifact_dir(tmp_path):
    path = tmp_path / "theorem_artifacts"
    path.mkdir()
    return path
