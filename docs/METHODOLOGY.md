# Methodology

## Indicators
- **ATR (Wilder):** true range smoothed with α = 1/n.
- **SuperTrend:** bands = (H+L)/2 ± m·ATR. The upper band can only fall and the lower only rise while price stays inside, forming a trailing stop. Direction flips when the close crosses the active band.
- **DEMA:** 2·EMA − EMA(EMA). Less lag than an EMA of equal length (tested).

## Avoiding look-ahead
1. A weekly bar is complete only on Friday's close, so its direction is applied from the following week (`shift(1)` before mapping to daily). Tested by altering the final week and confirming earlier filter values don't change.
2. A position decided at day *t*'s close earns day *t+1*'s return onward. Tested with a single-bar jump that the strategy must not capture.

## Costs
Turnover (|Δposition|) × cost per side, deducted on the day of each change.

## Metrics
CAGR, max drawdown (both vs buy-and-hold), annualised Sharpe on daily returns (rf = 0), exposure, trade count, win rate and average trade (compounded over each holding spell).

## Caveats
- Single-instrument results on three names don't establish an edge.
- Tuning parameters per instrument will inflate backtest returns; validate any tuned set out-of-sample (walk-forward).
- Yahoo prices are adjusted; exits on real charts may differ slightly.
