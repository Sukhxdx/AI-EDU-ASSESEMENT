"""Training loop for the Index-Constrained Sparse Autoencoder."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset

from .config import ExperimentConfig
from .model import (
    IndexConstrainedSparseAE,
    extract_sparse_weights,
    icsae_loss,
    refine_weights_projected_ls,
)


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _temperature_schedule(epoch: int, total_epochs: int) -> float:
    # Mild annealing; keep softmax from becoming a one-hot too early
    start_t, end_t = 1.2, 0.85
    frac = epoch / max(total_epochs - 1, 1)
    return start_t + (end_t - start_t) * frac


def train_icsae(
    train_stock: pd.DataFrame,
    train_index: pd.Series,
    cfg: ExperimentConfig,
    device: str | None = None,
) -> Tuple[IndexConstrainedSparseAE, List[Dict[str, float]], np.ndarray, List[str], np.ndarray]:
    set_seed(cfg.seed)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    x = torch.tensor(train_stock.values, dtype=torch.float32)
    y = torch.tensor(train_index.values, dtype=torch.float32)
    dataset = TensorDataset(x, y)
    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True, drop_last=False)

    model = IndexConstrainedSparseAE(
        n_assets=train_stock.shape[1],
        latent_dim=cfg.latent_dim,
        hidden_dim=cfg.hidden_dim,
    ).to(device)

    opt = torch.optim.Adam(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )

    history: List[Dict[str, float]] = []
    model.train()
    for epoch in range(cfg.epochs):
        temp = _temperature_schedule(epoch, cfg.epochs)
        bucket = {"total": 0.0, "recon": 0.0, "track": 0.0, "l2": 0.0, "conc": 0.0}
        n_seen = 0
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            recon, port_ret, weights = model(xb, temperature=temp)
            loss, parts = icsae_loss(
                xb,
                yb,
                recon,
                port_ret,
                weights,
                lambda_recon=cfg.lambda_recon,
                lambda_track=cfg.lambda_track,
                lambda_l2=cfg.lambda_l2,
                lambda_conc=cfg.lambda_conc,
                max_weight=cfg.max_weight,
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            bs = xb.shape[0]
            n_seen += bs
            for key in bucket:
                bucket[key] += parts[key] * bs
        epoch_row = {k: v / max(n_seen, 1) for k, v in bucket.items()}
        epoch_row["epoch"] = float(epoch + 1)
        epoch_row["temperature"] = float(temp)
        history.append(epoch_row)
        if (epoch + 1) % 50 == 0 or epoch == 0:
            print(
                f"epoch {epoch+1:4d}/{cfg.epochs}  "
                f"loss={epoch_row['total']:.6f}  "
                f"recon={epoch_row['recon']:.6f}  "
                f"track={epoch_row['track']:.6f}  "
                f"T={temp:.2f}"
            )

    soft_hard, selected, soft_w = extract_sparse_weights(
        model, k=cfg.n_assets_select, asset_names=list(train_stock.columns)
    )
    selected_idx = np.flatnonzero(soft_hard > 0)

    if cfg.refine_with_ls:
        hard_w = refine_weights_projected_ls(
            train_stock.values,
            train_index.values,
            selected_idx,
        )
    else:
        hard_w = soft_hard

    return model, history, hard_w, selected, soft_w
