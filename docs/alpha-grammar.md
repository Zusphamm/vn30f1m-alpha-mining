# Alpha grammar

An alpha is a dict of slot values; `vn30alpha.grammar.signal()` turns it into a position in {-1, 0, 1}.

## Slots

| Slot | Values | Meaning |
|------|--------|---------|
| `template` | `quantile`, `pair`, `zero` | see below |
| `a`, `pa` | primitive, period 6..60 | main indicator |
| `b`, `pb` | primitive, period | confirming indicator (`pair` only) |
| `smooth` | 1, 3, 5 | EMA smoothing of the indicators |
| `qw`, `q` | window 20..100 bars, quantile 0.65..0.85 | entry thresholds |
| `sign` | bool | also require x > 0 for longs, x < 0 for shorts |
| `trend` | 0, 100, 200, 400 | longs only when close > SMA(trend), shorts only below |
| `vol` | none, calm, active | ATR(14) vs its 100-bar mean |
| `session` | all, am, pm | morning bars (09:00-11:20) or afternoon bars (13:00-14:20) |
| `side` | both, long, short | |

| Template | Long when | Short when |
|----------|-----------|------------|
| `quantile` | x > rolling q-quantile of x | x < rolling (1-q)-quantile |
| `pair` | x and y both above their q-quantiles | both below their (1-q)-quantiles |
| `zero` | x > 0 | x < 0 |

The key `pair|rangexp18&vmom18|s5|q100@0.85+|T200|none|all|both` reads: pair template, `rangexp` (18) and
`vmom` (18), smoothing 5, quantile window 100 at 0.85 with the sign condition, trend filter SMA 200, no volatility
filter, all sessions, both sides.

## Primitives used by the best alphas

| Name | Definition |
|------|------------|
| `rangexp` | EMA(p) of (bar range / ATR14) x sign(close - open): directional range expansion |
| `vmom` | sum(dClose x volume) / sum(abs(dClose) x volume) over p bars: volume-weighted momentum |
| `upvol` | (up-bar volume - down-bar volume) / volume over p bars |
| `tsi` | true strength index (EMA p, then EMA p/2 of close changes) |
| `roc` | p-bar rate of change |
| `kamasl` | 3-bar slope of KAMA(p) |
| `macd` | MACD histogram, fast p, slow 2p, signal 9 |

All 28 primitives are documented in `DESC` in [`vn30alpha/grammar.py`](../vn30alpha/grammar.py).

## Economic reading

VN30F1M trends intraday: retail-heavy order flow, herding and large players splitting orders make moves that
start with range expansion and volume persist for a while. The best alphas buy that confirmation in the trend
direction and leave when it fades, so they lose small on false breakouts and win big on trend days (IS: 40% win
rate, average win 8.3 pts vs average loss 2.65 pts, the best 10% of trades carry all the profit). Mean-reversion
and high-win-rate (small take-profit, wide stop) variants did not survive costs in earlier rounds.

## Related

- [Methodology](methodology.md)
- [Batch b1 results](results.md)
- [README](../README.md)
