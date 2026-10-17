"""Dual-timeframe rules.

Higher timeframe (weekly) decides WHETHER to be long; lower timeframe
(daily) decides WHEN.

  Long entry : weekly SuperTrend up  AND daily SuperTrend up  AND close > DEMA(200)
  Exit       : daily SuperTrend flips down  OR close < DEMA(200)  OR weekly turns down

No look-ahead: a weekly bar is only known after the week closes, so its
direction is applied from the NEXT week's first session.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .indicators import dema, supertrend


@dataclass(frozen=True)
class SystemParams:
    st_period: int = 10
    st_mult: float = 3.0
    wk_st_period: int = 10
    wk_st_mult: float = 3.0
    dema_len: int = 200
    use_weekly_filter: bool = True


def resample_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Daily OHLCV -> weekly bars ending Friday."""
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    if "Volume" in df:
        agg["Volume"] = "sum"
    return df.resample("W-FRI").agg(agg).dropna(subset=["Close"])


def weekly_filter(df: pd.DataFrame, period: int, mult: float) -> pd.Series:
    """Weekly SuperTrend direction mapped onto daily dates WITHOUT look-ahead."""
    wk = resample_weekly(df)
    wdir = supertrend(wk, period, mult)["dir"]
    known_from = wdir.shift(1)                   # week t's direction usable during week t+1
    return known_from.reindex(df.index, method="ffill").fillna(0).astype(int)


def generate_positions(df: pd.DataFrame, p: SystemParams = SystemParams()) -> pd.DataFrame:
    """Return frame with indicators, raw conditions and the 0/1 position held
    at each day's close (stateful: once in, stay in until an exit rule fires)."""
    out = df.copy()
    st = supertrend(df, p.st_period, p.st_mult)
    out["st"], out["st_dir"] = st["st"], st["dir"]
    out["dema"] = dema(df["Close"], p.dema_len)
    out["wk_dir"] = weekly_filter(df, p.wk_st_period, p.wk_st_mult) if p.use_weekly_filter else 1
    above = out["Close"] > out["dema"]
    want = (out["st_dir"] == 1) & above & (out["wk_dir"] == 1)
    exit_ = (out["st_dir"] == -1) | ~above | (out["wk_dir"] != 1)
    pos, holding = [], 0
    for w, x in zip(want.values, exit_.values):
        if holding and x:
            holding = 0
        elif not holding and w:
            holding = 1
        pos.append(holding)
    out["position"] = pos
    out["entry"] = (out["position"].diff() == 1)
    out["exit"] = (out["position"].diff() == -1)
    return out
