"""Lightweight checks for metrics and sparsification helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from src.metrics import portfolio_returns, tracking_error
from src.model import IndexConstrainedSparseAE, extract_sparse_weights, refine_weights_projected_ls


def test_portfolio_and_te() -> None:
    idx = pd.bdate_range("2020-01-01", periods=100)
    stocks = pd.DataFrame(
        {
            "A": np.linspace(0.001, 0.002, 100),
            "B": np.linspace(-0.001, 0.001, 100),
        },
        index=idx,
    )
    weights = np.array([0.6, 0.4])
    port = portfolio_returns(stocks, weights)
    index = port + 0.0001
    te = tracking_error(port, index, annualize=True)
    assert te >= 0.0
    assert abs(port.iloc[0] - (0.6 * stocks["A"].iloc[0] + 0.4 * stocks["B"].iloc[0])) < 1e-12


def test_extract_sparse_weights() -> None:
    model = IndexConstrainedSparseAE(n_assets=5, latent_dim=2, hidden_dim=8)
    with torch.no_grad():
        model.selection_logits.copy_(torch.tensor([3.0, 2.0, 1.0, 0.0, -1.0]))
    hard, selected, soft = extract_sparse_weights(model, k=2, asset_names=list("ABCDE"))
    assert len(selected) == 2
    assert abs(hard.sum() - 1.0) < 1e-6
    assert np.sum(hard > 0) == 2
    assert soft.shape == (5,)


def test_refine_ls() -> None:
    rng = np.random.default_rng(0)
    r = rng.normal(0, 0.01, size=(200, 5))
    true_w = np.array([0.4, 0.3, 0.3, 0.0, 0.0])
    y = r @ true_w + rng.normal(0, 0.0005, size=200)
    est = refine_weights_projected_ls(r, y, np.array([0, 1, 2]))
    assert abs(est.sum() - 1.0) < 1e-6
    assert np.all(est >= -1e-10)
    assert np.sum(est > 0) == 3


if __name__ == "__main__":
    test_portfolio_and_te()
    test_extract_sparse_weights()
    test_refine_ls()
    print("ok")
