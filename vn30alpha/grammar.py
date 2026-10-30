"""Typed-slot alpha grammar: 28 primitives x 3 templates x trend / volatility / session / side filters.

An alpha is a dict of slot values (see alphas/*.json); signal() turns it into a held position per bar in {-1, 0, 1}.
"""
import numpy as np
from numba import njit

from . import indicators as ind

PERIODS = (6, 9, 12, 14, 18, 20, 27, 30, 40, 60)
QW = (20, 35, 65, 100)
QS = (0.65, 0.7, 0.75, 0.8, 0.85)
TRENDS = (0, 100, 200, 400)
SMOOTH = (1, 3, 5)
VOLF = ("none", "calm", "active")
SESSION = ("all", "am", "pm")
SIDES = ("both", "long", "short")
TEMPLATES = {"quantile": "x above its rolling q-quantile -> long, below its (1-q)-quantile -> short",
             "pair": "a AND b both above their q-quantiles -> long, both below -> short (confirmation)",
             "zero": "sign of the smoothed indicator x (long when x > 0), no quantile"}
DESC = {
    "linreg": "angle of the linear-regression line of close over p bars", "pgo": "typical price minus its p-bar SMA, relative",
    "wave": "tanh z-score of mid-price / its p-bar SMA", "roc": "p-bar rate of change of close", "rsi": "RSI(p) - 50",
    "cmo": "Chande momentum oscillator(p)", "macd": "MACD histogram with fast p, slow 2p, signal 9",
    "ppo": "(EMA p - EMA 2p) / EMA 2p", "trix": "1-bar slope of triple-smoothed EMA(p)", "emasl": "3-bar slope of EMA(p)",
    "bb": "Bollinger position (c - SMA p) / 2 std", "stoch": "stochastic %K(p) - 50", "cci": "(typical - SMA p) / std p",
    "kamasl": "3-bar slope of KAMA(p)", "donch": "position of close inside the p-bar Donchian channel",
    "mfi": "money flow index(p) - 50", "chaikin": "Chaikin A/D oscillator (p/3, p)", "vwdev": "close vs rolling p-bar VWAP, relative",
    "tsi": "true strength index (p, p/2)", "vmom": "volume-weighted momentum over p bars",
    "er": "signed Kaufman efficiency ratio over p bars", "obvsl": "OBV change over p bars / volume over p bars",
    "clv": "mean close-location-value over p bars", "aroon": "Aroon oscillator(p)", "ha": "EMA(p) of Heikin-Ashi body / ATR",
    "dpo": "detrended price oscillator(p)", "upvol": "(up-bar volume - down-bar volume) / volume over p",
    "rangexp": "EMA(p) of bar range / ATR times bar direction"}


def _lag(x, k):
    return np.r_[np.full(k, np.nan), x[:-k]]


def _rsum(x, p):
    return ind.sma(np.nan_to_num(x), p) * p


@njit(cache=True)
def _aroon(h, l, p):
    out = np.full(len(h), np.nan)
    for i in range(p, len(h)):
        hi = 0; lo = 0
        for j in range(p + 1):
            if h[i - j] >= h[i - hi]: hi = j
            if l[i - j] <= l[i - lo]: lo = j
        out[i] = (lo - hi) / p
    return out


def primitive(name, p, D):
    o, h, l, c, v = D["o"], D["h"], D["l"], D["c"], D["v"]
    tp = (h + l + c) / 3; dc = np.r_[0, np.diff(c)]
    if name == "linreg": return ind.linreg_angle(c, p)
    if name == "pgo": s = ind.sma(tp, p); return (tp - s) / s
    if name == "wave": m = (h + l) / 2; return ind.squash(ind.rolling_zscore(m / ind.sma(m, p), 35))
    if name == "roc": return c / _lag(c, p) - 1
    if name == "rsi": return ind.rsi(c, p) - 50
    if name == "cmo": return ind.cmo(c, p)
    if name == "macd": m = ind.ema(c, p) - ind.ema(c, 2 * p); return m - ind.ema(np.nan_to_num(m), 9)
    if name == "ppo": s = ind.ema(c, 2 * p); return (ind.ema(c, p) - s) / s
    if name == "trix": e = ind.ema(ind.ema(ind.ema(c, p), p), p); return e / _lag(e, 1) - 1
    if name == "emasl": e = ind.ema(c, p); return e / _lag(e, 3) - 1
    if name == "bb": return (c - ind.sma(c, p)) / (2 * ind.rolling_std(c, p))
    if name == "stoch": return ind.stoch_k(h, l, c, p) - 50
    if name == "cci": return (tp - ind.sma(tp, p)) / ind.rolling_std(tp, p)
    if name == "kamasl": k = ind.kama(c, p); return k / _lag(k, 3) - 1
    if name == "donch": mx, mn = ind.rolling_max(h, p), ind.rolling_min(l, p); return (c - (mx + mn) / 2) / (mx - mn)
    if name == "mfi": return ind.mfi(h, l, c, v, p) - 50
    if name == "chaikin": return ind.chaikin_osc(h, l, c, v, max(2, p // 3), p)
    if name == "vwdev": w = ind.vwap(h, l, c, v, p); return (c - w) / w
    if name == "tsi":
        q = max(2, p // 2)
        return ind.ema(ind.ema(dc, p), q) / (ind.ema(ind.ema(np.abs(dc), p), q) + 1e-12)
    if name == "vmom": return ind.sma(dc * v, p) / (ind.sma(np.abs(dc) * v, p) + 1e-12)
    if name == "er": return (c - _lag(c, p)) / (_rsum(np.abs(dc), p) + 1e-12)
    if name == "obvsl": obv = np.cumsum(np.sign(dc) * v); return (obv - _lag(obv, p)) / (_rsum(v, p) + 1e-12)
    if name == "clv": return ind.sma(((c - l) - (h - c)) / np.maximum(h - l, 1e-9), p)
    if name == "aroon": return _aroon(h, l, p)
    if name == "ha":
        hc = (o + h + l + c) / 4; ho = np.empty_like(c); ho[0] = (o[0] + c[0]) / 2
        for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
        return ind.ema(hc - ho, p) / ind.atr(h, l, c, 14)
    if name == "dpo": return (c - _lag(ind.sma(c, p), p // 2 + 1)) / c
    if name == "upvol": return _rsum(np.where(dc > 0, v, 0.0) - np.where(dc < 0, v, 0.0), p) / (_rsum(v, p) + 1e-12)
    if name == "rangexp": return ind.ema(np.nan_to_num((h - l) / ind.atr(h, l, c, 14) * np.sign(c - o)), p)
    raise KeyError(name)


class Ctx:
    """Price arrays, filters and an indicator cache for one data window."""
    def __init__(self, d):
        self.D = {k: d[x].to_numpy().astype(float) for k, x in (("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"), ("v", "volume"))}
        self.days, self.di = np.unique(d["day"].to_numpy(), return_inverse=True)
        self.bod = d["bod"].to_numpy()
        c, h, l = self.D["c"], self.D["h"], self.D["l"]
        self.trend = {n: c > ind.sma(c, n) for n in TRENDS if n}
        a = ind.atr(h, l, c, 14); base = ind.sma(a, 100)
        self.vol = {"calm": a < base * 1.5, "active": a > base}
        self.cache = {}

    def x(self, name, p, smooth):
        k = (name, p, smooth)
        if k not in self.cache:
            x = np.asarray(primitive(name, p, self.D), float)
            y = ind.ema(np.nan_to_num(x), smooth) if smooth > 1 else x.copy()
            y[np.isnan(x)] = np.nan
            self.cache[k] = y
        return self.cache[k]


def signal(cx, a):
    """Alpha dict -> position held over the next bar (decided at bar close), in {-1, 0, 1}."""
    x = cx.x(a["a"], a["pa"], a["smooth"])
    if a["template"] == "zero":
        le, se = x > 0, x < 0
    else:
        le = x > ind.rolling_quantile(x, a["qw"], a["q"]); se = x < ind.rolling_quantile(x, a["qw"], 1 - a["q"])
        if a["sign"]: le &= x > 0; se &= x < 0
        if a["template"] == "pair":
            y = cx.x(a["b"], a["pb"], a["smooth"])
            le &= y > ind.rolling_quantile(y, a["qw"], a["q"]); se &= y < ind.rolling_quantile(y, a["qw"], 1 - a["q"])
    if a["trend"]: le &= cx.trend[a["trend"]]; se &= ~cx.trend[a["trend"]]
    if a["vol"] != "none": le &= cx.vol[a["vol"]]; se &= cx.vol[a["vol"]]
    if a["session"] == "am": m = cx.bod <= 14; le &= m; se &= m
    if a["session"] == "pm": m = cx.bod >= 15; le &= m; se &= m
    if a["side"] == "long": se[:] = False
    if a["side"] == "short": le[:] = False
    s = np.zeros(len(x)); s[le] = 1.0; s[se] = -1.0
    return s


def key(a):
    """Short readable id, e.g. pair|rangexp18&vmom18|s5|q100@0.85+|T200|none|all|both."""
    s = f"{a['template']}|{a['a']}{a['pa']}" + (f"&{a['b']}{a['pb']}" if a["template"] == "pair" else "")
    s += f"|s{a['smooth']}" + (f"|q{a['qw']}@{a['q']}{'+' if a['sign'] else ''}" if a["template"] != "zero" else "")
    return s + f"|T{a['trend']}|{a['vol']}|{a['session']}|{a['side']}"
