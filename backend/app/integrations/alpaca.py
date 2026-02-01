"""Alpaca exchange implementation."""

import logging
from datetime import datetime
from typing import Any

from app.config import settings
from app.integrations.base import BaseExchange

logger = logging.getLogger(__name__)


class AlpacaExchange(BaseExchange):
    """Alpaca trading API implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        paper: bool = True,
    ) -> None:
        super().__init__(
            api_key=api_key or settings.ALPACA_API_KEY,
            api_secret=api_secret or settings.ALPACA_API_SECRET,
        )
        self.paper = paper
        self.base_url = settings.ALPACA_BASE_URL if paper else "https://api.alpaca.markets"
        self._trading_client = None
        self._data_client = None

    @property
    def name(self) -> str:
        return "alpaca"

    def _get_trading_client(self) -> Any:
        """Get or create trading client."""
        if self._trading_client is None:
            try:
                from alpaca.trading.client import TradingClient
                self._trading_client = TradingClient(
                    api_key=self.api_key,
                    secret_key=self.api_secret,
                    paper=self.paper,
                )
            except ImportError:
                logger.warning("alpaca-py not installed, using mock client")
                self._trading_client = None
        return self._trading_client

    def _get_data_client(self) -> Any:
        """Get or create data client."""
        if self._data_client is None:
            try:
                from alpaca.data.historical import StockHistoricalDataClient
                self._data_client = StockHistoricalDataClient(
                    api_key=self.api_key,
                    secret_key=self.api_secret,
                )
            except ImportError:
                logger.warning("alpaca-py not installed, using mock client")
                self._data_client = None
        return self._data_client

    async def get_balance(self, currency: str | None = None) -> dict[str, Any]:
        """Get account balance."""
        client = self._get_trading_client()
        if not client:
            return {"error": "Alpaca client not configured"}

        try:
            account = client.get_account()
            return {
                "currency": "USD",
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "portfolio_value": float(account.portfolio_value),
                "equity": float(account.equity),
            }
        except Exception as e:
            logger.error(f"Error fetching Alpaca balance: {e}")
            raise

    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        """Get current ticker for a symbol."""
        client = self._get_data_client()
        if not client:
            return {"error": "Alpaca data client not configured"}

        try:
            from alpaca.data.requests import StockLatestQuoteRequest
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = client.get_stock_latest_quote(request)

            if symbol in quote:
                q = quote[symbol]
                return {
                    "symbol": symbol,
                    "bid": float(q.bid_price),
                    "ask": float(q.ask_price),
                    "last": float(q.ask_price),
                    "timestamp": q.timestamp,
                }

            return {"symbol": symbol, "error": "Quote not found"}
        except Exception as e:
            logger.error(f"Error fetching Alpaca ticker: {e}")
            raise

    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        """Get order book for a symbol."""
        return {
            "symbol": symbol,
            "bids": [],
            "asks": [],
            "note": "Order book not available for Alpaca",
        }

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        since: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get OHLCV candlestick data."""
        client = self._get_data_client()
        if not client:
            return []

        try:
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame

            timeframe_map = {
                "1m": TimeFrame.Minute,
                "5m": TimeFrame.Minute,
                "15m": TimeFrame.Minute,
                "1h": TimeFrame.Hour,
                "1d": TimeFrame.Day,
            }

            tf = timeframe_map.get(timeframe, TimeFrame.Hour)

            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                limit=limit,
            )

            bars = client.get_stock_bars(request)

            if symbol in bars:
                return [
                    {
                        "timestamp": bar.timestamp,
                        "open": float(bar.open),
                        "high": float(bar.high),
                        "low": float(bar.low),
                        "close": float(bar.close),
                        "volume": float(bar.volume),
                    }
                    for bar in bars[symbol]
                ]

            return []
        except Exception as e:
            logger.error(f"Error fetching Alpaca OHLCV: {e}")
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
        client = self._get_trading_client()
        if not client:
            return {"error": "Alpaca trading client not configured"}

        try:
            from alpaca.trading.enums import OrderSide, TimeInForce
            from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest

            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL

            if order_type.lower() == "market":
                request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=order_side,
                    time_in_force=TimeInForce.DAY,
                )
            elif order_type.lower() == "limit":
                if price is None:
                    raise ValueError("Price required for limit orders")
                request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=order_side,
                    time_in_force=TimeInForce.DAY,
                    limit_price=price,
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")

            order = client.submit_order(request)

            logger.info(f"Alpaca order created: {order.id}")
            return {
                "order_id": str(order.id),
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price,
                "status": str(order.status),
                "timestamp": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Error creating Alpaca order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        """Cancel an order."""
        client = self._get_trading_client()
        if not client:
            return {"error": "Alpaca trading client not configured"}

        try:
            client.cancel_order_by_id(order_id)
            logger.info(f"Alpaca order cancelled: {order_id}")
            return {
                "order_id": order_id,
                "status": "cancelled",
            }
        except Exception as e:
            logger.error(f"Error cancelling Alpaca order: {e}")
            raise

    async def get_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        """Get order details."""
        client = self._get_trading_client()
        if not client:
            return {"error": "Alpaca trading client not configured"}

        try:
            order = client.get_order_by_id(order_id)
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "side": str(order.side),
                "type": str(order.type),
                "quantity": float(order.qty) if order.qty else None,
                "price": float(order.limit_price) if order.limit_price else None,
                "filled": float(order.filled_qty) if order.filled_qty else None,
                "status": str(order.status),
            }
        except Exception as e:
            logger.error(f"Error fetching Alpaca order: {e}")
            raise

    async def get_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get all open orders."""
        client = self._get_trading_client()
        if not client:
            return []

        try:
            from alpaca.trading.enums import QueryOrderStatus
            from alpaca.trading.requests import GetOrdersRequest

            request = GetOrdersRequest(status=QueryOrderStatus.OPEN)
            orders = client.get_orders(request)

            result = []
            for o in orders:
                if symbol is None or o.symbol == symbol:
                    result.append({
                        "order_id": str(o.id),
                        "symbol": o.symbol,
                        "side": str(o.side),
                        "type": str(o.type),
                        "quantity": float(o.qty) if o.qty else None,
                        "status": str(o.status),
                    })

            return result
        except Exception as e:
            logger.error(f"Error fetching Alpaca open orders: {e}")
            return []

    async def get_positions(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get open positions."""
        client = self._get_trading_client()
        if not client:
            return []

        try:
            positions = client.get_all_positions()

            result = []
            for p in positions:
                if symbol is None or p.symbol == symbol:
                    result.append({
                        "symbol": p.symbol,
                        "side": "long" if float(p.qty) > 0 else "short",
                        "quantity": abs(float(p.qty)),
                        "entry_price": float(p.avg_entry_price),
                        "current_price": float(p.current_price),
                        "unrealized_pnl": float(p.unrealized_pl),
                        "unrealized_pnl_percent": float(p.unrealized_plpc) * 100,
                    })

            return result
        except Exception as e:
            logger.error(f"Error fetching Alpaca positions: {e}")
            return []

    async def close(self) -> None:
        """Close exchange connection."""
        self._trading_client = None
        self._data_client = None
