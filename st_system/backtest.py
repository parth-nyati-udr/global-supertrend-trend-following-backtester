"""Vectorised long-only backtest with costs.

Signal at day t's close -> trade at day t+1's close (position shifted by one
bar), so a signal never earns the return of the bar that produced it.
Costs are charged in basis points per side on every position change.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def backtest(frame: pd.DataFrame, cost_bps: float = 15.0) -> pd.DataFrame:
    """Adds held, strat_ret, bh_ret, equity, bh_equity columns."""
    out = frame.copy()
    ret = out["Close"].pct_change().fillna(0)
    held = out["position"].shift(1).fillna(0)
    turnover = held.diff().abs().fillna(held.abs())
    out["held"] = held
    out["strat_ret"] = held * ret - turnover * cost_bps / 1e4
    out["bh_ret"] = ret
    out["equity"] = (1 + out["strat_ret"]).cumprod()
    out["bh_equity"] = (1 + ret).cumprod()
    return out


def _max_dd(eq: pd.Series) -> float:
    return float((eq / eq.cummax() - 1).min())


def _trades(bt: pd.DataFrame) -> list[float]:
    """Per-trade returns from compounding strat_ret over each holding spell."""
    spell = (bt["held"].diff().fillna(bt["held"]) == 1).cumsum().where(bt["held"] == 1)
    return [float((1 + g).prod() - 1) for _, g in bt.loc[spell.notna(), "strat_ret"].groupby(spell.dropna())]


def performance(bt: pd.DataFrame, periods_per_year: int = 252) -> dict:
    yrs = len(bt) / periods_per_year
    r = bt["strat_ret"]
    trades = _trades(bt)
    sd = r.std()
    return {
        "cagr_%": round(float(bt["equity"].iloc[-1] ** (1 / yrs) - 1) * 100, 2),
        "bh_cagr_%": round(float(bt["bh_equity"].iloc[-1] ** (1 / yrs) - 1) * 100, 2),
        "max_dd_%": round(_max_dd(bt["equity"]) * 100, 2),
        "bh_max_dd_%": round(_max_dd(bt["bh_equity"]) * 100, 2),
        "sharpe": round(float(r.mean() / sd * np.sqrt(periods_per_year)), 2) if sd > 0 else None,
        "exposure_%": round(float(bt["held"].mean()) * 100, 1),
        "trades": len(trades),
        "win_rate_%": round(float(np.mean([t > 0 for t in trades])) * 100, 1) if trades else None,
        "avg_trade_%": round(float(np.mean(trades)) * 100, 2) if trades else None,
    }


def run(symbol: str, start: str = "2015-01-01", **kw) -> tuple[pd.DataFrame, dict]:
    """Download (yfinance), generate signals, backtest. Needs network."""
    import yfinance as yf

    from .signals import SystemParams, generate_positions
    df = yf.download(symbol, start=start, auto_adjust=True, progress=False, multi_level_index=False)
    bt = backtest(generate_positions(df, SystemParams(**kw)))
    return bt, performance(bt)
