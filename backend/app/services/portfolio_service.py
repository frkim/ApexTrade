"""Portfolio service for portfolio management."""

import logging
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.portfolio import Portfolio, Position
from app.models.user import User

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for managing portfolios."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> Portfolio | None:
        """Get portfolio by ID for a specific user."""
        result = await self.db.execute(
            select(Portfolio)
            .options(selectinload(Portfolio.positions))
            .where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_portfolios(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Portfolio]:
        """List portfolios for a user."""
        result = await self.db.execute(
            select(Portfolio)
            .options(selectinload(Portfolio.positions))
            .where(Portfolio.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Portfolio.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_portfolio(
        self,
        user: User,
        name: str,
        description: str | None = None,
        initial_capital: Decimal = Decimal("10000"),
        is_paper: bool = True,
        exchange: str | None = None,
    ) -> Portfolio:
        """Create a new portfolio."""
        portfolio = Portfolio(
            name=name,
            description=description,
            initial_capital=initial_capital,
            cash_balance=initial_capital,
            is_paper=is_paper,
            exchange=exchange,
            user_id=user.id,
        )
        self.db.add(portfolio)
        await self.db.flush()
        await self.db.refresh(portfolio)

        logger.info(f"Portfolio created: {portfolio.name} by user {user.id}")
        return portfolio

    async def update_portfolio(
        self,
        portfolio: Portfolio,
        **kwargs: Any,
    ) -> Portfolio:
        """Update a portfolio."""
        for field, value in kwargs.items():
            if hasattr(portfolio, field):
                setattr(portfolio, field, value)

        await self.db.flush()
        await self.db.refresh(portfolio)

        logger.info(f"Portfolio updated: {portfolio.name}")
        return portfolio

    async def delete_portfolio(self, portfolio: Portfolio) -> None:
        """Delete a portfolio."""
        await self.db.delete(portfolio)
        logger.info(f"Portfolio deleted: {portfolio.name}")

    async def get_portfolio_value(self, portfolio: Portfolio) -> dict[str, Any]:
        """Calculate total portfolio value and metrics."""
        result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio.id)
        )
        positions = list(result.scalars().all())

        positions_value = sum(p.quantity * p.current_price for p in positions)
        total_value = portfolio.cash_balance + positions_value
        total_pnl = total_value - portfolio.initial_capital
        total_pnl_percent = (
            total_pnl / portfolio.initial_capital * 100 if portfolio.initial_capital > 0 else 0
        )

        return {
            "cash_balance": portfolio.cash_balance,
            "positions_value": positions_value,
            "total_value": total_value,
            "initial_capital": portfolio.initial_capital,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "positions_count": len(positions),
        }

    async def add_position(
        self,
        portfolio: Portfolio,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        side: str = "long",
    ) -> Position:
        """Add a position to the portfolio."""
        result = await self.db.execute(
            select(Position).where(
                Position.portfolio_id == portfolio.id,
                Position.symbol == symbol,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            total_quantity = existing.quantity + quantity
            total_cost = existing.quantity * existing.average_entry_price + quantity * price
            existing.average_entry_price = total_cost / total_quantity
            existing.quantity = total_quantity
            existing.current_price = price
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            position = Position(
                portfolio_id=portfolio.id,
                symbol=symbol,
                quantity=quantity,
                average_entry_price=price,
                current_price=price,
                side=side,
            )
            self.db.add(position)
            await self.db.flush()
            await self.db.refresh(position)

            logger.info(f"Position added: {symbol} to portfolio {portfolio.name}")
            return position

    async def close_position(
        self,
        position: Position,
        exit_price: Decimal,
    ) -> Decimal:
        """Close a position and return P&L."""
        if position.side == "long":
            pnl = (exit_price - position.average_entry_price) * position.quantity
        else:
            pnl = (position.average_entry_price - exit_price) * position.quantity

        result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == position.portfolio_id)
        )
        portfolio = result.scalar_one()
        portfolio.cash_balance += position.quantity * exit_price

        await self.db.delete(position)
        await self.db.flush()

        logger.info(f"Position closed: {position.symbol} with P&L {pnl}")
        return pnl

    async def update_position_prices(
        self,
        portfolio: Portfolio,
        prices: dict[str, Decimal],
    ) -> None:
        """Update current prices for all positions."""
        result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio.id)
        )
        positions = result.scalars().all()

        for position in positions:
            if position.symbol in prices:
                position.current_price = prices[position.symbol]

        await self.db.flush()
