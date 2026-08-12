# Methodology: Sparse Nifty 50 Tracking with ICSAE

## 1. Problem

Let \(R_t \in \mathbb{R}^N\) be the vector of daily simple returns for \(N\)
Nifty-related equities on day \(t\), and let \(r_t\) be the Nifty 50 index
return. A sparse long-only tracker chooses a weight vector \(w \in \mathbb{R}^N\)
with at most \(k\) positive entries, \(w \ge 0\), \(\mathbf{1}^\top w = 1\), that
keeps the active return \(w^\top R_t - r_t\) small.

The usual scalar objective is annualized tracking error

\[
\mathrm{TE}(w) = \sqrt{252}\;\widehat{\mathrm{std}}\,(w^\top R_t - r_t).
\]

Holding fewer names raises TE, so the interesting design choice is how to pick
the \(k\) names and how to weight them.

## 2. Data

Prices are downloaded through Yahoo Finance for `^NSEI` and a fixed list of NSE
tickers that approximate a recent Nifty 50 membership. Adjusted closes are
converted to simple returns. Rows with missing values after a light forward fill
are dropped. The time series is split chronologically (default 70% train /
30% test); there is no random shuffle, because leakage across time would make
tracking numbers meaningless.

If the download is incomplete, the loader builds a synthetic panel from three
latent Gaussian factors plus idiosyncratic noise. Index returns are a
positive-weight combination of the asset returns. That fallback is only for
pipeline smoke tests; real conclusions need `meta.source = "yfinance"`.

## 3. Model: Index-Constrained Sparse Autoencoder

### 3.1 Soft selection

Learnable logits \(\ell \in \mathbb{R}^N\) define soft portfolio weights

\[
w = \mathrm{softmax}(\ell / T),
\]

where temperature \(T\) anneals from 1.5 to 0.6 during training. Softmax keeps
\(w\) on the probability simplex without a separate projection step.

### 3.2 Autoencoder body

Each batch of stock returns \(X\) is gated by the current weights,

\[
\tilde{X} = X \odot (N\, w)^\top,
\]

then passed through a two-layer tanh encoder into a latent code of size \(d\)
(default 8) and decoded back to \(\hat{X}\). Soft gating scales each name by a
normalized function of \(w\), so poorly selected names influence the latent code
less without hard-zeroing gradients early in training.

Portfolio returns on the batch are simply \(p = X w\).

### 3.3 Loss

For a batch,

\[
\mathcal{L}
=
\lambda_{\mathrm{rec}}\,\|X-\hat{X}\|_F^2
+
\lambda_{\mathrm{tr}}\,\|p - r\|_2^2
+
\lambda_{2}\,\|w - \tfrac{1}{N}\mathbf{1}\|_2^2
+
\lambda_{c}\sum_i \big[\mathrm{ReLU}(w_i - w_{\max})\big]^2.
\]

Tracking is the dominant term. A light ridge toward equal weight keeps the
softmax from drifting into a random corner early in training. The concentration
penalty stops any single name from taking more than \(w_{\max}\) (default 0.25)
of the soft portfolio, which otherwise collapses selection quality.

Defaults: \(\lambda_{\mathrm{rec}}=0.5\), \(\lambda_{\mathrm{tr}}=25\),
\(\lambda_2=0.001\), \(\lambda_c=2\), \(w_{\max}=0.25\).

### 3.4 Hard sparsification and weight refinement

Names are ranked by a blend of soft portfolio weight (70%) and L1 column norm of
the first encoder layer (30%). The top \(k\) are kept. Soft mass on that subset
is a starting point; by default the final weights are re-fit with projected
non-negative least squares on the training window (same simplex projection used
by the quadratic baselines). The network therefore owns **selection**; the LS
step owns **weights on the chosen set**. That split is intentional: selection is
where the autoencoder’s factor view helps, while a convex tracker is hard to beat
once the subset is fixed.

## 4. Baselines

| Method | Selection | Weights |
|--------|-----------|---------|
| Random equal | uniform sample of \(k\) names | \(1/k\) |
| Low-vol equal | \(k\) smallest in-sample vols | \(1/k\) |
| High-corr equal | \(k\) highest corr with index | \(1/k\) |
| High-corr + quad | same names | projected LS vs index |
| PCA equal | top loadings on leading PCs | \(1/k\) |
| PCA + quad | same names | projected LS vs index |
| Greedy forward | stepwise MSE reduction | projected LS on chosen set |
| Full-universe LS | all names | projected LS (dense reference) |

Projected LS here means ordinary least squares followed by clipping negatives
and renormalizing. It is a lightweight stand-in for a simplex QP and needs no
extra solver package.

## 5. Training details

- Optimizer: Adam, learning rate \(10^{-3}\), weight decay \(10^{-5}\)
- Batch size 64, default 400 epochs
- Gradient clipping at global norm 5
- Xavier init on linear layers; selection logits start near zero with tiny noise

The network is small on purpose. Daily equity panels are short relative to
deep-learning norms, so capacity is kept low to limit overfit on the train
window.

## 6. Evaluation protocol

All methods are fit on the train window only. Metrics are reported separately
for train and test:

- annualized tracking error (primary)
- mean absolute daily active return
- \(R^2\) treating the index as the target path
- correlation of portfolio and index returns
- annualized active mean return
- portfolio / index volatility and max drawdown

Plots cover cumulative wealth on the test set, active-return paths for ICSAE,
training loss curves, and a bar chart of OOS tracking errors.

## 7. Design choices and limitations

**Fixed membership.** Real Nifty 50 membership changes. Using a static ticker
list avoids look-ahead on future inclusions only if the list is dated to the
start of the sample; here the list is a convenience basket. Treat results as a
method study, not as a historical fund backtest with official reconstitutions.

**No costs.** TE ignores spreads, impact, and rebalance turnover. A production
desk would add a turnover penalty or a holding period constraint.

**Long-only.** Shorting is disallowed by the softmax parameterization. That
matches typical passive equity mandates but rules out dollar-neutral overlays.

**Why an autoencoder at all?** Pure tracking LS on a pre-selected subset often
works well. The autoencoder is useful when selection should depend on how names
participate in a shared latent factor structure, not only on pairwise
correlation with the index. Whether that helps on a given sample is an empirical
question; the baseline table is there so the neural method has to earn its keep.

## 8. Reproducing a run

```bash
cd nifty50_tracker
pip install -r requirements.txt
python -m src.run_pipeline --k 10 --epochs 400 --seed 42
```

Inspect `results/run_summary.json` for data source and TE numbers, and
`results/test_metrics.csv` for the full comparison table.
