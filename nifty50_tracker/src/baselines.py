"""Classical baselines for sparse Nifty 50 index tracking."""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


def _renormalize(w: np.ndarray) -> np.ndarray:
    w = np.clip(w, 0.0, None)
    s = w.sum()
    if s <= 0:
        w = np.ones_like(w) / len(w)
    else:
        w = w / s
    return w


def equal_weight_subset(n_assets: int, selected_idx: np.ndarray) -> np.ndarray:
    w = np.zeros(n_assets, dtype=float)
    w[selected_idx] = 1.0 / len(selected_idx)
    return w


def random_k_equal(n_assets: int, k: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    idx = rng.choice(n_assets, size=min(k, n_assets), replace=False)
    return equal_weight_subset(n_assets, idx)


def volatility_screen_equal(train_stock: pd.DataFrame, k: int) -> np.ndarray:
    """Pick k lowest-volatility names, equal weight (naive risk screen)."""
    vol = train_stock.std(ddof=1)
    idx = np.argsort(vol.values)[:k]
    return equal_weight_subset(train_stock.shape[1], idx)


def correlation_screen_equal(train_stock: pd.DataFrame, train_index: pd.Series, k: int) -> np.ndarray:
    """Pick k assets with highest correlation to the index, equal weight."""
    corr = train_stock.corrwith(train_index).fillna(0.0)
    idx = np.argsort(corr.values)[::-1][:k]
    return equal_weight_subset(train_stock.shape[1], idx)


def pca_factor_subset(train_stock: pd.DataFrame, k: int, n_components: int = 5) -> np.ndarray:
    """
    Rank assets by absolute loading on the leading PCA factors, then equal-weight
    the top-k names. A simple unsupervised sparse proxy.
    """
    x = train_stock.values
    x = (x - x.mean(axis=0)) / (x.std(axis=0) + 1e-8)
    n_components = min(n_components, x.shape[1], x.shape[0])
    pca = PCA(n_components=n_components)
    pca.fit(x)
    # Importance = sum of abs loadings weighted by explained variance ratio
    importance = np.abs(pca.components_).T @ pca.explained_variance_ratio_
    idx = np.argsort(importance)[::-1][:k]
    return equal_weight_subset(train_stock.shape[1], idx)


def quadratic_tracking_subset(
    train_stock: pd.DataFrame,
    train_index: pd.Series,
    selected_idx: np.ndarray,
) -> np.ndarray:
    """
    Solve a constrained least-squares tracker on a fixed subset:

        min_w ||R_s w - r_index||^2  s.t. w >= 0, 1'w = 1

    Uses projected gradient descent (no CVXPY dependency).
    """
    r = train_stock.values[:, selected_idx]
    y = train_index.values
    n = r.shape[1]
    w = np.ones(n) / n
    lr = 0.25
    for _ in range(2000):
        pred = r @ w
        grad = (2.0 / len(y)) * r.T @ (pred - y)
        w = w - lr * grad
        w = _renormalize(w)
    full = np.zeros(train_stock.shape[1], dtype=float)
    full[selected_idx] = w
    return full


def greedy_forward_selection(
    train_stock: pd.DataFrame,
    train_index: pd.Series,
    k: int,
) -> np.ndarray:
    """
    Greedy forward selection minimizing in-sample tracking MSE, with
    non-negative least-squares-ish weights via regression + projection.
    """
    n = train_stock.shape[1]
    selected: List[int] = []
    remaining = set(range(n))
    y = train_index.values

    for _ in range(min(k, n)):
        best_j = None
        best_mse = float("inf")
        best_w_sub = None
        for j in list(remaining):
            trial = selected + [j]
            x = train_stock.values[:, trial]
            # Unconstrained LS then project to simplex
            beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
            beta = _renormalize(beta)
            mse = float(np.mean((x @ beta - y) ** 2))
            if mse < best_mse:
                best_mse = mse
                best_j = j
                best_w_sub = beta
        selected.append(best_j)
        remaining.remove(best_j)

    full = np.zeros(n, dtype=float)
    full[np.array(selected)] = best_w_sub
    return full


def full_universe_ls(
    train_stock: pd.DataFrame,
    train_index: pd.Series,
) -> np.ndarray:
    """Dense long-only tracker fit by projected LS on all assets (upper bound)."""
    x = train_stock.values
    y = train_index.values
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return _renormalize(beta)


def baseline_suite(
    train_stock: pd.DataFrame,
    train_index: pd.Series,
    k: int,
    seed: int,
) -> dict:
    corr_w = correlation_screen_equal(train_stock, train_index, k)
    corr_idx = np.flatnonzero(corr_w > 0)
    pca_w = pca_factor_subset(train_stock, k)
    pca_idx = np.flatnonzero(pca_w > 0)

    return {
        "random_equal": random_k_equal(train_stock.shape[1], k, seed),
        "low_vol_equal": volatility_screen_equal(train_stock, k),
        "high_corr_equal": corr_w,
        "high_corr_quad": quadratic_tracking_subset(train_stock, train_index, corr_idx),
        "pca_equal": pca_w,
        "pca_quad": quadratic_tracking_subset(train_stock, train_index, pca_idx),
        "greedy_forward": greedy_forward_selection(train_stock, train_index, k),
        "full_universe_ls": full_universe_ls(train_stock, train_index),
    }
