"""Trainable, visible multimodal TNE architecture."""

from .data import MultimodalDataset, make_synthetic_multimodal_dataset
from .axes import ModalityAxisNetwork, ModalityAxisState
from .evaluation import MultimodalEvaluation, evaluate_multimodal_model
from .growth import AdaptiveModalityClusterNetwork, ClusterGrowthState
from .model import TNETrainableMultimodalModel, TNETrainableMultimodalOutput
from .optimization import (
    DynamicKDSearch,
    DynamicKDSOISearch,
    KDProbe,
    KDSelection,
    validation_objective,
)
from .rbm import GaussianBernoulliEnergyLayer, RBMEnergyState
from .training import MultimodalTrainingRun, train_multimodal_model
from .validation import validate_multimodal_model

__all__ = [
    "MultimodalDataset",
    "MultimodalEvaluation",
    "MultimodalTrainingRun",
    "ModalityAxisNetwork",
    "ModalityAxisState",
    "AdaptiveModalityClusterNetwork",
    "ClusterGrowthState",
    "GaussianBernoulliEnergyLayer",
    "RBMEnergyState",
    "TNETrainableMultimodalModel",
    "TNETrainableMultimodalOutput",
    "DynamicKDSearch",
    "DynamicKDSOISearch",
    "KDProbe",
    "KDSelection",
    "evaluate_multimodal_model",
    "make_synthetic_multimodal_dataset",
    "train_multimodal_model",
    "validation_objective",
    "validate_multimodal_model",
]
