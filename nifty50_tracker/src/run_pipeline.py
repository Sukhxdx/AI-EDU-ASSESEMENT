#!/usr/bin/env python3
"""End-to-end Nifty 50 sparse index tracking pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Allow `python -m src.run_pipeline` and `python src/run_pipeline.py`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.baselines import baseline_suite
from src.config import ExperimentConfig
from src.data_loader import load_market_data, train_test_split_returns
from src.evaluate import (
    evaluate_methods,
    plot_active_returns,
    plot_cumulative,
    plot_te_bars,
    plot_training_curve,
    save_weights_table,
    write_json,
)
from src.train import train_icsae


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Nifty 50 ICSAE index tracking")
    p.add_argument("--start", default="2019-01-01")
    p.add_argument("--end", default="2025-12-31")
    p.add_argument("--k", type=int, default=10, help="number of stocks in sparse portfolio")
    p.add_argument("--epochs", type=int, default=400)
    p.add_argument("--latent-dim", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--results-dir", default="results")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--force-synthetic", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig(
        start_date=args.start,
        end_date=args.end,
        n_assets_select=args.k,
        epochs=args.epochs,
        latent_dim=args.latent_dim,
        seed=args.seed,
        results_dir=args.results_dir,
        data_dir=args.data_dir,
    )

    results_dir = Path(cfg.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    print("Loading market data...")
    if args.force_synthetic:
        # Clear cache so synthetic path is used after forced failure path.
        for name in ("stock_prices.csv", "index_prices.csv", "meta.json"):
            path = Path(cfg.data_dir) / name
            if path.exists():
                path.unlink()
        # Monkey-patch: temporarily empty tickers download by using synthetic only
        from src import data_loader as dl

        def _fail(*_a, **_k):
            return None, None

        dl._try_yfinance_download = _fail  # type: ignore

    stock_rets, index_rets, meta = load_market_data(cfg)
    print(json.dumps(meta, indent=2))

    train_s, train_i, test_s, test_i = train_test_split_returns(
        stock_rets, index_rets, cfg.train_ratio
    )
    print(f"Train days={len(train_s)}  Test days={len(test_s)}  Assets={train_s.shape[1]}")

    print("\nTraining Index-Constrained Sparse Autoencoder...")
    model, history, hard_w, selected, soft_w = train_icsae(train_s, train_i, cfg)

    print("Selected holdings:")
    for t, w in sorted(
        ((train_s.columns[i], hard_w[i]) for i in range(len(hard_w)) if hard_w[i] > 0),
        key=lambda z: -z[1],
    ):
        print(f"  {t:18s}  {w:.4f}")

    print("\nFitting baselines...")
    baselines = baseline_suite(train_s, train_i, k=cfg.n_assets_select, seed=cfg.seed)
    methods = {"icsae_sparse": hard_w, **baselines}

    print("Evaluating in-sample / out-of-sample...")
    train_summary = evaluate_methods(methods, train_s, train_i)
    test_summary = evaluate_methods(methods, test_s, test_i)
    train_summary.to_csv(results_dir / "train_metrics.csv", index=False)
    test_summary.to_csv(results_dir / "test_metrics.csv", index=False)
    print("\nOut-of-sample tracking error ranking:")
    print(test_summary[["method", "n_holdings", "tracking_error_ann", "r_squared", "corr"]].to_string(index=False))

    save_weights_table(
        hard_w,
        list(train_s.columns),
        results_dir / "icsae_weights.csv",
        soft_weights=soft_w,
    )
    pd.DataFrame(history).to_csv(results_dir / "training_history.csv", index=False)

    # Focus plots on ICSAE vs strongest sparse baselines
    plot_methods = {
        "ICSAE (k={})".format(cfg.n_assets_select): hard_w,
        "Greedy forward": baselines["greedy_forward"],
        "High-corr + quad": baselines["high_corr_quad"],
        "PCA + quad": baselines["pca_quad"],
    }
    plot_cumulative(
        plot_methods,
        test_s,
        test_i,
        results_dir / "oos_cumulative.png",
        title="Out-of-sample cumulative returns vs index",
    )
    plot_active_returns(
        hard_w,
        test_s,
        test_i,
        results_dir / "oos_active.png",
        title="ICSAE out-of-sample active returns",
    )
    plot_training_curve(history, results_dir / "training_curve.png")
    plot_te_bars(
        test_summary[test_summary["method"] != "full_universe_ls"],
        results_dir / "oos_te_bars.png",
        title="Out-of-sample annualized tracking error",
    )

    # Persist model state for later inspection
    torch.save(
        {
            "state_dict": model.state_dict(),
            "asset_names": list(train_s.columns),
            "config": cfg.__dict__,
            "selected": selected,
            "hard_weights": hard_w,
        },
        results_dir / "icsae_model.pt",
    )

    report = {
        "meta": meta,
        "config": {k: v for k, v in cfg.__dict__.items() if k != "tickers"},
        "selected_holdings": selected,
        "train_best_te": float(train_summary.iloc[0]["tracking_error_ann"]),
        "test_icsae_te": float(
            test_summary.loc[test_summary["method"] == "icsae_sparse", "tracking_error_ann"].iloc[0]
        ),
        "test_best_method": str(test_summary.iloc[0]["method"]),
        "test_best_te": float(test_summary.iloc[0]["tracking_error_ann"]),
    }
    write_json(report, results_dir / "run_summary.json")
    print(f"\nArtifacts written to {results_dir.resolve()}")


if __name__ == "__main__":
    main()
