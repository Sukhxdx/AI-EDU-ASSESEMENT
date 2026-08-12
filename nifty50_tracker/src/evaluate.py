"""Evaluation helpers and figure writers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .metrics import cumulative_returns, portfolio_returns, summarize_tracking


def evaluate_weight_vector(
    name: str,
    weights: np.ndarray,
    stock_rets: pd.DataFrame,
    index_rets: pd.Series,
) -> Dict[str, float]:
    port = portfolio_returns(stock_rets, weights)
    n_hold = int(np.sum(weights > 1e-8))
    stats = summarize_tracking(port, index_rets, n_holdings=n_hold)
    stats["method"] = name
    return stats


def evaluate_methods(
    methods: Dict[str, np.ndarray],
    stock_rets: pd.DataFrame,
    index_rets: pd.Series,
) -> pd.DataFrame:
    rows = []
    for name, w in methods.items():
        rows.append(evaluate_weight_vector(name, w, stock_rets, index_rets))
    df = pd.DataFrame(rows)
    # Keep method first
    cols = ["method"] + [c for c in df.columns if c != "method"]
    return df[cols].sort_values("tracking_error_ann")


def save_weights_table(
    weights: np.ndarray,
    asset_names: List[str],
    path: Path,
    soft_weights: np.ndarray | None = None,
) -> pd.DataFrame:
    rows = []
    for i, name in enumerate(asset_names):
        if weights[i] <= 1e-10 and (soft_weights is None or soft_weights[i] <= 1e-10):
            continue
        rows.append(
            {
                "ticker": name,
                "hard_weight": float(weights[i]),
                "soft_weight": float(soft_weights[i]) if soft_weights is not None else np.nan,
            }
        )
    df = pd.DataFrame(rows).sort_values("hard_weight", ascending=False)
    df.to_csv(path, index=False)
    return df


def plot_cumulative(
    methods: Dict[str, np.ndarray],
    stock_rets: pd.DataFrame,
    index_rets: pd.Series,
    out_path: Path,
    title: str,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(12, 6))
    cum_index = cumulative_returns(index_rets)
    ax.plot(cum_index.index, cum_index.values, label="Nifty 50 / Index", linewidth=2.5, color="#1f2937")

    palette = sns.color_palette("deep", n_colors=max(len(methods), 3))
    for (name, w), color in zip(methods.items(), palette):
        port = portfolio_returns(stock_rets, w)
        cum = cumulative_returns(port)
        ax.plot(cum.index, cum.values, label=name, linewidth=1.8, color=color)

    ax.set_title(title)
    ax.set_ylabel("Cumulative return")
    ax.set_xlabel("")
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_active_returns(
    weights: np.ndarray,
    stock_rets: pd.DataFrame,
    index_rets: pd.Series,
    out_path: Path,
    title: str,
) -> None:
    port = portfolio_returns(stock_rets, weights)
    active = (port - index_rets).dropna()
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    axes[0].plot(active.index, active.values, color="#0f766e", linewidth=1.0)
    axes[0].axhline(0.0, color="#111827", linewidth=1.0)
    axes[0].set_title(title)
    axes[0].set_ylabel("Active daily return")

    cum_active = active.cumsum()
    axes[1].plot(cum_active.index, cum_active.values, color="#b45309", linewidth=1.6)
    axes[1].axhline(0.0, color="#111827", linewidth=1.0)
    axes[1].set_ylabel("Cumulative active return")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_training_curve(history: List[Dict[str, float]], out_path: Path) -> None:
    df = pd.DataFrame(history)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["epoch"], df["total"], label="total", linewidth=2)
    ax.plot(df["epoch"], df["recon"], label="recon", linewidth=1.5)
    ax.plot(df["epoch"], df["track"], label="track", linewidth=1.5)
    if "conc" in df.columns:
        ax.plot(df["epoch"], df["conc"], label="conc", linewidth=1.2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("ICSAE training losses")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_te_bars(summary_df: pd.DataFrame, out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    order = summary_df.sort_values("tracking_error_ann")
    ax.barh(order["method"], order["tracking_error_ann"], color="#334155")
    ax.set_xlabel("Annualized tracking error")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def write_json(obj: dict, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str))
