"""VN30F1M 10-minute bars on a clean continuous-session grid.

Input: a parquet (or csv) file with columns time_vn (bar open time, Vietnam time, tz-aware or naive), open, high,
low, close, volume. Only the 24 continuous-session bars per day are kept (09:00-11:20, 13:00-14:20); the 11:30 /
14:30 stub bars and the 14:40 ATC bar are dropped.
"""
import datetime as dt
from pathlib import Path

import numpy as np
import polars as pl

SLOTS = ["09:00", "09:10", "09:20", "09:30", "09:40", "09:50", "10:00", "10:10", "10:20", "10:30", "10:40", "10:50",
         "11:00", "11:10", "11:20", "13:00", "13:10", "13:20", "13:30", "13:40", "13:50", "14:00", "14:10", "14:20"]
IS_START, IS_END = dt.datetime(2018, 8, 13), dt.datetime(2021, 8, 13)        # in-sample = first 3 years
FOLDS = ((dt.date(2018, 8, 13), dt.date(2019, 8, 13)), (dt.date(2019, 8, 13), dt.date(2020, 8, 13)),
         (dt.date(2020, 8, 13), dt.date(2021, 8, 13)))


def load(path, until=None, since=None):
    """Bars with since <= t < until (naive Vietnam time), plus bod (bar-of-day 0..23) and day columns."""
    path = Path(path)
    d = pl.read_parquet(path) if path.suffix == ".parquet" else pl.read_csv(path, try_parse_dates=True)
    t = pl.col("time_vn")
    if isinstance(d.schema["time_vn"], pl.Datetime) and d.schema["time_vn"].time_zone:
        t = t.dt.convert_time_zone("Asia/Ho_Chi_Minh").dt.replace_time_zone(None)
    d = (d.with_columns(t.alias("t")).with_columns(pl.col("t").dt.strftime("%H:%M").alias("hm"))
         .filter(pl.col("hm").is_in(SLOTS)).sort("t"))
    if until is not None:
        d = d.filter(pl.col("t") < until)
    if since is not None:
        d = d.filter(pl.col("t") >= since)
    return d.with_columns(pl.col("hm").replace_strict({s: i for i, s in enumerate(SLOTS)}, return_dtype=pl.Int32).alias("bod"),
                          pl.col("t").dt.date().alias("day"))


def is_folds(days):
    """Fold index 0..2 for each in-sample day, -1 elsewhere."""
    fold = np.full(len(days), -1)
    for k, (a, b) in enumerate(FOLDS):
        fold[(days >= np.datetime64(a)) & (days < np.datetime64(b))] = k
    return fold
