"""Runtime-derived state contract for TNE AI visual evidence.

The helpers in this module never invent activations, coordinates, or graph
weights.  They reduce tensors returned by QENN, PGQENN, and SOInet into a
common finite snapshot used by the generic artifact renderers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch


@dataclass(frozen=True)
class ArchitectureRuntimeState:
    architecture: str
    node_activation: np.ndarray
    activation_trace: np.ndarray
    coordinates: np.ndarray
    adjacency: np.ndarray
    streams: tuple[str, ...]
    signed_coordinates: np.ndarray
    signed_adjacency: np.ndarray
    partner: np.ndarray
    source_status: str = "runtime_derived_model_state"


def _numpy(value: torch.Tensor) -> np.ndarray:
    return value.detach().cpu().to(dtype=torch.float64).numpy()


def _normalize_vector(value: np.ndarray) -> np.ndarray:
    vector = np.asarray(value, dtype=float).reshape(-1)
    if vector.size == 0:
        return np.zeros(1, dtype=float)
    minimum = float(np.min(vector))
    maximum = float(np.max(vector))
    if maximum - minimum <= 1e-12:
        scale = max(abs(maximum), 1.0)
        return np.clip(np.abs(vector) / scale, 0.0, 1.0)
    return np.clip((vector - minimum) / (maximum - minimum), 0.0, 1.0)


def _resample(value: np.ndarray, size: int) -> np.ndarray:
    vector = np.asarray(value, dtype=float).reshape(-1)
    if vector.size == size:
        return vector
    if vector.size == 1:
        return np.repeat(vector, size)
    source = np.linspace(0.0, 1.0, vector.size)
    target = np.linspace(0.0, 1.0, size)
    return np.interp(target, source, vector)


def _coordinates(matrix: torch.Tensor) -> np.ndarray:
    state = _numpy(matrix)
    if state.ndim == 1:
        state = state[:, None]
    state = state.reshape(state.shape[0], -1)
    centered = state - state.mean(axis=0, keepdims=True)
    if centered.shape[0] == 1:
        return np.zeros((1, 3), dtype=float)
    left, singular, _ = np.linalg.svd(centered, full_matrices=False)
    width = min(3, left.shape[1], singular.size)
    result = np.zeros((centered.shape[0], 3), dtype=float)
    result[:, :width] = left[:, :width] * singular[:width]
    scale = max(float(np.max(np.abs(result))), 1e-12)
    return np.clip(result / scale, -1.0, 1.0)


def _state_adjacency(matrix: torch.Tensor) -> np.ndarray:
    state = _numpy(matrix)
    if state.ndim == 1:
        state = state[:, None]
    state = state.reshape(state.shape[0], -1)
    norm = np.linalg.norm(state, axis=1, keepdims=True)
    normalized = state / np.maximum(norm, 1e-12)
    adjacency = np.abs(normalized @ normalized.T)
    np.fill_diagonal(adjacency, 0.0)
    return adjacency


def _signed_lift(
    coordinates: np.ndarray,
    adjacency: np.ndarray,
    activation: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count = len(coordinates)
    negative = -coordinates
    signed_coordinates = np.concatenate((coordinates, negative), axis=0)
    signed_adjacency = np.zeros((2 * count, 2 * count), dtype=float)
    signed_adjacency[:count, :count] = adjacency
    signed_adjacency[count:, count:] = adjacency
    partner_weight = 0.15 + 0.7 * _resample(_normalize_vector(activation), count)
    indices = np.arange(count)
    signed_adjacency[indices, count + indices] = partner_weight
    signed_adjacency[count + indices, indices] = partner_weight
    partner = np.concatenate((count + indices, indices))
    return signed_coordinates, signed_adjacency, partner


def _dtqc_trace(dtqc_state: Any | None, fallback: torch.Tensor) -> np.ndarray:
    if dtqc_state is None or getattr(dtqc_state, "trajectory", None) is None:
        values = np.abs(_numpy(fallback).reshape(fallback.shape[0], -1))
        return values
    trajectory = _numpy(dtqc_state.trajectory)
    return np.abs(trajectory.reshape(trajectory.shape[0], -1))


def capture_runtime_state(
    architecture: str,
    result: Any,
    *,
    network_node_count: int,
) -> ArchitectureRuntimeState:
    """Reduce one real architecture output to a common artifact snapshot."""

    architecture = architecture.lower()
    if architecture == "qenn":
        matrix = result.hidden
        trace = _dtqc_trace(result.dtqc_state, result.hidden)
        streams = tuple(
            ("invariant", "anti_invariant", "dtqc_memory", "closure")[index % 4]
            for index in range(matrix.shape[0])
        )
        adjacency = _state_adjacency(matrix)
    elif architecture == "pgqenn":
        matrix = result.node_state
        trace = _dtqc_trace(result.qenn_backbone_output.dtqc_state, result.node_state)
        graph_adjacency = result.graph.message_adjacency
        adjacency = _numpy(graph_adjacency)
        streams = tuple(
            result.mpl_motifs[index % len(result.mpl_motifs)]
            if result.mpl_motifs
            else "prime_growth"
            for index in range(matrix.shape[0])
        )
    elif architecture == "soinets":
        states = [output.hidden.mean(dim=0) for output in result.qenn_outputs]
        states.extend(output.hidden.mean(dim=0) for output in result.pgqenn_outputs)
        if result.memory_transfers is not None:
            states.extend(result.memory_transfers)
        matrix = torch.stack(states)
        trace_rows = [
            np.abs(_numpy(output.hidden).reshape(-1))
            for output in (*result.qenn_outputs, *result.pgqenn_outputs)
        ]
        trace_rows.append(np.abs(_numpy(result.meta_state).reshape(-1)))
        width = max(row.size for row in trace_rows)
        trace = np.stack([_resample(row, width) for row in trace_rows])
        adjacency = _numpy(result.meta_adjacency)
        streams = tuple(
            ["qenn"] * len(result.qenn_outputs)
            + ["pgqenn"] * len(result.pgqenn_outputs)
            + ["memory_transfer"] * max(0, matrix.shape[0] - len(result.qenn_outputs) - len(result.pgqenn_outputs))
        )
    else:
        raise ValueError(f"unknown runtime architecture {architecture!r}")

    coordinates = _coordinates(matrix)
    if adjacency.shape != (len(coordinates), len(coordinates)):
        adjacency = _state_adjacency(matrix)
    activation = np.linalg.norm(_numpy(matrix).reshape(matrix.shape[0], -1), axis=1)
    node_activation = _normalize_vector(_resample(activation, network_node_count))
    activation_trace = np.stack(
        [_normalize_vector(_resample(row, network_node_count)) for row in trace]
    )
    if activation_trace.shape[0] < 10:
        repeats = int(np.ceil(10 / activation_trace.shape[0]))
        activation_trace = np.tile(activation_trace, (repeats, 1))[:10]
    signed_coordinates, signed_adjacency, partner = _signed_lift(
        coordinates, adjacency, activation
    )
    return ArchitectureRuntimeState(
        architecture=architecture,
        node_activation=node_activation,
        activation_trace=activation_trace,
        coordinates=coordinates,
        adjacency=adjacency,
        streams=streams,
        signed_coordinates=signed_coordinates,
        signed_adjacency=signed_adjacency,
        partner=partner,
    )
