"""Backtest the published alphas on your own VN30F1M 10-minute data.

  python scripts/run_alphas.py DATA.parquet                       # the 6 alphas with OS Sharpe > 1.2 + the top-10 books
  python scripts/run_alphas.py DATA.parquet --group all           # all 268 frozen batch-b1 alphas -> results/rerun.csv
  python scripts/run_alphas.py DATA.parquet --slip 0.5 --out results/best_slip05.csv

IS = 2018-08-13 .. 2021-08-12 (3 yearly folds); OS = everything after. Points per contract, net of costs.
"""
import argparse, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vn30alpha import backtest as B, data, grammar as G     # noqa: E402


def run(cx, sig, slip, is_mask, fold):
    is_bar = is_mask[cx.di]
    net, _, _ = B.pnl(cx.D["o"], cx.D["c"], cx.di, sig, slip)
    dly = B.daily(net, cx.di, len(cx.days))
    s_os = sig.copy(); s_os[is_bar] = 0                                    # OS trades only, for the OS win rate
    _, ntr, nw = B.pnl(cx.D["o"], cx.D["c"], cx.di, s_os, slip)
    i_s, o_s = B.stats(dly[is_mask], fold[is_mask]), B.stats(dly[~is_mask])
    return dict(is_worst=i_s["worst"], is_sharpe=i_s["sharpe"], os_sharpe=o_s["sharpe"], os_pts=o_s["pts"], os_dd=o_s["dd"],
                os_trades=ntr, os_wr=nw / max(ntr, 1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("--group", default="best", choices=["best", "top10", "all"])
    ap.add_argument("--slip", type=float, default=0.3); ap.add_argument("--out")
    a = ap.parse_args()
    book = json.loads((ROOT / "alphas/batch_b1.json").read_text())
    d = data.load(a.data, since=data.IS_START)
    cx = G.Ctx(d)
    days = cx.days.astype("datetime64[D]")
    is_mask = days < np.datetime64(data.IS_END.date()); fold = data.is_folds(days)
    rows = []
    for x in book["alphas"]:
        if a.group == "all" or (a.group == "best" and x["os_sharpe"] > 1.2) or x["key"] in book["top10"]:
            rows.append(dict(key=x["key"], group=x["group"], **run(cx, G.signal(cx, x["alpha"]), a.slip, is_mask, fold)))
    S = np.vstack([G.signal(cx, x["alpha"]) for x in book["alphas"] if x["key"] in book["top10"]])
    for name, sig in (("BOOK_SUM10", S.sum(0) / len(S)), ("BOOK_MV2", B.majority(S, 2))):
        rows.append(dict(key=name, group="book", **run(cx, sig, a.slip, is_mask, fold)))
    R = pd.DataFrame(rows)
    if a.out or a.group == "all":
        R.to_csv(a.out or ROOT / "results/rerun.csv", index=False)
    pd.set_option("display.width", 200)
    print(R.round(3).to_string(index=False))
