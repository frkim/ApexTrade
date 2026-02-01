"""Backtest schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class BacktestCreate(BaseModel):
    """Backtest creation schema."""

    strategy_id: UUID
    start_date: date
    end_date: date
    initial_capital: Decimal = Field(default=Decimal("10000"), ge=0)
    symbols: list[str] | None = None
    timeframe: str | None = None


class BacktestTradeResponse(BaseModel):
    """Backtest trade response schema."""

    id: UUID
    symbol: str
    side: str
    entry_price: Decimal
    exit_price: Decimal | None = None
    quantity: Decimal
    entry_time: datetime
    exit_time: datetime | None = None
    pnl: Decimal | None = None
    pnl_percent: Decimal | None = None

    model_config = {"from_attributes": True}


class BacktestResponse(BaseModel):
    """Backtest response schema."""

    id: UUID
    strategy_id: UUID
    start_date: date
    end_date: date
    symbols: list[str]
    timeframe: str
    initial_capital: Decimal
    final_capital: Decimal | None = None
    status: str
    error_message: str | None = None
    total_return: Decimal | None = None
    total_trades: int | None = None
    winning_trades: int | None = None
    losing_trades: int | None = None
    win_rate: Decimal | None = None
    max_drawdown: Decimal | None = None
    sharpe_ratio: Decimal | None = None
    profit_factor: Decimal | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class BacktestResult(BaseModel):
    """Backtest result with full details."""

    backtest_id: UUID
    status: str
    initial_capital: Decimal
    final_capital: Decimal | None = None
    total_return: Decimal | None = None
    total_trades: int | None = None
    winning_trades: int | None = None
    losing_trades: int | None = None
    win_rate: Decimal | None = None
    max_drawdown: Decimal | None = None
    sharpe_ratio: Decimal | None = None
    profit_factor: Decimal | None = None
    trades: list[BacktestTradeResponse] = []
    equity_curve: list[dict[str, Any]] = []
