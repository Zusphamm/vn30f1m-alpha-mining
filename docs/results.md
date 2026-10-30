# Batch b1 results

Frozen 2026-10-30 after 1,701 trials; OS 2021-08-13 .. 2026-10-28; slippage 0.3 pt per side unless noted.

## IS selection vs random control

| Group | Alphas | OS Sharpe median | OS Sharpe > 0 | OS Sharpe > 1.2 |
|-------|---:|---:|---:|---:|
| Random rejected (control) | 60 | -0.03 | 48% | 0 |
| Admitted (incl. top-10) | 208 | 0.53 | 88% | 6 |
| Top-10 (diverse, by IS) | 10 | 0.70 | 100% | 1 |

The IS filter separates alphas with an edge from noise. Within the admitted group, though, the IS ranking barely
predicts the OS ranking (Spearman about 0.07): IS tells you which alphas work, not which work best.

## Books from the top-10

| Book | IS Sharpe | OS Sharpe | OS @0.5 slip | OS points | OS max DD |
|------|---:|---:|---:|---:|---:|
| SUM10 | 3.13 | 1.09 | 0.55 | 421 | -82 |
| MV2 | 2.46 | 0.82 | 0.34 | 670 | -165 |

SUM10 OS Sharpe by year: 2021 1.09, 2022 1.30, 2023 0.63, 2024 1.14, 2025 2.40, 2026 -0.09. OS/IS Sharpe ratio
about 0.35.

## Per-alpha tables

- [`results/best_slip03.csv`](../results/best_slip03.csv), [`results/best_slip05.csv`](../results/best_slip05.csv):
  the 6 alphas with OS Sharpe > 1.2, the top-10 and both books.
- [`alphas/batch_b1.json`](../alphas/batch_b1.json): every frozen alpha with its definition, IS metrics, OS
  Sharpe (0.3 and 0.5 slip), points, drawdown and yearly OS Sharpe.

## Related

- [Caveats](caveats.md)
- [Methodology](methodology.md)
- [README](../README.md)
