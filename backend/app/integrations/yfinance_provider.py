"""Yahoo Finance data provider for stock data."""

import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class YFinanceDataProvider:
    """Yahoo Finance data provider for stock market data."""

    def __init__(self) -> None:
        self._yf = None

    def _get_yfinance(self) -> Any:
        """Get yfinance module."""
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
            except ImportError:
                logger.warning("yfinance not installed")
                self._yf = None
        return self._yf

    async def get_ticker_info(self, symbol: str) -> dict[str, Any]:
        """Get ticker information."""
        yf = self._get_yfinance()
        if not yf:
            return {"error": "yfinance not installed"}

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("shortName") or info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "currency": info.get("currency"),
                "exchange": info.get("exchange"),
                "country": info.get("country"),
            }
        except Exception as e:
            logger.error(f"Error fetching ticker info: {e}")
            raise

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Get current quote for a symbol."""
        yf = self._get_yfinance()
        if not yf:
            return {"error": "yfinance not installed"}

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "bid": info.get("bid"),
                "ask": info.get("ask"),
                "last": info.get("currentPrice") or info.get("regularMarketPrice"),
                "open": info.get("open") or info.get("regularMarketOpen"),
                "high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose"),
            }
        except Exception as e:
            logger.error(f"Error fetching quote: {e}")
            raise

    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        period: str | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical OHLCV data."""
        yf = self._get_yfinance()
        if not yf:
            return pd.DataFrame()

        try:
            ticker = yf.Ticker(symbol)

            if period:
                df = ticker.history(period=period, interval=interval)
            else:
                start = start_date or (datetime.now() - timedelta(days=365))
                end = end_date or datetime.now()
                df = ticker.history(start=start, end=end, interval=interval)

            if df.empty:
                return df

            df.reset_index(inplace=True)
            df.columns = [c.lower() for c in df.columns]

            if "date" in df.columns:
                df.rename(columns={"date": "timestamp"}, inplace=True)
            elif "datetime" in df.columns:
                df.rename(columns={"datetime": "timestamp"}, inplace=True)

            return df[["timestamp", "open", "high", "low", "close", "volume"]]

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 500,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Get OHLCV data as list of dictionaries."""
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1wk",
            "1M": "1mo",
        }

        interval = interval_map.get(timeframe, "1d")

        period_map = {
            "1m": "7d",
            "5m": "60d",
            "15m": "60d",
            "30m": "60d",
            "1h": "730d",
            "4h": "730d",
            "1d": "max",
            "1wk": "max",
            "1mo": "max",
        }

        df = await self.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period_map.get(interval) if not start_date else None,
            interval=interval,
        )

        if df.empty:
            return []

        if len(df) > limit:
            df = df.tail(limit)

        return df.to_dict("records")

    async def search_symbols(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for symbols."""
        yf = self._get_yfinance()
        if not yf:
            return []

        try:
            _ = yf.Tickers(query)  # Validate tickers exist
            results = []

            for symbol in query.split():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    if info.get("symbol"):
                        results.append({
                            "symbol": info.get("symbol"),
                            "name": info.get("shortName") or info.get("longName"),
                            "exchange": info.get("exchange"),
                            "type": info.get("quoteType"),
                        })
                except Exception:
                    pass

                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []

    async def get_dividends(self, symbol: str) -> pd.DataFrame:
        """Get dividend history."""
        yf = self._get_yfinance()
        if not yf:
            return pd.DataFrame()

        try:
            ticker = yf.Ticker(symbol)
            return ticker.dividends.reset_index()
        except Exception as e:
            logger.error(f"Error fetching dividends: {e}")
            return pd.DataFrame()

    async def get_splits(self, symbol: str) -> pd.DataFrame:
        """Get stock split history."""
        yf = self._get_yfinance()
        if not yf:
            return pd.DataFrame()

        try:
            ticker = yf.Ticker(symbol)
            return ticker.splits.reset_index()
        except Exception as e:
            logger.error(f"Error fetching splits: {e}")
            return pd.DataFrame()
