"""Experiment defaults for Nifty 50 sparse index tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# Fixed Yahoo NSE symbols approximating a recent Nifty 50 basket.
# TATAMOTORS trades as TMPV on Yahoo after the rename; LTIM omitted (no quote).
NIFTY50_TICKERS: List[str] = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "BHARTIARTL.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "SBIN.NS",
    "ITC.NS",
    "HINDUNILVR.NS",
    "LT.NS",
    "BAJFINANCE.NS",
    "HCLTECH.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "AXISBANK.NS",
    "TITAN.NS",
    "ASIANPAINT.NS",
    "ULTRACEMCO.NS",
    "NTPC.NS",
    "BAJAJFINSV.NS",
    "WIPRO.NS",
    "ONGC.NS",
    "NESTLEIND.NS",
    "POWERGRID.NS",
    "M&M.NS",
    "KOTAKBANK.NS",
    "TMPV.NS",
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "COALINDIA.NS",
    "TATASTEEL.NS",
    "JSWSTEEL.NS",
    "TECHM.NS",
    "CIPLA.NS",
    "GRASIM.NS",
    "HDFCLIFE.NS",
    "SBILIFE.NS",
    "BRITANNIA.NS",
    "BPCL.NS",
    "HEROMOTOCO.NS",
    "EICHERMOT.NS",
    "DRREDDY.NS",
    "DIVISLAB.NS",
    "APOLLOHOSP.NS",
    "INDUSINDBK.NS",
    "BAJAJ-AUTO.NS",
    "TATACONSUM.NS",
    "HINDALCO.NS",
    "BEL.NS",
    "TRENT.NS",
]

INDEX_TICKER = "^NSEI"


@dataclass
class ExperimentConfig:
    start_date: str = "2019-01-01"
    end_date: str = "2025-12-31"
    train_ratio: float = 0.70
    n_assets_select: int = 10
    latent_dim: int = 8
    hidden_dim: int = 32
    epochs: int = 400
    batch_size: int = 64
    learning_rate: float = 1e-3
    weight_decay: float = 1e-5
    # Loss weights — tracking dominates; mild equal-weight ridge + concentration cap
    lambda_recon: float = 0.5
    lambda_track: float = 25.0
    lambda_l2: float = 0.001
    lambda_conc: float = 2.0
    max_weight: float = 0.25
    refine_with_ls: bool = True
    min_history_frac: float = 0.85
    seed: int = 42
    use_synthetic_if_download_fails: bool = True
    results_dir: str = "results"
    data_dir: str = "data"
    tickers: List[str] = field(default_factory=lambda: list(NIFTY50_TICKERS))
    index_ticker: str = INDEX_TICKER
