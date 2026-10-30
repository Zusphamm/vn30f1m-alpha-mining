"""Bar-by-bar P&L in index points for one VN30F1M contract, with Vietnamese derivatives costs.

Execution: the position decided at the close of bar i-1 is filled at the open of bar i (no same-bar fills).
Costs per side: slippage (points) + broker/exchange fee 6,250 VND + tax 8.5 x price / 1e5 (0.85 bp of notional),
plus the VSD overnight margin fee on positions carried across days. 1 point = 100,000 VND.
"""
import numpy as np
from numba import njit

FEE_VND, TAX_PT, PT_VND, VSD_DAY = 6250.0, 8.5, 100_000.0, 0.1848 * 0.000024


@njit(cache=True)
def pnl(o, c, di, sig, slip):
    """Net points per bar, number of closed trades, number of winning trades (net of costs)."""
    n = len(c); net = np.zeros(n); prev = 0.0; ntr = 0; nwin = 0; entry = 0.0
    for i in range(1, n):
        pos = sig[i - 1]
        gross = prev * (o[i] - c[i - 1]) + pos * (c[i] - o[i])
        cost = abs(pos - prev) * (slip + (FEE_VND + TAX_PT * o[i]) / PT_VND)
        if di[i] != di[i - 1] and prev != 0:
            cost += abs(prev) * c[i - 1] * VSD_DAY
        if pos != prev:
            if prev != 0:
                g = prev * (o[i] - entry) - 2 * slip - (2 * FEE_VND + TAX_PT * (entry + o[i])) / PT_VND
                ntr += 1
                if g > 0:
                    nwin += 1
            if pos != 0:
                entry = o[i]
        net[i] = gross - cost
        prev = pos
    return net, ntr, nwin


def daily(net, di, n_days):
    out = np.zeros(n_days)
    np.add.at(out, di, net)
    return out


def sharpe(x):
    sd = x.std(ddof=1)
    return x.mean() / sd * np.sqrt(252) if sd > 0 else 0.0


def stats(dly, fold=None):
    """Annualised Sharpe of daily points, total points, max drawdown; with fold: per-fold Sharpe and the worst one."""
    eq = np.cumsum(dly)
    r = dict(sharpe=sharpe(dly), pts=dly.sum(), dd=(eq - np.maximum.accumulate(np.r_[0, eq])[1:]).min())
    if fold is not None:
        fs = [sharpe(dly[fold == k]) for k in range(3)]
        r.update(f1=fs[0], f2=fs[1], f3=fs[2], worst=min(fs))
    return r


def majority(S, k):
    """Long when >= k signals are long and longs outnumber shorts (mirror for short)."""
    lo = (S > 0).sum(0); sh = (S < 0).sum(0); out = np.zeros(S.shape[1])
    out[(lo >= k) & (lo > sh)] = 1.0
    out[(sh >= k) & (sh > lo)] = -1.0
    return out
