"""Canonical Spectrum-Of-Infinities neural meta-network."""

from .model import SOInetModel, SOInetOutput
from .multimodal import TNEMultimodalOutput, TNEMultimodalSOInet

__all__ = [
    "SOInetModel",
    "SOInetOutput",
    "TNEMultimodalOutput",
    "TNEMultimodalSOInet",
]
