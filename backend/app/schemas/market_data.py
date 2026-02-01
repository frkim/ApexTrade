"""Market data schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OHLCVBar(BaseModel):
    """Single OHLCV bar."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class OHLCVResponse(BaseModel):
    """OHLCV response schema."""

    symbol: str
    exchange: str
    timeframe: str
    data: list[OHLCVBar]


class SymbolInfo(BaseModel):
    """Symbol information."""

    symbol: str
    base: str
    quote: str
    active: bool = True
    min_quantity: Decimal | None = None
    max_quantity: Decimal | None = None
    price_precision: int | None = None
    quantity_precision: int | None = None


class SymbolResponse(BaseModel):
    """Symbol response schema."""

    symbol: str
    base: str
    quote: str
    exchange: str
    active: bool = True


class TickerResponse(BaseModel):
    """Ticker response schema."""

    symbol: str
    bid: Decimal | None = None
    ask: Decimal | None = None
    last: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    volume: Decimal | None = None
    timestamp: datetime | None = None


class OrderBookLevel(BaseModel):
    """Order book level."""

    price: Decimal
    quantity: Decimal


class OrderBookResponse(BaseModel):
    """Order book response schema."""

    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: datetime | None = None
