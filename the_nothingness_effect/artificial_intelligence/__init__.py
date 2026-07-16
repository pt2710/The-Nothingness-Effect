"""Canonical differentiable TNE AI architecture."""

from .bidirectional_color_classification import BidirectionalColorClassifier
from .bidirectional_sound_classification import BidirectionalSoundClassifier
from .color_classification import ColorClassifier
from .color_cloning import ColorCloner
from .multimodal import TNETrainableMultimodalModel
from .sound_classification import SoundClassifier
from .sound_cloning import SoundCloner

__all__ = [
    "BidirectionalColorClassifier",
    "BidirectionalSoundClassifier",
    "ColorClassifier",
    "ColorCloner",
    "TNETrainableMultimodalModel",
    "SoundClassifier",
    "SoundCloner",
]
