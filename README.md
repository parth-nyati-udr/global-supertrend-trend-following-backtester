# supertrend-dema-system

A rules-based, long-only trend-following system for NSE instruments: a **weekly SuperTrend** decides whether to be in the market, a **daily SuperTrend + DEMA(200)** decides when. Indicators are implemented from first principles, and the backtest is cost-aware and free of look-ahead.

## Rules
| | Condition |
|---|---|
| Entry | Weekly SuperTrend up **and** daily SuperTrend up **and** close > DEMA(200) |
| Exit | Daily SuperTrend flips down **or** close < DEMA(200) **or** weekly turns down |

Defaults: SuperTrend (10, 3.0) on both timeframes, DEMA 200, 15 bps per side. All in `SystemParams`.

## Results (2015 → 15 Oct 2026, defaults, 15 bps/side)
| Instrument | CAGR | Buy & hold | Max DD | B&H max DD | Exposure | Trades | Win rate |
|---|---|---|---|---|---|---|---|
| Nifty 50 | 4.1% | 9.1% | −15.0% | −38.4% | 35% | 38 | 45% |
| PHARMABEES | 6.8% | 12.6% | −10.9% | −21.1% | 37% | 15 | 33% |
| BAJAJ-AUTO | 6.7% | 16.3% | −27.9% | −42.3% | 36% | 36 | 39% |

**Reading these honestly:** at default parameters the system roughly halves drawdowns while being invested about a third of the time, but it gives up a lot of return versus buy-and-hold. It's a risk-reduction overlay, not an alpha source, unless parameters are tuned (and tuning invites overfitting; see METHODOLOGY).

## Install & run
```bash
pip install -e ".[dev]"
python -c "from st_system.backtest import run; print(run('^NSEI')[1])"
```

## Layout
```
st_system/
  indicators.py  EMA, DEMA, Wilder ATR, SuperTrend
  signals.py     weekly resample, look-ahead-free filter, stateful positions
  backtest.py    next-bar execution, costs, metrics, per-trade stats
tests/           11 offline tests
docs/            SCOPE.md, METHODOLOGY.md, TEST_PLAN.md
```

## License
MIT. Educational research, not investment advice.
