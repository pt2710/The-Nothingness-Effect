"""Typed QENN and PGQENN subnetwork ensembles."""

from __future__ import annotations

import torch
from torch import nn

from the_nothingness_effect.artificial_intelligence.pgqenn.model import PGQENNModel, PGQENNOutput
from the_nothingness_effect.artificial_intelligence.qenn.model import QENNModel, QENNOutput


class SubnetworkEnsemble(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, *, qenn_count: int = 2, pgqenn_count: int = 2, K_D: float = 1.0):
        super().__init__()
        if qenn_count < 1 or pgqenn_count < 1:
            raise ValueError("SOInets requires at least one QENN and one PGQENN subnetwork")
        self.qenn = nn.ModuleList(QENNModel(input_dim, hidden_dim, output_dim, K_D=K_D) for _ in range(qenn_count))
        self.pgqenn = nn.ModuleList(PGQENNModel(input_dim, hidden_dim, output_dim, K_D=K_D) for _ in range(pgqenn_count))

    def forward(self, qenn_features: torch.Tensor, pgqenn_features: torch.Tensor) -> tuple[list[QENNOutput], list[PGQENNOutput]]:
        return (
            [model(qenn_features) for model in self.qenn],
            [model(pgqenn_features) for model in self.pgqenn],
        )
