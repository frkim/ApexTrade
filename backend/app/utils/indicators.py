"""Technical indicator calculations."""

import numpy as np
import pandas as pd


def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
    """Calculate Simple Moving Average.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average

    Returns:
        Series containing SMA values
    """
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int = 20) -> pd.Series:
    """Calculate Exponential Moving Average.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average

    Returns:
        Series containing EMA values
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for RSI calculation

    Returns:
        Series containing RSI values (0-100)
    """
    delta = data.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    for i in range(period, len(data)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.replace([np.inf, -np.inf], np.nan)
    rsi = rsi.fillna(50)

    return rsi


def calculate_macd(
    data: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> dict[str, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence).

    Args:
        data: Price series (typically close prices)
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line EMA period

    Returns:
        Dictionary containing 'macd', 'signal', and 'histogram' series
    """
    fast_ema = calculate_ema(data, fast_period)
    slow_ema = calculate_ema(data, slow_period)

    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
    }


def calculate_bollinger_bands(
    data: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> dict[str, pd.Series]:
    """Calculate Bollinger Bands.

    Args:
        data: Price series (typically close prices)
        period: Number of periods for the moving average
        std_dev: Number of standard deviations for the bands

    Returns:
        Dictionary containing 'upper', 'middle', and 'lower' band series
    """
    middle = calculate_sma(data, period)
    std = data.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
    }


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Calculate Average True Range.

    Args:
        high: High prices series
        low: Low prices series
        close: Close prices series
        period: Number of periods for ATR calculation

    Returns:
        Series containing ATR values
    """
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(window=period).mean()

    return atr


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> dict[str, pd.Series]:
    """Calculate Stochastic Oscillator.

    Args:
        high: High prices series
        low: Low prices series
        close: Close prices series
        k_period: Period for %K calculation
        d_period: Period for %D (signal line) calculation

    Returns:
        Dictionary containing 'k' and 'd' series
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()

    return {
        "k": k,
        "d": d,
    }


def calculate_williams_r(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Calculate Williams %R.

    Args:
        high: High prices series
        low: Low prices series
        close: Close prices series
        period: Lookback period

    Returns:
        Series containing Williams %R values (-100 to 0)
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()

    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)

    return williams_r


def calculate_adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> dict[str, pd.Series]:
    """Calculate Average Directional Index.

    Args:
        high: High prices series
        low: Low prices series
        close: Close prices series
        period: Period for ADX calculation

    Returns:
        Dictionary containing 'adx', 'plus_di', and 'minus_di' series
    """
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    atr = calculate_atr(high, low, close, period)

    plus_di = 100 * calculate_ema(plus_dm, period) / atr
    minus_di = 100 * calculate_ema(minus_dm, period) / atr

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = calculate_ema(dx, period)

    return {
        "adx": adx,
        "plus_di": plus_di,
        "minus_di": minus_di,
    }


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Calculate On-Balance Volume.

    Args:
        close: Close prices series
        volume: Volume series

    Returns:
        Series containing OBV values
    """
    direction = np.sign(close.diff())
    direction.iloc[0] = 0

    obv = (volume * direction).cumsum()

    return obv


def calculate_vwap(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
) -> pd.Series:
    """Calculate Volume Weighted Average Price.

    Args:
        high: High prices series
        low: Low prices series
        close: Close prices series
        volume: Volume series

    Returns:
        Series containing VWAP values
    """
    typical_price = (high + low + close) / 3
    vwap = (typical_price * volume).cumsum() / volume.cumsum()

    return vwap
