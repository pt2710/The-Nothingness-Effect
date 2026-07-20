"""Learned modality axes with explicit 3D frames and dual geometry."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn import functional

from the_nothingness_effect.artificial_intelligence.shared.types import (
    AIObstructionError,
    require_finite_tensor,
)


@dataclass(frozen=True)
class ModalityAxisState:
    modality_names: tuple[str, ...]
    axis_latents: torch.Tensor
    shared_latents: torch.Tensor
    private_latents: torch.Tensor
    mapped_axes: torch.Tensor
    adjacency: torch.Tensor
    reverse_adjacency: torch.Tensor
    reconstructed_axes: torch.Tensor
    fused_axis: torch.Tensor
    geometric_coordinates: torch.Tensor
    dual_coordinates: torch.Tensor
    modality_frames: torch.Tensor
    observer_horizon: torch.Tensor
    mpl_tc_stream_weights: torch.Tensor
    mpl_tc_growth_vectors: torch.Tensor
    residuals: dict[str, torch.Tensor]


def _rotation_x(
    angle: float,
    *,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return torch.tensor(
        [
            [1.0, 0.0, 0.0],
            [0.0, cosine, -sine],
            [0.0, sine, cosine],
        ],
        dtype=dtype,
        device=device,
    )


def _rotation_z(
    angle: float,
    *,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return torch.tensor(
        [
            [cosine, -sine, 0.0],
            [sine, cosine, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=dtype,
        device=device,
    )


def _state_frame(
    *,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    diagonal = torch.tensor(
        [1.0, 1.0, 1.0],
        dtype=dtype,
        device=device,
    )
    diagonal = diagonal / torch.linalg.vector_norm(diagonal)
    tangent_a = torch.tensor(
        [1.0, -1.0, 0.0],
        dtype=dtype,
        device=device,
    )
    tangent_a = tangent_a / torch.linalg.vector_norm(tangent_a)
    tangent_b = torch.cross(
        diagonal,
        tangent_a,
        dim=0,
    )
    return torch.stack(
        (diagonal, tangent_a, tangent_b),
        dim=1,
    )


def _frame_for(
    name: str,
    *,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    normalized = name.lower()
    if normalized == "sound":
        return torch.eye(3, dtype=dtype, device=device)
    if normalized == "vision":
        return _rotation_x(
            -math.pi / 12.0,
            dtype=dtype,
            device=device,
        )
    if normalized == "color":
        return _rotation_x(
            math.pi / 12.0,
            dtype=dtype,
            device=device,
        )
    if normalized == "text":
        return _rotation_z(
            math.pi / 8.0,
            dtype=dtype,
            device=device,
        )
    if normalized == "state":
        return _state_frame(dtype=dtype, device=device)
    checksum = sum(ord(character) for character in normalized)
    angle = (checksum % 17) * math.pi / 34.0
    return _rotation_z(angle, dtype=dtype, device=device)


def _local_geometry(
    name: str,
    value: torch.Tensor,
) -> torch.Tensor:
    normalized = name.lower()
    local = value.clone()
    if normalized in {"vision", "color"}:
        local[..., 0] = 0.0
    elif normalized == "text":
        local[..., 1] = 0.0
    elif normalized == "state":
        scalar = local.mean(dim=-1, keepdim=True)
        local = torch.cat(
            (
                scalar,
                torch.zeros_like(scalar),
                torch.zeros_like(scalar),
            ),
            dim=-1,
        )
    return local


class ModalityAxisNetwork(nn.Module):
    """Map modalities to shared latent axes and explicit rotated 3D frames.

    The same encoder is used for all modalities. Shared/private latent
    coordinates support cross-modal transport, while a separate three
    dimensional projection provides interpretable placement, antipodal duals,
    observer-horizon state and MPL-TC stream-directed growth vectors.
    """

    def __init__(
        self,
        input_dim: int,
        axis_dim: int,
        *,
        shared_dim: int | None = None,
    ) -> None:
        super().__init__()
        if input_dim < 2 or axis_dim < 4:
            raise AIObstructionError(
                "axis input_dim must be >= 2 and axis_dim >= 4"
            )
        split = axis_dim // 2 if shared_dim is None else int(shared_dim)
        if split < 1 or split >= axis_dim:
            raise AIObstructionError(
                "axis shared_dim must lie strictly inside axis_dim"
            )
        self.input_dim = int(input_dim)
        self.axis_dim = int(axis_dim)
        self.shared_dim = split
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, axis_dim, bias=False),
            nn.LayerNorm(axis_dim),
            nn.SiLU(),
        )
        self.forward_transport = nn.Linear(
            axis_dim,
            axis_dim,
            bias=False,
        )
        self.reverse_transport = nn.Linear(
            axis_dim,
            axis_dim,
            bias=False,
        )
        self.geometry_projection = nn.Linear(
            axis_dim,
            3,
            bias=False,
        )
        with torch.no_grad():
            self.forward_transport.weight.copy_(
                torch.eye(axis_dim)
            )
            self.reverse_transport.weight.copy_(
                torch.eye(axis_dim)
            )
            self.geometry_projection.weight.zero_()
            self.geometry_projection.weight[:, :3].copy_(
                torch.eye(3)
            )
        self.log_temperature = nn.Parameter(torch.zeros(()))
        tetrahedral = torch.tensor(
            [
                [1.0, 1.0, 1.0],
                [1.0, -1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, -1.0, 1.0],
            ],
            dtype=torch.float32,
        )
        tetrahedral = functional.normalize(
            tetrahedral,
            dim=-1,
        )
        self.register_buffer(
            "mpl_tc_directions",
            tetrahedral,
        )

    def forward(
        self,
        tokens: torch.Tensor,
        modality_names: tuple[str, ...],
        modality_weights: torch.Tensor,
    ) -> ModalityAxisState:
        require_finite_tensor(
            tokens,
            "modality-axis input tokens",
        )
        require_finite_tensor(
            modality_weights,
            "modality-axis weights",
        )
        if tokens.ndim != 3 or tokens.shape[-1] != self.input_dim:
            raise AIObstructionError(
                "axis tokens must have shape "
                f"[batch, modalities, {self.input_dim}]"
            )
        batch, modality_count, _ = tokens.shape
        if modality_count < 2 or len(modality_names) != modality_count:
            raise AIObstructionError(
                "axis network requires one unique name per modality"
            )
        if len(set(modality_names)) != modality_count:
            raise AIObstructionError(
                "modality-axis names must be unique"
            )
        if modality_weights.shape != (batch, modality_count):
            raise AIObstructionError(
                "modality-axis weights have the wrong shape"
            )

        axes = require_finite_tensor(
            self.encoder(tokens),
            "encoded modality axes",
        )
        shared = axes[..., : self.shared_dim]
        private = axes[..., self.shared_dim :]
        normalized = functional.normalize(
            shared,
            dim=-1,
            eps=1e-8,
        )
        temperature = functional.softplus(self.log_temperature) + 1e-4
        similarity = torch.einsum(
            "bmd,bnd->bmn",
            normalized,
            normalized,
        ) / temperature
        adjacency = require_finite_tensor(
            torch.softmax(similarity, dim=-1),
            "modality-axis adjacency",
        )
        transported = self.forward_transport(axes)
        mapped = require_finite_tensor(
            torch.einsum(
                "bmn,bnd->bmd",
                adjacency,
                transported,
            ),
            "forward modality-axis transport",
        )
        reverse = adjacency.transpose(-1, -2)
        reverse = reverse / reverse.sum(
            dim=-1,
            keepdim=True,
        ).clamp_min(1e-8)
        reconstructed = require_finite_tensor(
            self.reverse_transport(
                torch.einsum(
                    "bmn,bnd->bmd",
                    reverse,
                    mapped,
                )
            ),
            "reverse modality-axis transport",
        )
        normalized_weights = modality_weights / modality_weights.sum(
            dim=-1,
            keepdim=True,
        ).clamp_min(1e-8)
        fused = require_finite_tensor(
            torch.sum(
                normalized_weights.unsqueeze(-1) * mapped,
                dim=1,
            ),
            "fused modality-axis state",
        )

        local_raw = torch.tanh(self.geometry_projection(mapped))
        local_coordinates = torch.stack(
            tuple(
                _local_geometry(
                    name,
                    local_raw[:, index, :],
                )
                for index, name in enumerate(modality_names)
            ),
            dim=1,
        )
        frames = torch.stack(
            tuple(
                _frame_for(
                    name,
                    dtype=mapped.dtype,
                    device=mapped.device,
                )
                for name in modality_names
            ),
            dim=0,
        )
        coordinates = require_finite_tensor(
            torch.einsum(
                "mij,bmj->bmi",
                frames,
                local_coordinates,
            ),
            "modality 3D coordinates",
        )
        dual_coordinates = require_finite_tensor(
            -coordinates,
            "modality antipodal dual coordinates",
        )
        observer_horizon = require_finite_tensor(
            1.0
            - torch.linalg.vector_norm(
                coordinates,
                dim=-1,
            ),
            "modality observer horizon",
        )
        stream_weights = require_finite_tensor(
            torch.softmax(mapped[..., :4], dim=-1),
            "MPL-TC stream weights",
        )
        directions = self.mpl_tc_directions.to(
            dtype=mapped.dtype,
            device=mapped.device,
        )
        rotated_directions = torch.einsum(
            "mij,sj->msi",
            frames,
            directions,
        )
        growth_vectors = require_finite_tensor(
            torch.einsum(
                "bms,msi->bmi",
                stream_weights,
                rotated_directions,
            ),
            "MPL-TC modality growth vectors",
        )

        identity = torch.eye(
            modality_count,
            dtype=tokens.dtype,
            device=tokens.device,
        )
        frame_identity = torch.eye(
            3,
            dtype=tokens.dtype,
            device=tokens.device,
        )
        cycle_matrix = torch.matmul(reverse, adjacency)
        residuals = {
            "axis_adjacency_normalization": torch.max(
                torch.abs(adjacency.sum(dim=-1) - 1.0)
            ),
            "axis_reverse_normalization": torch.max(
                torch.abs(reverse.sum(dim=-1) - 1.0)
            ),
            "axis_transport_cycle": torch.sqrt(
                torch.mean((reconstructed - axes) ** 2)
            ),
            "axis_cycle_identity": torch.sqrt(
                torch.mean(
                    (
                        cycle_matrix
                        - identity.unsqueeze(0)
                    )
                    ** 2
                )
            ),
            "axis_shared_alignment": torch.sqrt(
                torch.mean(
                    (
                        mapped[..., : self.shared_dim]
                        - shared
                    )
                    ** 2
                )
            ),
            "geometry_dual_involution": torch.max(
                torch.abs(dual_coordinates + coordinates)
            ),
            "geometry_frame_orthogonality": torch.max(
                torch.abs(
                    torch.matmul(
                        frames.transpose(-1, -2),
                        frames,
                    )
                    - frame_identity.unsqueeze(0)
                )
            ),
            "mpl_tc_stream_normalization": torch.max(
                torch.abs(stream_weights.sum(dim=-1) - 1.0)
            ),
            "mpl_tc_growth_bound": torch.max(
                torch.relu(
                    torch.linalg.vector_norm(
                        growth_vectors,
                        dim=-1,
                    )
                    - 1.0
                )
            ),
        }
        for name, residual in residuals.items():
            require_finite_tensor(residual, name)
        return ModalityAxisState(
            modality_names=modality_names,
            axis_latents=axes,
            shared_latents=shared,
            private_latents=private,
            mapped_axes=mapped,
            adjacency=adjacency,
            reverse_adjacency=reverse,
            reconstructed_axes=reconstructed,
            fused_axis=fused,
            geometric_coordinates=coordinates,
            dual_coordinates=dual_coordinates,
            modality_frames=frames,
            observer_horizon=observer_horizon,
            mpl_tc_stream_weights=stream_weights,
            mpl_tc_growth_vectors=growth_vectors,
            residuals=residuals,
        )
