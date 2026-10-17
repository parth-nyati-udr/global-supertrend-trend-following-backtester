# Scope

## The ask
Codify a discretionary dual-timeframe SuperTrend + DEMA 200 approach into explicit rules, and measure it honestly (costs, no look-ahead, against buy-and-hold) before trusting it with capital.

## In scope
- SuperTrend, DEMA, ATR implemented and tested from definitions.
- Weekly trend filter + daily entries/exits, long-only.
- Single-instrument backtest with transaction costs and standard metrics.

## Out of scope
- Shorting, leverage, position sizing, portfolio-level backtests.
- Parameter optimisation (deliberately excluded to avoid curve-fitting).
- Live order placement.

## Assumptions
- Execution at the next session's close after a signal.
- 15 bps per side approximates brokerage, STT and slippage for liquid NSE names.
- Adjusted daily prices from Yahoo Finance.

## Success criteria
- Tests prove: no look-ahead, correct cost accounting, correct indicator behaviour.
- Results reported side by side with buy-and-hold, including drawdowns.
