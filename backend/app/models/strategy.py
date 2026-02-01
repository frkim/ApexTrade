"""Strategy model."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.backtest import Backtest
    from app.models.trade import Trade
    from app.models.user import User


class Strategy(BaseModel):
    """Trading strategy model."""

    __tablename__ = "strategies"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    rules: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    entry_rules: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    exit_rules: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON,
        nullable=True,
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
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_paper: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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
        back_populates="strategies",
    )
    backtests: Mapped[list["Backtest"]] = relationship(
        "Backtest",
        back_populates="strategy",
        cascade="all, delete-orphan",
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        back_populates="strategy",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Strategy {self.name}>"
