"""Indicators, implemented from their definitions (no TA-lib dependency)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def dema(s: pd.Series, n: int) -> pd.Series:
    """Double EMA = 2*EMA - EMA(EMA). Less lag than an EMA of the same length."""
    e1 = s.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    out = 2 * e1 - e2
    out.iloc[:n - 1] = np.nan
    return out


def atr_wilder(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 10) -> pd.Series:
    """ATR with Wilder smoothing (alpha = 1/n), the standard used by SuperTrend."""
    prev = close.shift(1)
    tr = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
    """SuperTrend line and direction (+1 up / -1 down).

    Bands = (H+L)/2 +/- multiplier*ATR. The final upper band only moves down
    (and the lower only up) while price stays inside, which is what makes it
    a trailing stop. Direction flips when close crosses the active band.
    """
    h, l, c = df["High"].values, df["Low"].values, df["Close"].values
    a = atr_wilder(df["High"], df["Low"], df["Close"], period).values
    mid = (h + l) / 2
    ub, lb = mid + multiplier * a, mid - multiplier * a
    n = len(c)
    fub, flb = np.full(n, np.nan), np.full(n, np.nan)
    direction, line = np.zeros(n, dtype=int), np.full(n, np.nan)
    start = int(np.argmax(~np.isnan(a)))
    if np.isnan(a[start]):
        return pd.DataFrame({"st": line, "dir": direction}, index=df.index)
    fub[start], flb[start], direction[start] = ub[start], lb[start], 1
    for i in range(start + 1, n):
        fub[i] = ub[i] if (ub[i] < fub[i - 1] or c[i - 1] > fub[i - 1]) else fub[i - 1]
        flb[i] = lb[i] if (lb[i] > flb[i - 1] or c[i - 1] < flb[i - 1]) else flb[i - 1]
        if direction[i - 1] == 1:
            direction[i] = -1 if c[i] < flb[i] else 1
        else:
            direction[i] = 1 if c[i] > fub[i] else -1
        line[i] = flb[i] if direction[i] == 1 else fub[i]
    direction[:start + 1] = 0
    return pd.DataFrame({"st": line, "dir": direction}, index=df.index)
