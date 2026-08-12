# Sample run notes

Date window: 2019-01-03 to 2025-12-30 (Yahoo Finance, 50 names, 1725 trading days).
Split: 70% train / 30% test. Sparse cardinality k = 10. Seed 42. Epochs 400.

Out-of-sample annualized tracking error (lower is better):

| Method | TE (ann.) | R² |
|--------|-----------|-----|
| Full-universe LS (dense ref.) | 2.04% | 0.975 |
| Greedy forward (k=10) | 3.80% | 0.913 |
| ICSAE sparse (k=10) | 4.41% | 0.884 |
| High-corr + quad | 5.64% | 0.809 |
| PCA + quad | 6.02% | 0.783 |
| Random equal | 7.14% | 0.694 |
| Low-vol equal | 8.36% | 0.581 |

ICSAE selected: HDFC Bank, Reliance, ICICI Bank, Infosys, Kotak Bank, TCS,
ITC, Axis Bank, SBI, L&T — large, liquid names that dominate Nifty risk.

Figures: `oos_cumulative.png`, `oos_te_bars.png`, `oos_active.png`,
`training_curve.png`. Tables: `test_metrics.csv`, `icsae_weights.csv`.
