"""Binance exchange implementation using CCXT."""

import logging
from datetime import datetime
from typing import Any

import ccxt.async_support as ccxt

from app.config import settings
from app.integrations.base import BaseExchange

logger = logging.getLogger(__name__)


class BinanceExchange(BaseExchange):
    """Binance exchange implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        testnet: bool = False,
    ) -> None:
        super().__init__(
            api_key=api_key or settings.BINANCE_API_KEY,
            api_secret=api_secret or settings.BINANCE_API_SECRET,
        )
        self.testnet = testnet
        self._client: ccxt.binance | None = None

    @property
    def name(self) -> str:
        return "binance"

    @property
    def client(self) -> ccxt.binance:
        """Get or create CCXT client."""
        if self._client is None:
            config: dict[str, Any] = {
                "enableRateLimit": True,
            }

            if self.api_key and self.api_secret:
                config["apiKey"] = self.api_key
                config["secret"] = self.api_secret

            if self.testnet:
                config["sandbox"] = True

            self._client = ccxt.binance(config)

        return self._client

    async def get_balance(self, currency: str | None = None) -> dict[str, Any]:
        """Get account balance."""
        try:
            balance = await self.client.fetch_balance()

            if currency:
                return {
                    "currency": currency,
                    "free": balance.get(currency, {}).get("free", 0),
                    "used": balance.get(currency, {}).get("used", 0),
                    "total": balance.get(currency, {}).get("total", 0),
                }

            return {
                "total": balance.get("total", {}),
                "free": balance.get("free", {}),
                "used": balance.get("used", {}),
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise

    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        """Get current ticker for a symbol."""
        try:
            ticker = await self.client.fetch_ticker(symbol)
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

    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        """Get order book for a symbol."""
        try:
            orderbook = await self.client.fetch_order_book(symbol, limit)
            return {
                "symbol": symbol,
                "bids": orderbook.get("bids", []),
                "asks": orderbook.get("asks", []),
                "timestamp": datetime.fromtimestamp(orderbook["timestamp"] / 1000) if orderbook.get("timestamp") else None,
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            raise

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        since: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get OHLCV candlestick data."""
        try:
            ohlcv = await self.client.fetch_ohlcv(symbol, timeframe, since, limit)
            return [
                {
                    "timestamp": datetime.fromtimestamp(candle[0] / 1000),
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                }
                for candle in ohlcv
            ]
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            raise

    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
    ) -> dict[str, Any]:
        """Create an order."""
        try:
            if order_type.lower() == "market":
                order = await self.client.create_market_order(symbol, side, quantity)
            elif order_type.lower() == "limit":
                if price is None:
                    raise ValueError("Price required for limit orders")
                order = await self.client.create_limit_order(symbol, side, quantity, price)
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            logger.info(f"Order created: {order['id']}")
            return {
                "order_id": order["id"],
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price or order.get("price"),
                "status": order.get("status"),
                "filled": order.get("filled"),
                "timestamp": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        """Cancel an order."""
        try:
            result = await self.client.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return {
                "order_id": order_id,
                "status": "cancelled",
                "result": result,
            }
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise

    async def get_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        """Get order details."""
        try:
            order = await self.client.fetch_order(order_id, symbol)
            return {
                "order_id": order["id"],
                "symbol": symbol,
                "side": order.get("side"),
                "type": order.get("type"),
                "quantity": order.get("amount"),
                "price": order.get("price"),
                "filled": order.get("filled"),
                "remaining": order.get("remaining"),
                "status": order.get("status"),
                "timestamp": datetime.fromtimestamp(order["timestamp"] / 1000) if order.get("timestamp") else None,
            }
        except Exception as e:
            logger.error(f"Error fetching order: {e}")
            raise

    async def get_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get all open orders."""
        try:
            orders = await self.client.fetch_open_orders(symbol)
            return [
                {
                    "order_id": o["id"],
                    "symbol": o["symbol"],
                    "side": o.get("side"),
                    "type": o.get("type"),
                    "quantity": o.get("amount"),
                    "price": o.get("price"),
                    "filled": o.get("filled"),
                    "status": o.get("status"),
                }
                for o in orders
            ]
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise

    async def get_positions(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get open positions (for futures)."""
        try:
            positions = await self.client.fetch_positions([symbol] if symbol else None)
            return [
                {
                    "symbol": p["symbol"],
                    "side": p.get("side"),
                    "quantity": p.get("contracts"),
                    "entry_price": p.get("entryPrice"),
                    "mark_price": p.get("markPrice"),
                    "unrealized_pnl": p.get("unrealizedPnl"),
                    "leverage": p.get("leverage"),
                }
                for p in positions
                if p.get("contracts") and float(p["contracts"]) != 0
            ]
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def close(self) -> None:
        """Close exchange connection."""
        if self._client:
            await self._client.close()
            self._client = None
