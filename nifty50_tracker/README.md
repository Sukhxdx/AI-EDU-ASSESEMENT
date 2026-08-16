# Nifty 50 Sparse Index Tracking (ICSAE)

Sparse replication of the Nifty 50 using an **Index-Constrained Sparse Autoencoder**.
The goal is a long-only portfolio of `k` stocks whose returns stay close to the
index, measured mainly by annualized tracking error.

## Why sparse tracking?

Holding all 50 names is not always practical (ticket size, rebalancing cost,
mandate constraints). A sparse tracker keeps a smaller basket and still tries to
match index returns. Classical approaches pick names by correlation / PCA and
then solve a quadratic tracking problem. This project adds a neural alternative
that learns selection and tracking in one training loop.

## Method in one paragraph

Daily returns of the constituent stocks go into a bottleneck autoencoder. A
learnable soft-selection vector (softmax over logits) forms a portfolio return
on every batch. The loss mixes reconstruction of the return cross-section,
squared tracking error vs the index, a light equal-weight ridge, and a penalty
on overly concentrated names. After training, the top-`k` names are chosen from
a blend of soft weights and encoder sensitivity; weights on that subset are
refined with projected least squares and scored out of sample against baselines.

## Setup

```bash
cd nifty50_tracker
pip install -r requirements.txt
python -m src.run_pipeline --k 10 --epochs 400
```

Useful flags:

```bash
python -m src.run_pipeline --k 15 --epochs 500
python -m src.run_pipeline --force-synthetic   # offline / CI path
python -m src.run_pipeline --start 2018-01-01 --end 2024-12-31
```

Market data is pulled with `yfinance` (`^NSEI` + NSE tickers). If the download
fails, the loader builds a factor-driven synthetic panel so the pipeline still
runs. Cached prices land in `data/`.

## Outputs (`results/`)

| File | Content |
|------|---------|
| `test_metrics.csv` | OOS tracking metrics for ICSAE and baselines |
| `train_metrics.csv` | In-sample metrics |
| `icsae_weights.csv` | Soft + hard portfolio weights |
| `oos_cumulative.png` | Cumulative return chart |
| `oos_te_bars.png` | Tracking-error comparison |
| `icsae_model.pt` | Trained model checkpoint |
| `run_summary.json` | Compact run metadata |

## Project layout

```
nifty50_tracker/
  src/
    config.py         # tickers + hyperparameters
    data_loader.py    # Yahoo / synthetic data
    model.py          # ICSAE network + loss
    train.py          # training loop
    baselines.py      # correlation, PCA, greedy, LS trackers
    metrics.py        # TE, R², drawdown, etc.
    evaluate.py       # tables + plots
    run_pipeline.py   # CLI entry point
  docs/METHODOLOGY.md
  results/            # created after a run
  data/               # price cache
```

## Baselines included

- Random `k` equal weight
- Lowest-volatility `k` equal weight
- Highest index-correlation `k` (equal and quadratic weights)
- PCA loading screen (equal and quadratic weights)
- Greedy forward selection with projected least squares
- Dense full-universe long-only least squares (reference upper bound)

## Metrics

Primary metric: **annualized tracking error**  
`TE = std(r_p - r_index) * sqrt(252)`

Also reported: daily MAD, R² vs index, correlation, active return, volatility,
and max drawdown.

## Notes / limits

- Constituent list is fixed for the sample (no corporate-action reconstitution
  calendar). That is a simplification versus a production index fund.
- Transaction costs and turnover are not modeled.
- Results depend on the train/test split and on whether real NSE data or the
  synthetic fallback was used; check `results/run_summary.json` → `meta.source`.

See [docs/METHODOLOGY.md](docs/METHODOLOGY.md) for the full write-up.
