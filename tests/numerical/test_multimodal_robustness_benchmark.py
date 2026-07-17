from __future__ import annotations

import torch

from tools.run_multimodal_robustness_benchmark import corrupt_batch
from the_nothingness_effect.artificial_intelligence.multimodal.data import (
    make_synthetic_multimodal_dataset,
)


def test_multimodal_corruptions_preserve_typed_batch_and_are_deterministic():
    batch=make_synthetic_multimodal_dataset(samples_per_class=5,seed=3).test
    scenarios=(
        "clean","gaussian_0.05","remove_color","remove_sound","remove_vision",
        "sound_phase_shift","vision_occlusion","color_channel_permutation",
    )
    for scenario in scenarios:
        first=corrupt_batch(batch,scenario,seed=17)
        second=corrupt_batch(batch,scenario,seed=17)
        assert first.labels.shape==batch.labels.shape
        assert set(first.modalities)==set(batch.modalities)
        assert all(torch.equal(first.modalities[name],second.modalities[name]) for name in first.modalities)
        assert all(torch.isfinite(value).all() for value in first.modalities.values())


def test_leave_one_modality_out_zeroes_only_selected_channel():
    batch=make_synthetic_multimodal_dataset(samples_per_class=5,seed=4).test
    removed=corrupt_batch(batch,"remove_sound",seed=0)
    assert torch.count_nonzero(removed.modalities["sound"])==0
    assert torch.equal(removed.modalities["color"],batch.modalities["color"])
    assert torch.equal(removed.modalities["vision"],batch.modalities["vision"])
