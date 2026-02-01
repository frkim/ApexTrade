"""Backtest models."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.strategy import Strategy


class Backtest(BaseModel):
    """Backtest run model."""

    __tablename__ = "backtests"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategies.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    symbols: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False,
    )
    timeframe: Mapped[str] = mapped_column(
        String(10),
        default="1h",
        nullable=False,
    )
    initial_capital: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        default=Decimal("10000"),
        nullable=False,
    )
    final_capital: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Performance metrics
    total_return: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    total_trades: Mapped[int | None] = mapped_column(nullable=True)
    winning_trades: Mapped[int | None] = mapped_column(nullable=True)
    losing_trades: Mapped[int | None] = mapped_column(nullable=True)
    win_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    max_drawdown: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    profit_factor: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    equity_curve: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    strategy: Mapped["Strategy"] = relationship(
        "Strategy",
        back_populates="backtests",
    )
    trades: Mapped[list["BacktestTrade"]] = relationship(
        "BacktestTrade",
        back_populates="backtest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Backtest {self.id} ({self.status})>"


class BacktestTrade(BaseModel):
    """Individual trade within a backtest."""

    __tablename__ = "backtest_trades"

    backtest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("backtests.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    side: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    exit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    entry_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    exit_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    pnl: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )
    pnl_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )

    # Relationships
    backtest: Mapped["Backtest"] = relationship(
        "Backtest",
        back_populates="trades",
    )

    def __repr__(self) -> str:
        return f"<BacktestTrade {self.symbol} {self.side}>"
