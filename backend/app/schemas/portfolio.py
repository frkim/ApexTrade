"""Portfolio schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PositionBase(BaseModel):
    """Base position schema."""

    symbol: str
    quantity: Decimal
    average_entry_price: Decimal
    current_price: Decimal | None = None
    side: str = "long"


class PositionCreate(PositionBase):
    """Position creation schema."""

    pass


class PositionResponse(PositionBase):
    """Position response schema."""

    id: UUID
    portfolio_id: UUID
    current_price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioBase(BaseModel):
    """Base portfolio schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    initial_capital: Decimal = Field(default=Decimal("10000"), ge=0)
    is_paper: bool = True
    exchange: str | None = None


class PortfolioCreate(PortfolioBase):
    """Portfolio creation schema."""

    pass


class PortfolioUpdate(BaseModel):
    """Portfolio update schema."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    is_paper: bool | None = None
    exchange: str | None = None


class PortfolioResponse(PortfolioBase):
    """Portfolio response schema."""

    id: UUID
    user_id: UUID
    cash_balance: Decimal
    created_at: datetime
    updated_at: datetime
    positions: list[PositionResponse] = []

    model_config = {"from_attributes": True}
