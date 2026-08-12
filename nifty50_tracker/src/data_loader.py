"""Download and prepare Nifty 50 / NSEI returns for index tracking."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .config import ExperimentConfig


def _try_yfinance_download(
    tickers: List[str],
    index_ticker: str,
    start: str,
    end: str,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
    try:
        import yfinance as yf
    except ImportError:
        return None, None

    all_symbols = tickers + [index_ticker]
    raw = yf.download(
        all_symbols,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="ticker",
    )
    if raw is None or raw.empty:
        return None, None

    closes: Dict[str, pd.Series] = {}
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = set(raw.columns.get_level_values(0))
        if "Close" in level0 or "Adj Close" in level0:
            price_field = "Close" if "Close" in level0 else "Adj Close"
            for t in all_symbols:
                try:
                    series = raw[price_field][t].dropna()
                    if not series.empty:
                        closes[t] = series
                except Exception:
                    continue
        else:
            for t in all_symbols:
                try:
                    if t not in raw.columns.get_level_values(0):
                        continue
                    sub = raw[t]
                    col = "Close" if "Close" in sub.columns else "Adj Close"
                    series = sub[col].dropna()
                    if not series.empty:
                        closes[t] = series
                except Exception:
                    continue
    else:
        col = "Close" if "Close" in raw.columns else "Adj Close"
        closes[all_symbols[0]] = raw[col].dropna()

    if index_ticker not in closes:
        return None, None

    index_px = closes[index_ticker].sort_index()
    stock_frames = {t: closes[t].sort_index() for t in tickers if t in closes}
    if len(stock_frames) < 15:
        return None, None

    # Align each stock to the index calendar without forcing the shortest IPO
    # date on the whole panel. Drop names that miss too much of the index span.
    panel = pd.DataFrame(index=index_px.index)
    for t, s in stock_frames.items():
        panel[t] = s.reindex(index_px.index)
    coverage = panel.notna().mean()
    keep = coverage[coverage >= 0.85].index.tolist()
    if len(keep) < 15:
        keep = coverage.sort_values(ascending=False).head(40).index.tolist()
    panel = panel[keep]
    # Require contiguous coverage after the first valid date per column is filled
    panel = panel.dropna(how="any")
    if len(panel) < 250:
        return None, None

    index_aligned = index_px.reindex(panel.index).dropna()
    panel = panel.loc[index_aligned.index]
    return panel, index_aligned


def _synthetic_nifty_panel(
    n_assets: int,
    n_days: int,
    seed: int,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Factor-driven synthetic equity panel.

    Index return is a positive-weight mix of asset returns plus a small residual.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-01", periods=n_days)

    factors = rng.normal(0.0, 0.008, size=(n_days, 3))
    betas = rng.normal(0.0, 1.0, size=(n_assets, 3))
    betas[:, 0] = np.abs(betas[:, 0]) + 0.4
    idio = rng.normal(0.0, 0.012, size=(n_days, n_assets))
    asset_rets = factors @ betas.T + idio

    raw_w = rng.random(n_assets) + 0.05
    caps = raw_w / raw_w.sum()
    index_rets = asset_rets @ caps + rng.normal(0.0, 0.001, size=n_days)

    tickers = [f"SYN{i:02d}.NS" for i in range(n_assets)]
    stock_px = 100.0 * np.cumprod(1.0 + asset_rets, axis=0)
    index_px = 100.0 * np.cumprod(1.0 + index_rets)

    prices = pd.DataFrame(stock_px, index=dates, columns=tickers)
    index = pd.Series(index_px, index=dates, name="SYN_NIFTY")
    return prices, index


def prices_to_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="any")


def load_market_data(
    cfg: ExperimentConfig,
) -> Tuple[pd.DataFrame, pd.Series, dict]:
    """
    Returns aligned stock returns, index returns, and metadata.
    Caches downloaded prices under cfg.data_dir.
    """
    data_dir = Path(cfg.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    meta: dict = {"source": None, "n_assets": 0, "n_days": 0}

    cache_stocks = data_dir / "stock_prices.csv"
    cache_index = data_dir / "index_prices.csv"
    cache_meta = data_dir / "meta.json"

    stock_prices: Optional[pd.DataFrame] = None
    index_prices: Optional[pd.Series] = None

    if cache_stocks.exists() and cache_index.exists():
        stock_prices = pd.read_csv(cache_stocks, index_col=0, parse_dates=True)
        index_prices = pd.read_csv(cache_index, index_col=0, parse_dates=True).iloc[:, 0]
        meta = json.loads(cache_meta.read_text()) if cache_meta.exists() else {"source": "cache"}
    else:
        stock_prices, index_prices = _try_yfinance_download(
            cfg.tickers, cfg.index_ticker, cfg.start_date, cfg.end_date
        )
        if stock_prices is not None:
            meta = {
                "source": "yfinance",
                "index_ticker": cfg.index_ticker,
                "tickers": list(stock_prices.columns),
            }
            stock_prices.to_csv(cache_stocks)
            index_prices.to_csv(cache_index, header=True)
            cache_meta.write_text(json.dumps(meta, indent=2))
        elif cfg.use_synthetic_if_download_fails:
            stock_prices, index_prices = _synthetic_nifty_panel(
                n_assets=min(50, len(cfg.tickers)),
                n_days=1500,
                seed=cfg.seed,
            )
            meta = {
                "source": "synthetic",
                "note": "Yahoo download failed or returned incomplete data; synthetic panel used.",
                "tickers": list(stock_prices.columns),
            }
            stock_prices.to_csv(cache_stocks)
            index_prices.to_csv(cache_index, header=True)
            cache_meta.write_text(json.dumps(meta, indent=2))
        else:
            raise RuntimeError("Failed to download market data and synthetic fallback disabled.")

    common_idx = stock_prices.index.intersection(index_prices.index)
    stock_prices = stock_prices.loc[common_idx].sort_index()
    index_prices = index_prices.loc[common_idx].sort_index()

    miss_frac = stock_prices.isna().mean()
    keep = miss_frac[miss_frac <= (1.0 - cfg.min_history_frac)].index.tolist()
    if len(keep) < 15:
        keep = miss_frac.sort_values().head(40).index.tolist()
    stock_prices = stock_prices[keep].ffill().bfill()
    index_prices = index_prices.ffill().bfill()

    # Drop residual incomplete rows
    mask = stock_prices.notna().all(axis=1) & index_prices.notna()
    stock_prices = stock_prices.loc[mask]
    index_prices = index_prices.loc[mask]

    stock_rets = prices_to_returns(stock_prices)
    index_rets = prices_to_returns(index_prices.to_frame("index"))["index"]
    aligned = stock_rets.join(index_rets, how="inner").dropna(how="any")
    stock_rets = aligned[stock_rets.columns]
    index_rets = aligned["index"]

    meta["n_assets"] = int(stock_rets.shape[1])
    meta["n_days"] = int(stock_rets.shape[0])
    meta["start"] = str(stock_rets.index.min().date())
    meta["end"] = str(stock_rets.index.max().date())
    return stock_rets, index_rets, meta


def train_test_split_returns(
    stock_rets: pd.DataFrame,
    index_rets: pd.Series,
    train_ratio: float,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    n = len(stock_rets)
    cut = int(n * train_ratio)
    cut = max(cut, 60)
    cut = min(cut, n - 60)
    return (
        stock_rets.iloc[:cut],
        index_rets.iloc[:cut],
        stock_rets.iloc[cut:],
        index_rets.iloc[cut:],
    )
