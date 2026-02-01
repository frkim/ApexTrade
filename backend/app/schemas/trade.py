"""Trade schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TradeBase(BaseModel):
    """Base trade schema."""

    symbol: str
    side: str
    order_type: str = "market"
    quantity: Decimal
    price: Decimal


class TradeCreate(TradeBase):
    """Trade creation schema."""

    portfolio_id: UUID
    strategy_id: UUID | None = None


class TradeResponse(TradeBase):
    """Trade response schema."""

    id: UUID
    portfolio_id: UUID
    strategy_id: UUID | None = None
    filled_quantity: Decimal | None = None
    filled_price: Decimal | None = None
    commission: Decimal
    status: str
    exchange_order_id: str | None = None
    pnl: Decimal | None = None
    notes: str | None = None
    executed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
