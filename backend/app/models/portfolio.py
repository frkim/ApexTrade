"""Portfolio and Position models."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.trade import Trade
    from app.models.user import User


class Portfolio(BaseModel):
    """Portfolio model for tracking trading accounts."""

    __tablename__ = "portfolios"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    initial_capital: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        default=Decimal("10000"),
        nullable=False,
    )
    cash_balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        default=Decimal("10000"),
        nullable=False,
    )
    is_paper: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    exchange: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="portfolios",
    )
    positions: Mapped[list["Position"]] = relationship(
        "Position",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

    @property
    def total_value(self) -> Decimal:
        """Calculate total portfolio value including positions."""
        positions_value = sum(p.quantity * p.current_price for p in self.positions)
        return self.cash_balance + positions_value

    @property
    def total_pnl(self) -> Decimal:
        """Calculate total P&L."""
        return self.total_value - self.initial_capital

    @property
    def total_pnl_percent(self) -> Decimal:
        """Calculate total P&L percentage."""
        if self.initial_capital == 0:
            return Decimal("0")
        return (self.total_pnl / self.initial_capital) * 100

    def __repr__(self) -> str:
        return f"<Portfolio {self.name}>"


class Position(BaseModel):
    """Position model for tracking open positions."""

    __tablename__ = "positions"

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    average_entry_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    current_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )
    side: Mapped[str] = mapped_column(
        String(10),
        default="long",
        nullable=False,
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="positions",
    )

    @property
    def market_value(self) -> Decimal:
        """Calculate current market value."""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> Decimal:
        """Calculate cost basis."""
        return self.quantity * self.average_entry_price

    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized P&L."""
        if self.side == "long":
            return self.market_value - self.cost_basis
        else:
            return self.cost_basis - self.market_value

    @property
    def unrealized_pnl_percent(self) -> Decimal:
        """Calculate unrealized P&L percentage."""
        if self.cost_basis == 0:
            return Decimal("0")
        return (self.unrealized_pnl / self.cost_basis) * 100

    def __repr__(self) -> str:
        return f"<Position {self.symbol} {self.quantity}>"
