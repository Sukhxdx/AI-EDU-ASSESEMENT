"""Tracking-error and portfolio performance metrics."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def portfolio_returns(stock_rets: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    w = np.asarray(weights, dtype=float)
    if w.ndim != 1 or len(w) != stock_rets.shape[1]:
        raise ValueError("weights must be 1-D and match number of assets")
    return pd.Series(stock_rets.values @ w, index=stock_rets.index, name="portfolio")


def tracking_error(port_rets: pd.Series, index_rets: pd.Series, annualize: bool = True) -> float:
    """Annualized std of active returns (portfolio - index)."""
    active = (port_rets - index_rets).dropna()
    te = float(active.std(ddof=1))
    if annualize:
        te *= np.sqrt(TRADING_DAYS)
    return te


def mean_absolute_tracking_diff(port_rets: pd.Series, index_rets: pd.Series) -> float:
    return float((port_rets - index_rets).abs().mean())


def r_squared(port_rets: pd.Series, index_rets: pd.Series) -> float:
    aligned = pd.concat([port_rets, index_rets], axis=1).dropna()
    if aligned.empty:
        return float("nan")
    y = aligned.iloc[:, 0].values
    x = aligned.iloc[:, 1].values
    ss_res = np.sum((y - x) ** 2)
    ss_tot = np.sum((x - x.mean()) ** 2)
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def cumulative_returns(rets: pd.Series) -> pd.Series:
    return (1.0 + rets.fillna(0.0)).cumprod() - 1.0


def max_drawdown(rets: pd.Series) -> float:
    wealth = (1.0 + rets.fillna(0.0)).cumprod()
    peak = wealth.cummax()
    dd = wealth / peak - 1.0
    return float(dd.min())


def summarize_tracking(
    port_rets: pd.Series,
    index_rets: pd.Series,
    n_holdings: int,
) -> Dict[str, float]:
    active = (port_rets - index_rets).dropna()
    return {
        "n_holdings": float(n_holdings),
        "tracking_error_ann": tracking_error(port_rets, index_rets, annualize=True),
        "mad_daily": mean_absolute_tracking_diff(port_rets, index_rets),
        "r_squared": r_squared(port_rets, index_rets),
        "corr": float(port_rets.corr(index_rets)),
        "active_return_ann": float(active.mean() * TRADING_DAYS),
        "port_vol_ann": float(port_rets.std(ddof=1) * np.sqrt(TRADING_DAYS)),
        "index_vol_ann": float(index_rets.std(ddof=1) * np.sqrt(TRADING_DAYS)),
        "port_max_drawdown": max_drawdown(port_rets),
        "index_max_drawdown": max_drawdown(index_rets),
    }
