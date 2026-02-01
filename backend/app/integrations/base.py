"""Base exchange abstract class."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class BaseExchange(ABC):
    """Abstract base class for exchange integrations."""

    def __init__(self, api_key: str | None = None, api_secret: str | None = None) -> None:
        self.api_key = api_key
        self.api_secret = api_secret

    @property
    @abstractmethod
    def name(self) -> str:
        """Exchange name."""
        ...

    @abstractmethod
    async def get_balance(self, currency: str | None = None) -> dict[str, Any]:
        """Get account balance."""
        ...

    @abstractmethod
    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        """Get current ticker for a symbol."""
        ...

    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        """Get order book for a symbol."""
        ...

    @abstractmethod
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        since: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get OHLCV candlestick data."""
        ...

    @abstractmethod
    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
    ) -> dict[str, Any]:
        """Create an order."""
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        """Cancel an order."""
        ...

    @abstractmethod
    async def get_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        """Get order details."""
        ...

    @abstractmethod
    async def get_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get all open orders."""
        ...

    @abstractmethod
    async def get_positions(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get open positions."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close exchange connection."""
        ...
