"""supertrend-dema-system: dual-timeframe SuperTrend + DEMA 200 trend-following system with backtest."""
from .indicators import atr_wilder, supertrend, ema, dema
from .signals import SystemParams, resample_weekly, weekly_filter, generate_positions
from .backtest import backtest, performance

__version__ = "1.0.0"
