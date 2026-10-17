# Test plan

Run `pytest -q`. All offline on synthetic paths.

| Test | Scenario | Expected |
|---|---|---|
| `test_supertrend_direction_follows_trend` | Linear up / down | +1 / −1 after warm-up |
| `test_supertrend_line_trails_below_price_in_uptrend` | Linear up | Line below price |
| `test_dema_lags_less_than_ema` | Linear ramp | DEMA closer to price than EMA |
| `test_weekly_resample` | 10 business days | Friday-ended bars, correct close |
| `test_weekly_filter_has_no_lookahead` | Change last week's prices | Earlier filter values unchanged |
| `test_positions_are_stateful_and_binary` | Wave path | 0/1 only; held days satisfy all rules |
| `test_no_position_before_dema_warmup` | First 199 bars | Flat |
| `test_always_long_equals_buy_and_hold_without_costs` | Position always 1, 0 bps | Equity = buy-and-hold |
| `test_costs_reduce_returns` | 50 vs 0 bps | Lower equity with costs |
| `test_signal_not_traded_same_bar` | Signal on a jump bar | Jump not captured |
| `test_performance_metrics` | Wave with deep down-leg | Valid metrics; drawdown smaller than buy-and-hold |

## Manual checks
Compare SuperTrend flips on one instrument with TradingView (same period/multiplier); dates should match.
