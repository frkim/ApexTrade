"""Unit tests for technical indicators."""

import numpy as np
import pandas as pd
import pytest

from app.utils.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_stochastic,
    calculate_williams_r,
    calculate_adx,
    calculate_obv,
    calculate_vwap,
)


@pytest.fixture
def sample_prices() -> pd.Series:
    """Create sample price series."""
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    return pd.Series(prices)


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
    """Create sample OHLCV DataFrame."""
    np.random.seed(42)
    n = 100

    close = 100 + np.cumsum(np.random.randn(n) * 2)
    high = close + np.abs(np.random.randn(n) * 1)
    low = close - np.abs(np.random.randn(n) * 1)
    open_price = close + np.random.randn(n) * 0.5
    volume = 1000 + np.random.randint(0, 500, n)

    return pd.DataFrame({
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


class TestSMA:
    """Test cases for Simple Moving Average."""

    def test_sma_basic(self, sample_prices: pd.Series):
        """Test basic SMA calculation."""
        sma = calculate_sma(sample_prices, period=20)
        assert len(sma) == len(sample_prices)
        assert pd.isna(sma.iloc[0])
        assert not pd.isna(sma.iloc[20])

    def test_sma_different_periods(self, sample_prices: pd.Series):
        """Test SMA with different periods."""
        sma_5 = calculate_sma(sample_prices, period=5)
        sma_20 = calculate_sma(sample_prices, period=20)

        assert sma_5.notna().sum() > sma_20.notna().sum()

    def test_sma_values(self):
        """Test SMA calculation accuracy."""
        prices = pd.Series([10, 20, 30, 40, 50])
        sma = calculate_sma(prices, period=3)

        assert sma.iloc[2] == 20.0
        assert sma.iloc[3] == 30.0
        assert sma.iloc[4] == 40.0


class TestEMA:
    """Test cases for Exponential Moving Average."""

    def test_ema_basic(self, sample_prices: pd.Series):
        """Test basic EMA calculation."""
        ema = calculate_ema(sample_prices, period=20)
        assert len(ema) == len(sample_prices)
        assert not pd.isna(ema.iloc[-1])

    def test_ema_more_reactive(self, sample_prices: pd.Series):
        """Test that EMA is more reactive to recent prices than SMA."""
        sma = calculate_sma(sample_prices, period=20)
        ema = calculate_ema(sample_prices, period=20)

        last_price = sample_prices.iloc[-1]
        if last_price > sample_prices.mean():
            assert ema.iloc[-1] >= sma.iloc[-1] or abs(ema.iloc[-1] - sma.iloc[-1]) < 5


class TestRSI:
    """Test cases for Relative Strength Index."""

    def test_rsi_basic(self, sample_prices: pd.Series):
        """Test basic RSI calculation."""
        rsi = calculate_rsi(sample_prices, period=14)
        assert len(rsi) == len(sample_prices)

    def test_rsi_range(self, sample_prices: pd.Series):
        """Test RSI is bounded between 0 and 100."""
        rsi = calculate_rsi(sample_prices, period=14)
        valid_rsi = rsi.dropna()

        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_rsi_trending_up(self):
        """Test RSI for upward trending prices."""
        prices = pd.Series([i * 1.0 for i in range(1, 51)])
        rsi = calculate_rsi(prices, period=14)

        assert rsi.iloc[-1] > 50

    def test_rsi_trending_down(self):
        """Test RSI for downward trending prices."""
        prices = pd.Series([50.0 - i for i in range(50)])
        rsi = calculate_rsi(prices, period=14)

        assert rsi.iloc[-1] < 50


class TestMACD:
    """Test cases for MACD."""

    def test_macd_basic(self, sample_prices: pd.Series):
        """Test basic MACD calculation."""
        result = calculate_macd(sample_prices)

        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result

    def test_macd_lengths(self, sample_prices: pd.Series):
        """Test MACD output lengths match input."""
        result = calculate_macd(sample_prices)

        assert len(result["macd"]) == len(sample_prices)
        assert len(result["signal"]) == len(sample_prices)
        assert len(result["histogram"]) == len(sample_prices)

    def test_macd_histogram(self, sample_prices: pd.Series):
        """Test MACD histogram equals MACD minus signal."""
        result = calculate_macd(sample_prices)

        diff = result["macd"] - result["signal"]
        pd.testing.assert_series_equal(
            result["histogram"],
            diff,
            check_names=False,
        )


class TestBollingerBands:
    """Test cases for Bollinger Bands."""

    def test_bollinger_basic(self, sample_prices: pd.Series):
        """Test basic Bollinger Bands calculation."""
        result = calculate_bollinger_bands(sample_prices)

        assert "upper" in result
        assert "middle" in result
        assert "lower" in result

    def test_bollinger_ordering(self, sample_prices: pd.Series):
        """Test Bollinger Bands ordering (upper > middle > lower)."""
        result = calculate_bollinger_bands(sample_prices)

        valid_idx = result["upper"].notna()
        assert (result["upper"][valid_idx] >= result["middle"][valid_idx]).all()
        assert (result["middle"][valid_idx] >= result["lower"][valid_idx]).all()

    def test_bollinger_std_dev(self, sample_prices: pd.Series):
        """Test Bollinger Bands with different standard deviations."""
        bb_2 = calculate_bollinger_bands(sample_prices, std_dev=2.0)
        bb_3 = calculate_bollinger_bands(sample_prices, std_dev=3.0)

        valid_idx = bb_2["upper"].notna()
        width_2 = bb_2["upper"][valid_idx] - bb_2["lower"][valid_idx]
        width_3 = bb_3["upper"][valid_idx] - bb_3["lower"][valid_idx]

        assert (width_3 > width_2).all()


class TestATR:
    """Test cases for Average True Range."""

    def test_atr_basic(self, sample_ohlcv: pd.DataFrame):
        """Test basic ATR calculation."""
        atr = calculate_atr(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )
        assert len(atr) == len(sample_ohlcv)

    def test_atr_positive(self, sample_ohlcv: pd.DataFrame):
        """Test ATR is always positive."""
        atr = calculate_atr(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )
        valid_atr = atr.dropna()
        assert (valid_atr >= 0).all()


class TestStochastic:
    """Test cases for Stochastic Oscillator."""

    def test_stochastic_basic(self, sample_ohlcv: pd.DataFrame):
        """Test basic Stochastic calculation."""
        result = calculate_stochastic(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )

        assert "k" in result
        assert "d" in result

    def test_stochastic_range(self, sample_ohlcv: pd.DataFrame):
        """Test Stochastic is bounded between 0 and 100."""
        result = calculate_stochastic(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )

        valid_k = result["k"].dropna()
        assert (valid_k >= 0).all()
        assert (valid_k <= 100).all()


class TestWilliamsR:
    """Test cases for Williams %R."""

    def test_williams_r_basic(self, sample_ohlcv: pd.DataFrame):
        """Test basic Williams %R calculation."""
        wr = calculate_williams_r(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )
        assert len(wr) == len(sample_ohlcv)

    def test_williams_r_range(self, sample_ohlcv: pd.DataFrame):
        """Test Williams %R is bounded between -100 and 0."""
        wr = calculate_williams_r(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )

        valid_wr = wr.dropna()
        assert (valid_wr >= -100).all()
        assert (valid_wr <= 0).all()


class TestADX:
    """Test cases for Average Directional Index."""

    def test_adx_basic(self, sample_ohlcv: pd.DataFrame):
        """Test basic ADX calculation."""
        result = calculate_adx(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
        )

        assert "adx" in result
        assert "plus_di" in result
        assert "minus_di" in result


class TestOBV:
    """Test cases for On-Balance Volume."""

    def test_obv_basic(self, sample_ohlcv: pd.DataFrame):
        """Test basic OBV calculation."""
        obv = calculate_obv(sample_ohlcv["close"], sample_ohlcv["volume"])
        assert len(obv) == len(sample_ohlcv)


class TestVWAP:
    """Test cases for Volume Weighted Average Price."""

    def test_vwap_basic(self, sample_ohlcv: pd.DataFrame):
        """Test basic VWAP calculation."""
        vwap = calculate_vwap(
            sample_ohlcv["high"],
            sample_ohlcv["low"],
            sample_ohlcv["close"],
            sample_ohlcv["volume"],
        )
        assert len(vwap) == len(sample_ohlcv)
        assert not pd.isna(vwap.iloc[-1])
