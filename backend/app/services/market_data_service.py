"""Market data service for fetching data from exchanges."""

import logging
from datetime import datetime
from typing import Any

import ccxt.async_support as ccxt

from app.config import settings

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching market data from exchanges."""

    def __init__(self) -> None:
        self._exchanges: dict[str, ccxt.Exchange] = {}

    def _get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        """Get or create exchange instance."""
        if exchange_name not in self._exchanges:
            exchange_class = getattr(ccxt, exchange_name, None)
            if not exchange_class:
                raise ValueError(f"Unknown exchange: {exchange_name}")

            config: dict[str, Any] = {
                "enableRateLimit": True,
            }

            if exchange_name == "binance":
                if settings.BINANCE_API_KEY:
                    config["apiKey"] = settings.BINANCE_API_KEY
                    config["secret"] = settings.BINANCE_API_SECRET

            self._exchanges[exchange_name] = exchange_class(config)

        return self._exchanges[exchange_name]

    async def get_symbols(
        self,
        exchange: str = "binance",
        quote_currency: str | None = None,
        search: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get available trading symbols."""
        try:
            ex = self._get_exchange(exchange)
            await ex.load_markets()

            symbols = []
            for symbol, market in ex.markets.items():
                if quote_currency and market.get("quote") != quote_currency:
                    continue

                if search and search.upper() not in symbol.upper():
                    continue

                symbols.append({
                    "symbol": symbol,
                    "base": market.get("base"),
                    "quote": market.get("quote"),
                    "exchange": exchange,
                    "active": market.get("active", True),
                })

                if len(symbols) >= limit:
                    break

            return symbols

        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []
        finally:
            await self._close_exchange(exchange)

    async def get_ohlcv(
        self,
        symbol: str,
        exchange: str = "binance",
        timeframe: str = "1h",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Get OHLCV candlestick data."""
        try:
            ex = self._get_exchange(exchange)

            since = int(start_date.timestamp() * 1000) if start_date else None

            ohlcv = await ex.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=since,
                limit=limit,
            )

            data = []
            for candle in ohlcv:
                timestamp = datetime.fromtimestamp(candle[0] / 1000)

                if end_date and timestamp > end_date:
                    break

                data.append({
                    "timestamp": timestamp,
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                })

            return data

        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            raise
        finally:
            await self._close_exchange(exchange)

    async def get_ticker(
        self,
        symbol: str,
        exchange: str = "binance",
    ) -> dict[str, Any]:
        """Get current ticker data."""
        try:
            ex = self._get_exchange(exchange)
            ticker = await ex.fetch_ticker(symbol)

            return {
                "symbol": symbol,
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "last": ticker.get("last"),
                "high": ticker.get("high"),
                "low": ticker.get("low"),
                "volume": ticker.get("baseVolume"),
                "timestamp": datetime.fromtimestamp(ticker["timestamp"] / 1000) if ticker.get("timestamp") else None,
            }

        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            raise
        finally:
            await self._close_exchange(exchange)

    async def get_orderbook(
        self,
        symbol: str,
        exchange: str = "binance",
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get order book data."""
        try:
            ex = self._get_exchange(exchange)
            orderbook = await ex.fetch_order_book(symbol, limit)

            return {
                "symbol": symbol,
                "bids": [{"price": b[0], "quantity": b[1]} for b in orderbook.get("bids", [])],
                "asks": [{"price": a[0], "quantity": a[1]} for a in orderbook.get("asks", [])],
                "timestamp": datetime.fromtimestamp(orderbook["timestamp"] / 1000) if orderbook.get("timestamp") else None,
            }

        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            raise
        finally:
            await self._close_exchange(exchange)

    async def get_trades(
        self,
        symbol: str,
        exchange: str = "binance",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get recent trades."""
        try:
            ex = self._get_exchange(exchange)
            trades = await ex.fetch_trades(symbol, limit=limit)

            return [
                {
                    "id": t.get("id"),
                    "timestamp": datetime.fromtimestamp(t["timestamp"] / 1000) if t.get("timestamp") else None,
                    "side": t.get("side"),
                    "price": t.get("price"),
                    "amount": t.get("amount"),
                }
                for t in trades
            ]

        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            raise
        finally:
            await self._close_exchange(exchange)

    async def _close_exchange(self, exchange_name: str) -> None:
        """Close exchange connection."""
        if exchange_name in self._exchanges:
            try:
                await self._exchanges[exchange_name].close()
            except Exception:
                # Silently ignore errors when closing exchange connections
                pass

    async def close_all(self) -> None:
        """Close all exchange connections."""
        for name in list(self._exchanges.keys()):
            await self._close_exchange(name)
        self._exchanges.clear()
