"""Causal technical indicators on 1-D float arrays.

Every value at bar i uses bars <= i only. Rolling outputs are NaN until the window is full; a NaN inside a window
propagates (no skipping). Conventions: EMA is seeded with the first value, ATR is the simple mean of the true range,
standard deviations are population (ddof = 0), quantiles use linear interpolation.
"""
import numpy as np
from numba import njit


@njit(cache=True)
def sma(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].mean()
    return out


@njit(cache=True)
def rolling_std(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].std()
    return out


@njit(cache=True)
def rolling_quantile(x, n, q):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.quantile(x[i - n + 1:i + 1], q)
    return out


@njit(cache=True)
def rolling_max(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].max()
    return out


@njit(cache=True)
def rolling_min(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].min()
    return out


@njit(cache=True)
def rolling_zscore(x, n):
    """(x - mean) / std over the window; 0 when the window is flat."""
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        s = w.std()
        out[i] = (x[i] - w.mean()) / s if s != 0 else 0.0
    return out


@njit(cache=True)
def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.empty(len(x))
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def squash(x):
    """tanh with the input clipped to [-10, 10]; NaN stays NaN."""
    return np.tanh(np.clip(x, -10.0, 10.0))


@njit(cache=True)
def true_range(h, l, c):
    tr = np.zeros(len(c))
    for i in range(1, len(c)):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    return tr


@njit(cache=True)
def atr(h, l, c, n):
    tr = true_range(h, l, c)
    out = np.full(len(c), np.nan)
    for i in range(n, len(c)):
        out[i] = tr[i - n + 1:i + 1].mean()
    return out


@njit(cache=True)
def _up_down(c, i, n):
    up = 0.0; dn = 0.0
    for j in range(i - n + 1, i + 1):
        d = c[j] - c[j - 1]
        if d > 0:
            up += d
        else:
            dn -= d
    return up, dn


@njit(cache=True)
def rsi(c, n):
    """RSI with simple (not Wilder) averages of the last n changes."""
    out = np.full(len(c), np.nan)
    for i in range(n, len(c)):
        up, dn = _up_down(c, i, n)
        out[i] = 100.0 - 100.0 / (1.0 + up / dn) if dn != 0 else 100.0
    return out


@njit(cache=True)
def cmo(c, n):
    out = np.full(len(c), np.nan)
    for i in range(n, len(c)):
        up, dn = _up_down(c, i, n)
        out[i] = 100.0 * (up - dn) / (up + dn) if up + dn != 0 else 0.0
    return out


@njit(cache=True)
def mfi(h, l, c, v, n):
    tp = (h + l + c) / 3.0
    out = np.full(len(c), np.nan)
    for i in range(n, len(c)):
        pos = 0.0; neg = 0.0
        for j in range(i - n + 1, i + 1):
            if tp[j] > tp[j - 1]:
                pos += tp[j] * v[j]
            else:
                neg += tp[j] * v[j]
        out[i] = 100.0 - 100.0 / (1.0 + pos / neg) if neg != 0 else 100.0
    return out


@njit(cache=True)
def stoch_k(h, l, c, n):
    out = np.full(len(c), np.nan)
    for i in range(n - 1, len(c)):
        hh = h[i - n + 1:i + 1].max(); ll = l[i - n + 1:i + 1].min()
        out[i] = 100.0 * (c[i] - ll) / (hh - ll) if hh != ll else 50.0
    return out


@njit(cache=True)
def kama(c, n):
    """Kaufman adaptive moving average, fast 2 / slow 30."""
    out = np.full(len(c), np.nan)
    if len(c) < n + 1:
        return out
    fast = 2.0 / 3.0; slow = 2.0 / 31.0
    out[n - 1] = c[n - 1]
    for i in range(n, len(c)):
        path = 0.0
        for j in range(i - n + 1, i + 1):
            path += abs(c[j] - c[j - 1])
        sc = (abs(c[i] - c[i - n]) / path * fast + (1.0 - abs(c[i] - c[i - n]) / path) * slow) ** 2 if path != 0 else slow ** 2
        out[i] = out[i - 1] + sc * (c[i] - out[i - 1])
    return out


@njit(cache=True)
def linreg_angle(c, n):
    """Angle in degrees of the least-squares line through the last n closes."""
    out = np.full(len(c), np.nan)
    t = np.arange(n) - (n - 1) / 2.0
    tt = (t * t).sum()
    for i in range(n - 1, len(c)):
        y = c[i - n + 1:i + 1]
        out[i] = np.degrees(np.arctan(((y - y.mean()) * t).sum() / tt))
    return out


def chaikin_osc(h, l, c, v, fast, slow):
    """EMA(fast) - EMA(slow) of the accumulation / distribution line."""
    hl = h - l
    clv = np.where(hl != 0, ((c - l) - (h - c)) / np.where(hl != 0, hl, 1.0), 0.0)
    adl = np.cumsum(clv * v)
    return ema(adl, fast) - ema(adl, slow)


@njit(cache=True)
def vwap(h, l, c, v, n):
    """Rolling n-bar VWAP of the typical price; NaN when the window has no volume."""
    tp = (h + l + c) / 3.0
    out = np.full(len(c), np.nan)
    for i in range(n - 1, len(c)):
        vs = v[i - n + 1:i + 1].sum()
        if vs != 0:
            out[i] = (tp[i - n + 1:i + 1] * v[i - n + 1:i + 1]).sum() / vs
    return out
