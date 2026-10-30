# Caveats

| Issue | Effect |
|-------|--------|
| Choosing alphas by their OS result | The "best" table is sorted by OS. Among 208 alphas with a median OS Sharpe of 0.53, the top few at about 1.3 are partly luck; a fair forward expectation is lower (roughly 0.7-1.0). |
| OS window used before | Two earlier, different grammars were also scored on this 2021-2026 window (both failed). This is the third look, so the window is no longer a pristine holdout. |
| Decay | Book SUM10 goes from IS Sharpe 3.1 to OS 1.1 (ratio 0.35, below the usual 0.4-0.6 bar). |
| Not computed | PBO and Deflated Sharpe were not computed for this batch. |
| Cost sensitivity | Average losing trade is about 2.6 pts including costs; at 0.5 pt slippage every listed alpha falls below OS Sharpe 1.0. |
| Concentration | The top three share `vmom18` and the T200 trend filter: one idea, not three. |
| Regime | 2026 YTD is flat to negative for the books. |

The only clean test left is forward (paper) trading from 2026-10-29 on.

## Related

- [Batch b1 results](results.md)
- [Methodology](methodology.md)
- [README](../README.md)
