# Methodology

## IS / OS protocol

| Segment | Window | Use |
|---------|--------|-----|
| In-sample (IS) | 2018-08-13 .. 2021-08-12 (3 yearly folds) | mining, filtering, ranking, building books |
| Out-of-sample (OS) | 2021-08-13 .. 2026-10-28 | scored once per frozen batch, never used to choose or tune |

- The miner's evaluator loads data only up to the IS end and asserts it.
- A batch is frozen from the IS database (alpha definitions, IS metrics, the top-10 and its books), written to
  disk, then a lock file is written before the full series is loaded. The OS run happens once per batch.

## Miner

- A local LLM (Qwen3-8B via Ollama) proposes alphas as **typed slot values** through a JSON schema; no LLM-written
  code is executed. Each iteration: 8 LLM proposals + 8 random ones + mutations of good candidates.
- Admission on IS: worst of the 3 yearly fold Sharpes >= 1.0 and >= 150 trades; near-duplicates (daily P&L
  correlation > 0.9 with an admitted alpha) are dropped.
- Batch b1 was frozen after 1,701 trials: 208 admitted alphas plus 60 random rejected alphas (>= 150 trades)
  kept as a control group.
- Top-10: greedy by IS worst-fold Sharpe, skipping alphas with IS daily P&L correlation >= 0.7 to the ones taken.
  Books: `SUM10` (mean of the 10 signals, so 1/10 contract each) and `MV2` (majority vote, >= 2 agree).

## Execution and costs

| Item | Model |
|------|-------|
| Bars | 10-minute, 24 continuous-session bars per day; stub (11:30, 14:30) and ATC (14:40) bars dropped |
| Fills | signal at the close of bar i-1, filled at the open of bar i |
| Holding | bar by bar; overnight positions allowed |
| Slippage | 0.3 index points per side (also reported at 0.5) |
| Fees | 6,250 VND per contract per side |
| Tax | 0.85 bp of notional per side (8.5 x price / 1e5 points) |
| Overnight | VSD margin fee on carried positions |

## Metrics

Annualised Sharpe of daily point P&L (252 days), total points, maximum drawdown in points, trade win rate net
of costs (a flip counts as an exit plus an entry).

## Related

- [Alpha grammar](alpha-grammar.md)
- [Batch b1 results](results.md)
- [Caveats](caveats.md)
- [README](../README.md)
