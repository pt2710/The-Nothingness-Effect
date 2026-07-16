from __future__ import annotations

import math

import pytest
import torch

from the_nothingness_effect.artificial_intelligence.shared.capability_artifacts import (
    CAPABILITIES,
    run_capability_test,
)
from the_nothingness_effect.artificial_intelligence.shared.soinet_capability_runtime import (
    capability_dataset,
    evaluate_capability_with_soinet,
    multi_seed_benchmark,
)
from the_nothingness_effect.artificial_intelligence.shared.soinet_large_benchmark import (
    PROFILE_NAME,
    evaluate_large_capability,
    large_capability_dataset,
)


@pytest.mark.parametrize("capability", CAPABILITIES)
def test_each_capability_is_scored_from_soinet_with_held_out_data(capability: str) -> None:
    evaluation = evaluate_capability_with_soinet(
        capability, seed=7, simulation=False
    )
    assert evaluation.payload["metric_producer"] == "SOInet"
    assert evaluation.checkpoint["metric_producer"] == "SOInet"
    assert evaluation.checkpoint["train_samples"] > 0
    assert evaluation.checkpoint["validation_samples"] > 0
    assert evaluation.checkpoint["test_samples"] > 0
    assert "generalization_gap" in evaluation.metrics
    assert all(math.isfinite(float(value)) for value in evaluation.metrics.values())
    assert evaluation.rows
    assert all(row["metric_producer"] == "SOInet" for row in evaluation.rows)


def test_capability_checkpoint_roundtrip_contains_model_and_task_head(tmp_path) -> None:
    outputs = run_capability_test("color_classification", tmp_path, seed=11)
    checkpoint = torch.load(outputs["checkpoint"], weights_only=False)
    assert checkpoint["capability"] == "color_classification"
    assert checkpoint["metric_producer"] == "SOInet"
    assert checkpoint["model_state_dict"]
    assert checkpoint["task_head"].ndim == 2
    assert outputs["splits"].is_file()


def test_multiseed_benchmark_covers_all_six_capabilities() -> None:
    rows = multi_seed_benchmark(CAPABILITIES, seeds=(2, 5), simulation=False)
    assert len(rows) == 2 * len(CAPABILITIES)
    assert {row["capability"] for row in rows} == set(CAPABILITIES)
    assert {row["seed"] for row in rows} == {2, 5}
    assert all(row["metric_producer"] == "SOInet" for row in rows)
    assert all("generalization_gap" in row for row in rows)


@pytest.mark.parametrize("capability", CAPABILITIES)
def test_large_benchmark_profile_is_materially_larger_than_smoke(capability: str) -> None:
    smoke = capability_dataset(capability, seed=3, simulation=False)
    large = large_capability_dataset(capability, seed=3)

    assert len(large.train_samples) > len(smoke.train_samples)
    assert len(large.validation_samples) > len(smoke.validation_samples)
    assert len(large.test_samples) > len(smoke.test_samples)


def test_large_benchmark_metrics_are_still_soinet_coupled() -> None:
    evaluation = evaluate_large_capability("sound_classification", seed=4)

    assert evaluation.row["profile"] == PROFILE_NAME
    assert evaluation.row["metric_producer"] == "SOInet"
    assert evaluation.row["train_samples"] == 12
    assert evaluation.row["validation_samples"] == 6
    assert evaluation.row["test_samples"] == 6
    assert "generalization_gap" in evaluation.row
    assert evaluation.checkpoint["profile"] == PROFILE_NAME
    assert evaluation.checkpoint["model_state_dict"]
    assert evaluation.checkpoint["task_head"].ndim == 2
