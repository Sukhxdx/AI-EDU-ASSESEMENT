"""Index-Constrained Sparse Autoencoder (ICSAE) for sparse index tracking.

Training uses a soft long-only portfolio (softmax over logits) together with a
return autoencoder. After training, the top-k names by soft weight are kept and
their weights can be refined by a projected tracking least-squares step.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class IndexConstrainedSparseAE(nn.Module):
    def __init__(
        self,
        n_assets: int,
        latent_dim: int = 8,
        hidden_dim: int = 32,
    ) -> None:
        super().__init__()
        self.n_assets = n_assets
        self.latent_dim = latent_dim

        # Soft portfolio logits -> simplex weights via softmax
        self.selection_logits = nn.Parameter(torch.zeros(n_assets))

        self.encoder = nn.Sequential(
            nn.Linear(n_assets, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, latent_dim),
            nn.Tanh(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, n_assets),
        )

        self._init_weights()

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
        with torch.no_grad():
            # Near-equal start; small noise breaks symmetry
            self.selection_logits.normal_(mean=0.0, std=0.02)

    def portfolio_weights(self, temperature: float = 1.0) -> torch.Tensor:
        return F.softmax(self.selection_logits / max(temperature, 1e-6), dim=0)

    def forward(
        self,
        x: torch.Tensor,
        temperature: float = 1.0,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Parameters
        ----------
        x : (batch, n_assets) stock returns

        Returns
        -------
        recon, port_ret, weights
        """
        weights = self.portfolio_weights(temperature=temperature)
        # Soft gating: down-weight names the portfolio ignores, without hard zeros
        gated = x * (0.25 + 0.75 * weights / (weights.mean() + 1e-8)).unsqueeze(0)
        z = self.encoder(gated)
        recon = self.decoder(z)
        port_ret = (x * weights.unsqueeze(0)).sum(dim=1)
        return recon, port_ret, weights

    @torch.no_grad()
    def encoder_input_importance(self) -> np.ndarray:
        """L1 column norms of the first encoder layer (asset -> hidden)."""
        first = self.encoder[0]
        assert isinstance(first, nn.Linear)
        w = first.weight.detach().cpu().numpy()  # (hidden, n_assets)
        return np.abs(w).sum(axis=0)


def icsae_loss(
    x: torch.Tensor,
    index_ret: torch.Tensor,
    recon: torch.Tensor,
    port_ret: torch.Tensor,
    weights: torch.Tensor,
    lambda_recon: float,
    lambda_track: float,
    lambda_l2: float,
    lambda_conc: float,
    max_weight: float,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    recon_loss = F.mse_loss(recon, x)
    track_loss = F.mse_loss(port_ret, index_ret)
    # Mild ridge on weights around equal weight (keeps optimization stable)
    eq = torch.full_like(weights, 1.0 / weights.numel())
    l2 = F.mse_loss(weights, eq)
    # Penalize single-name concentration above max_weight
    conc = torch.relu(weights - max_weight).pow(2).sum()
    total = (
        lambda_recon * recon_loss
        + lambda_track * track_loss
        + lambda_l2 * l2
        + lambda_conc * conc
    )
    parts = {
        "total": float(total.detach().cpu()),
        "recon": float(recon_loss.detach().cpu()),
        "track": float(track_loss.detach().cpu()),
        "l2": float(l2.detach().cpu()),
        "conc": float(conc.detach().cpu()),
    }
    return total, parts


@torch.no_grad()
def extract_sparse_weights(
    model: IndexConstrainedSparseAE,
    k: int,
    asset_names: Optional[List[str]] = None,
    importance: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, List[str], np.ndarray]:
    """
    Keep top-k names by blended importance (soft weight + encoder sensitivity),
    zero the rest, renormalize soft mass on the kept set.
    """
    model.eval()
    soft = model.portfolio_weights(temperature=1.0).detach().cpu().numpy()
    enc = model.encoder_input_importance()
    enc = enc / (enc.sum() + 1e-12)
    if importance is None:
        # Blend portfolio preference with factor loading strength
        score = 0.7 * soft + 0.3 * enc
    else:
        score = importance
    k = int(min(max(k, 1), len(soft)))
    idx = np.argsort(score)[::-1][:k]
    hard = np.zeros_like(soft)
    hard[idx] = soft[idx]
    if hard.sum() <= 0:
        hard[idx] = 1.0
    hard = hard / hard.sum()
    names = asset_names if asset_names is not None else [str(i) for i in range(len(soft))]
    selected = [names[i] for i in idx]
    return hard, selected, soft


def refine_weights_projected_ls(
    train_stock: np.ndarray,
    train_index: np.ndarray,
    selected_idx: np.ndarray,
    steps: int = 2500,
    lr: float = 0.2,
) -> np.ndarray:
    """Non-negative, sum-to-one LS tracker on a fixed subset."""
    r = train_stock[:, selected_idx]
    y = train_index
    n = r.shape[1]
    w = np.ones(n) / n
    for _ in range(steps):
        pred = r @ w
        grad = (2.0 / len(y)) * r.T @ (pred - y)
        w = w - lr * grad
        w = np.clip(w, 0.0, None)
        s = w.sum()
        w = (np.ones(n) / n) if s <= 0 else (w / s)
    full = np.zeros(train_stock.shape[1], dtype=float)
    full[selected_idx] = w
    return full
