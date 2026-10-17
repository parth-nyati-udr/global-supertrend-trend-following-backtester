import numpy as np
import pandas as pd
import pytest

from st_system import (SystemParams, backtest, dema, ema, generate_positions, performance,
                       resample_weekly, supertrend, weekly_filter)

IDX = pd.bdate_range("2018-01-01", periods=1500)


def ohlc(close):
    c = pd.Series(np.asarray(close, float), index=IDX[:len(close)])
    return pd.DataFrame({"Open": c.shift(1).fillna(c), "High": c * 1.01, "Low": c * 0.99, "Close": c, "Volume": 1e6})


def wave(n=1500):
    """Long up-leg, long down-leg, recovery: gives the system real trades."""
    t = np.arange(n)
    return 100 * np.exp(0.5 * np.sin(t / 160) + 0.0002 * t) * (1 + 0.005 * np.sin(t * 1.3))


def test_supertrend_direction_follows_trend():
    up = supertrend(ohlc(np.linspace(100, 200, 300)))
    down = supertrend(ohlc(np.linspace(200, 100, 300)))
    assert (up["dir"].iloc[50:] == 1).all()
    assert (down["dir"].iloc[50:] == -1).all()


def test_supertrend_line_trails_below_price_in_uptrend():
    df = ohlc(np.linspace(100, 200, 300))
    st = supertrend(df)
    assert (st["st"].iloc[50:] < df["Close"].iloc[50:]).all()


def test_dema_lags_less_than_ema():
    s = pd.Series(np.linspace(100, 200, 600))
    assert abs(s.iloc[-1] - dema(s, 200).iloc[-1]) < abs(s.iloc[-1] - ema(s, 200).iloc[-1])


def test_weekly_resample():
    wk = resample_weekly(ohlc(np.arange(1, 11)))
    assert wk.index[0].dayofweek == 4 and wk["Close"].iloc[0] == 5


def test_weekly_filter_has_no_lookahead():
    """Changing prices in the final week must not change filter values before it."""
    base = ohlc(wave())
    tweaked = base.copy()
    tweaked.iloc[-5:, tweaked.columns.get_loc("Close")] *= 0.5
    a, b = weekly_filter(base, 10, 3), weekly_filter(tweaked, 10, 3)
    assert a.iloc[:-5].equals(b.iloc[:-5])


def test_positions_are_stateful_and_binary():
    out = generate_positions(ohlc(wave()))
    assert set(out["position"].unique()) <= {0, 1}
    assert out["entry"].sum() >= 1 and abs(out["entry"].sum() - out["exit"].sum()) <= 1
    held = out[out["position"] == 1]
    assert (held["Close"] > held["dema"]).all() and (held["wk_dir"] == 1).all()


def test_no_position_before_dema_warmup():
    out = generate_positions(ohlc(wave()))
    assert out["position"].iloc[:199].sum() == 0


def test_always_long_equals_buy_and_hold_without_costs():
    f = ohlc(wave()); f["position"] = 1
    bt = backtest(f, cost_bps=0)
    # signal from day 0's close is held from day 1, so every return is captured
    assert bt["equity"].iloc[-1] == pytest.approx(bt["bh_equity"].iloc[-1])


def test_costs_reduce_returns():
    out = generate_positions(ohlc(wave()))
    assert backtest(out, 50)["equity"].iloc[-1] < backtest(out, 0)["equity"].iloc[-1]


def test_signal_not_traded_same_bar():
    f = ohlc(np.r_[np.full(10, 100.0), 200.0, np.full(10, 200.0)])
    f["position"] = 0
    f.iloc[10:, f.columns.get_loc("position")] = 1   # signal on the jump bar
    bt = backtest(f, cost_bps=0)
    assert bt["equity"].iloc[-1] == pytest.approx(1.0)  # jump not captured


def test_performance_metrics():
    out = generate_positions(ohlc(wave()))
    p = performance(backtest(out))
    assert p["trades"] >= 1 and 0 <= p["exposure_%"] <= 100
    assert p["max_dd_%"] <= 0 and p["bh_max_dd_%"] <= 0
    # trend filter should cut the deep drawdown of the down-leg
    assert p["max_dd_%"] > p["bh_max_dd_%"]
