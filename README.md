# vn30f1m-alpha-mining

Intraday alphas for the Vietnamese VN30 index future (VN30F1M, 10-minute bars), found by an LLM-guided grammar
miner, selected on 3 years of in-sample data only, then frozen and scored **once** on 5 years of out-of-sample data.

No price data is included: bring your own VN30F1M 10-minute OHLCV (see [data format](docs/data-format.md)).

## Best alphas (batch b1, OS Sharpe > 1.2 at 0.3 pt slippage)

| Alpha | IS worst-year Sharpe | OS Sharpe | OS Sharpe @0.5 slip | OS points | OS max DD | OS win rate |
|-------|---:|---:|---:|---:|---:|---:|
| `pair\|rangexp18&vmom18\|s5\|q100@0.85+\|T200\|none\|all\|both` | 2.01 | **1.37** | 0.95 | 705 | -102 | 38.8% |
| `pair\|tsi18&vmom18\|s5\|q100@0.85+\|T200\|none\|all\|both` | 2.06 | **1.35** | 0.95 | 718 | -116 | 39.7% |
| `pair\|roc27&vmom18\|s5\|q100@0.8+\|T200\|none\|all\|both` | 1.30 | **1.33** | 0.98 | 815 | -126 | 42.9% |
| `pair\|tsi9&upvol18\|s3\|q100@0.85+\|T200\|none\|pm\|both` | 1.60 | **1.30** | 0.98 | 541 | -69 | 42.1% |
| `quantile\|kamasl18\|s5\|q65@0.85+\|T200\|none\|all\|both` | 1.00 | **1.21** | 0.78 | 853 | -167 | 42.3% |
| `pair\|upvol18&macd12\|s3\|q100@0.75+\|T200\|calm\|pm\|both` | 1.05 | **1.20** | 0.85 | 493 | -88 | 43.4% |
| Book SUM10 (equal-weight top-10 by IS, 1/10 contract each) | 3.02 | **1.09** | 0.55 | 421 | -82 | — |

Points are VN30 index points per contract (1 pt = 100,000 VND), net of costs. IS = 2018-08-13 .. 2021-08-12,
OS = 2021-08-13 .. 2026-10-28. Full table of all 268 frozen alphas: [`alphas/batch_b1.json`](alphas/batch_b1.json).

**Read the caveats before using any of these:** [docs/caveats.md](docs/caveats.md). In short, picking the best
alphas *by OS* turns OS into in-sample; expect less going forward.

## What the best alpha does

Trade only in the direction of the multi-day trend (close vs its 200-bar SMA, about 8 sessions). Enter when the
recent bars are unusually long relative to ATR in one direction (`rangexp`) **and** volume-weighted momentum
(`vmom`) confirms it, both above their 85th percentile of the last 100 bars. Exit as soon as either fades
(median hold about 50 minutes). It loses small on most false breakouts and wins about 3x larger on real trend
days: win rate about 40%, payoff about 3.1. More in [docs/alpha-grammar.md](docs/alpha-grammar.md).

## Quick start

```bash
pip install -r requirements.txt
python scripts/run_alphas.py path/to/VN30F1M_10m.parquet            # best alphas + top-10 books
python scripts/run_alphas.py path/to/VN30F1M_10m.parquet --slip 0.5
python scripts/run_alphas.py path/to/VN30F1M_10m.parquet --group all # all 268 -> results/rerun.csv
```

```python
from vn30alpha import data, grammar as G, backtest as B
import json
d = data.load("VN30F1M_10m.parquet"); cx = G.Ctx(d)
alpha = json.load(open("alphas/batch_b1.json"))["alphas"][0]["alpha"]
sig = G.signal(cx, alpha)                          # position held over the next bar, in {-1, 0, 1}
net, n_trades, n_wins = B.pnl(cx.D["o"], cx.D["c"], cx.di, sig, slip=0.3)
```

## Layout

| Path | Content |
|------|---------|
| `vn30alpha/indicators.py` | causal indicators (numba) |
| `vn30alpha/grammar.py` | 28 primitives, 3 templates, filters, `signal()` |
| `vn30alpha/backtest.py` | next-bar-open fills, VN derivatives costs, Sharpe / drawdown |
| `vn30alpha/data.py` | loader for the clean 24-bar session grid, IS window and folds |
| `alphas/batch_b1.json` | 268 frozen alphas (208 admitted + 60 random rejected controls) with IS and OS metrics |
| `results/` | the tables above, at 0.3 and 0.5 pt slippage |

## Docs

- [Methodology: IS/OS protocol, miner, costs](docs/methodology.md)
- [Alpha grammar](docs/alpha-grammar.md)
- [Batch b1 results](docs/results.md)
- [Caveats](docs/caveats.md)
- [Data format](docs/data-format.md)

Research code, not investment advice. MIT licence.
