"""Bounded AI provenance metadata."""

from __future__ import annotations

import torch


def backend_metadata() -> dict[str, str | bool]:
    return {
        "backend": "torch",
        "torch_version": torch.__version__,
        "device": "cpu",
        "differentiable": True,
        "formal_proof_substitute": False,
    }
